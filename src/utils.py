import json
import shutil
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile



def default_save_path_root(home: Path | None = None, platform: str | None = None) -> Path:
    home = home or Path.home()
    platform = platform or sys.platform

    if platform == "darwin":
        return home / "Library/Application Support/ZAUM Studio/Disco Elysium/SaveGames"

    return home / "AppData/LocalLow/ZAUM Studio/Disco Elysium/SaveGames"


def auto_discover() -> tuple[bool, str]:
    save_path_root = default_save_path_root()
    return save_path_root.is_dir(), str(save_path_root)


def parse_saves(save_path_root: str) -> dict:
    save_paths = Path(save_path_root).expanduser().glob("*.zip")
    return {
        save_path.stem.removesuffix(".ntwtf"): str(save_path)
        for save_path in save_paths
    }


def backup_save(save_path: str) -> str:
    save_path = Path(save_path)
    assert save_path.exists()
    backup_path = save_path.with_name(f"{save_path.name}.bak")
    if not backup_path.exists():
        save_path.rename(backup_path)
    return str(backup_path)


def restore_save(backup_path: str):
    backup_path = Path(backup_path)
    assert backup_path.exists()
    save_path = Path(str(backup_path)[:-4])
    if save_path.exists():
        save_path.unlink()
    backup_path.rename(save_path)


def discover_baks(save_path_root: str) -> dict:
    bak_paths = Path(save_path_root).expanduser().glob("*.bak")
    return {
        bak_path.name.split(".ntwtf", 1)[0]: str(bak_path) for bak_path in bak_paths
    }


def pprint_dict(dict: dict, keys_only: bool = False):
    if keys_only:
        for i, k in enumerate(dict.keys()):
            if k not in ["common_ancestor", "map"]:
                print(f"\t{i}. {k}\n")
    else:
        for k, v in dict.items():
            if k not in ["common_ancestor", "map"]:
                print(f"\t - {k}: {v}\n")


def unzip_save(save_path: str) -> str:
    save_path = Path(save_path)
    assert save_path.is_file()
    tmp_dir = save_path.parent / "tmp"
    tmp_dir.mkdir(exist_ok=True)
    with ZipFile(save_path, "r") as save:
        save.extractall(tmp_dir)
    return str(tmp_dir)


def zip_save(save_path: str, cleanup: bool = True):
    save_path = Path(save_path)
    tmp_dir = save_path.parent / "tmp"
    with ZipFile(save_path, "w", ZIP_DEFLATED) as save:
        for file in tmp_dir.iterdir():
            if file.is_file():
                save.write(file, arcname=file.name)
    if cleanup:
        shutil.rmtree(tmp_dir)


def get_save_state(tmp_dir: str) -> (str, dict):
    save_state_path = next(Path(tmp_dir).glob("*2nd.ntwtf.json"))
    with open(save_state_path, "r") as save:
        return str(save_state_path), json.load(save)


def write_save_state(state: dict, path: str):
    with open(path, "w") as p:
        json.dump(state, p)
