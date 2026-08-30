import os

import requests
from dotenv import load_dotenv

from gitquarium_config import load_config


load_dotenv()


def load_github_credentials():
    config = load_config()

    if config:
        username = config.get("github_username")
        token = config.get("github_token")

        if username:
            return username, token

    return (
        os.getenv("GITHUB_USERNAME"),
        os.getenv("GITHUB_TOKEN"),
    )


GITHUB_USERNAME, GITHUB_TOKEN = load_github_credentials()


def configure_github(username, token):
    global GITHUB_USERNAME, GITHUB_TOKEN

    GITHUB_USERNAME = username.strip()
    GITHUB_TOKEN = token.strip()


def get_headers():
    headers = {
        "Accept": "application/vnd.github+json",
    }

    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    return headers


def validate_github_connection(username=None, token=None):
    test_username = (
        username.strip()
        if username
        else GITHUB_USERNAME
    )

    test_token = (
        token.strip()
        if token
        else GITHUB_TOKEN
    )

    if not test_username:
        return False, "GitHub username is missing."

    headers = {
        "Accept": "application/vnd.github+json",
    }

    if test_token:
        headers["Authorization"] = f"Bearer {test_token}"

    url = f"https://api.github.com/users/{test_username}"

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=10,
        )

    except requests.RequestException:
        return False, "Could not connect to GitHub."

    if response.status_code == 200:
        return True, response.json()

    if response.status_code == 401:
        return False, "Invalid GitHub token."

    if response.status_code == 404:
        return False, "GitHub user not found."

    return (
        False,
        f"GitHub returned error {response.status_code}.",
    )


def get_repositories():
    if not GITHUB_USERNAME:
        raise ValueError(
            "GitHub username has not been configured."
        )

    url = (
        f"https://api.github.com/users/"
        f"{GITHUB_USERNAME}/repos"
    )

    response = requests.get(
        url,
        headers=get_headers(),
        params={
            "per_page": 100,
            "sort": "updated",
        },
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


def get_commits_for_repo(repo_name):
    if not GITHUB_USERNAME:
        raise ValueError(
            "GitHub username has not been configured."
        )

    url = (
        f"https://api.github.com/repos/"
        f"{GITHUB_USERNAME}/{repo_name}/commits"
    )

    response = requests.get(
        url,
        headers=get_headers(),
        params={
            "author": GITHUB_USERNAME,
            "per_page": 100,
        },
        timeout=10,
    )

    # Empty repositories can return 409
    if response.status_code == 409:
        return []

    response.raise_for_status()

    return response.json()


def get_recent_commits():
    repositories = get_repositories()

    commits = []

    for repo in repositories:
        repo_name = repo["name"]

        repo_commits = get_commits_for_repo(
            repo_name
        )

        for commit in repo_commits:
            commits.append(
                {
                    "sha": commit["sha"],
                    "message": commit[
                        "commit"
                    ]["message"],
                    "repo": repo_name,
                    "created_at": commit[
                        "commit"
                    ]["author"]["date"],
                }
            )

    commits.sort(
        key=lambda commit: commit["created_at"],
        reverse=True,
    )

    return commits


if __name__ == "__main__":
    success, result = (
        validate_github_connection()
    )

    if not success:
        print(
            f"\nGitHub connection failed: "
            f"{result}"
        )

        raise SystemExit(1)

    print(
        f"\nConnected to GitHub as "
        f"{result['login']}."
    )

    commits = get_recent_commits()

    print(
        f"\nRecent commits for "
        f"{GITHUB_USERNAME}:\n"
    )

    for commit in commits:
        short_sha = commit["sha"][:7]

        print(
            short_sha,
            "|",
            commit["repo"],
            "|",
            commit["message"],
            "|",
            commit["created_at"],
        )

    print(
        f"\nCommits found: {len(commits)}"
    )