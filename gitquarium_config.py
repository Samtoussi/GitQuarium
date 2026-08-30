import json
import os
from pathlib import Path


APP_NAME = "GitQuarium"


def get_app_data_dir():
    local_app_data = os.getenv("LOCALAPPDATA")

    if local_app_data:
        app_dir = Path(local_app_data) / APP_NAME
    else:
        app_dir = Path.home() / ".gitquarium"

    app_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    return app_dir


def get_config_path():
    return get_app_data_dir() / "config.json"


def config_exists():
    return get_config_path().exists()


def load_config():
    config_path = get_config_path()

    if not config_path.exists():
        return None

    try:
        with open(
            config_path,
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    except (
        json.JSONDecodeError,
        OSError,
    ):
        return None


def save_config(username, token):
    config_path = get_config_path()

    config_data = {
        "github_username": username.strip(),
        "github_token": token.strip(),
    }

    with open(
        config_path,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            config_data,
            file,
            indent=4,
        )

    return config_data


if __name__ == "__main__":
    print(
        "GitQuarium config path:",
        get_config_path(),
    )

    print(
        "Config exists:",
        config_exists(),
    )