import json
import os
import shutil
from glob import glob
from zipfile import ZIP_DEFLATED, ZipFile

DEFAULT_SAVE_PATH_ROOT = (
    rf"C:\Users\{os.getlogin()}\AppData\LocalLow\ZAUM Studio\Disco Elysium\SaveGames"
)


def auto_discover():
    return os.path.exists(DEFAULT_SAVE_PATH_ROOT), DEFAULT_SAVE_PATH_ROOT


def parse_saves(save_path_root):
    save_paths = glob(rf"{save_path_root}\*.zip")
    return {
        save_path.split("\\")[-1].split(".ntwtf")[0]: save_path
        for save_path in save_paths
    }


def backup_save(save_path):
    shutil.copy2(rf"{save_path}", rf"{save_path}.bak")


def restore_save(backup_path):
    if os.path.exists(rf"{backup_path[:-4]}"):
        os.remove(rf"{backup_path[:-4]}")
    os.rename(rf"{backup_path}", rf"{backup_path[:-4]}")


def discover_baks(save_path_root):
    bak_paths = glob(rf"{save_path_root}\*.bak")
    return {
        bak_path.split("\\")[-1].split(".ntwtf")[0]: bak_path for bak_path in bak_paths
    }


def pprint_dict(dict):
    for k, v in dict.items():
        print(f"\t - {k}: {v}\n")


def unzip_save(save_path):
    if os.path.exists(rf"{save_path}"):
        tmp_dir = "\\".join(save_path.split("\\")[:-1]) + r"\tmp"
        os.makedirs(tmp_dir, exist_ok=True)
        with ZipFile(save_path, "r") as save:
            save.extractall(tmp_dir)


def zip_save(save_path, cleanup=True):
    tmp_dir = "\\".join(save_path.split("\\")[:-1]) + r"\tmp"
    with ZipFile(save_path, "w", ZIP_DEFLATED) as save:
        files = glob(rf"{tmp_dir}\*")
        for file in files:
            save.write(file)
    if cleanup:
        shutil.rmtree(tmp_dir)


def get_save_state(tmp_dir):
    save_state_path = glob(rf"{tmp_dir}\*2nd.ntwtf.json")[0]
    with open(save_state_path, "r") as save:
        return json.load(save)


def write_save_state(state, path):
    with open(path, "w") as p:
        json.dump(state, p)
