import os

import requests
from dotenv import load_dotenv


load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
}


def get_repositories():
    url = f"https://api.github.com/users/{GITHUB_USERNAME}/repos"

    response = requests.get(
        url,
        headers=HEADERS,
        params={
            "per_page": 100,
            "sort": "updated",
        },
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


def get_commits_for_repo(repo_name):
    url = (
        f"https://api.github.com/repos/"
        f"{GITHUB_USERNAME}/{repo_name}/commits"
    )

    response = requests.get(
        url,
        headers=HEADERS,
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
                    "message": commit["commit"]["message"],
                    "repo": repo_name,
                    "created_at": commit["commit"]["author"]["date"],
                }
            )

    commits.sort(
        key=lambda commit: commit["created_at"],
        reverse=True,
    )

    return commits


if __name__ == "__main__":
    commits = get_recent_commits()

    print(f"\nRecent commits for {GITHUB_USERNAME}:\n")

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

    print(f"\nCommits found: {len(commits)}")