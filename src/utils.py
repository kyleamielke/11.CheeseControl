import configparser
from pathlib import Path


def get_project_root() -> Path:
    return Path(__file__).parent.parent


def get_config_root() -> Path:
    return Path(Path.joinpath(get_project_root(), 'config').absolute().as_posix())


def get_all_config_files() -> list[Path]:
    files = [f for f in Path(get_config_root()).glob('*.ini')]
    return files


def get_config_file_path(cfg_type: str) -> Path:
    if 'reg' in cfg_type:
        cfg_file = 'reg.ini'

    if 'cc' in cfg_type or 'cheese' in cfg_type:
        cfg_file = 'cc.ini'
    return Path(Path.joinpath(get_config_root(), cfg_file)).relative_to(get_project_root())


def get_config_contents(cfg_file: Path) -> configparser:
    config = configparser.ConfigParser()
    config.read(cfg_file)

    return config


def get_file_name(file_path: Path) -> str:
    return file_path.name
