from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent


def project_root():
    return _PROJECT_ROOT


def agents_dir():
    return _PROJECT_ROOT / "agents"


def skills_dir():
    return _PROJECT_ROOT / "skills"


def config_path():
    return _PROJECT_ROOT / "config.yaml"


def output_dir():
    return _PROJECT_ROOT / "output"


def videos_dir():
    return _PROJECT_ROOT / "videos"
