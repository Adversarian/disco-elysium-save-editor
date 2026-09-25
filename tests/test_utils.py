import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from utils import default_save_path_root, parse_saves, unzip_save, zip_save
from edits import SaveState
from fsm import state_manual_save


class SavePathTests(unittest.TestCase):
    def test_macos_default_save_path(self):
        self.assertEqual(
            default_save_path_root(Path("/Users/player"), "darwin"),
            Path("/Users/player/Library/Application Support/ZAUM Studio/Disco Elysium/SaveGames"),
        )

    def test_parse_and_rewrite_save_with_posix_path(self):
        with tempfile.TemporaryDirectory() as directory:
            save_path = Path(directory) / "quicksave.ntwtf.zip"
            with ZipFile(save_path, "w") as save:
                save.writestr("state2nd.ntwtf.json", "{}")

            self.assertEqual(parse_saves(directory), {"quicksave": str(save_path)})

            tmp_dir = Path(unzip_save(str(save_path)))
            self.assertEqual(tmp_dir, Path(directory) / "tmp")
            self.assertTrue((tmp_dir / "state2nd.ntwtf.json").is_file())

            zip_save(str(save_path))
            self.assertFalse(tmp_dir.exists())

    def test_manual_save_directory_selects_an_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            save_path = Path(directory) / "quicksave.ntwtf.zip"
            with ZipFile(save_path, "w"):
                pass

            with patch("fsm.get_input", side_effect=[directory, 0]):
                self.assertEqual(state_manual_save(), str(save_path))

    def test_save_state_can_commit_multiple_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            save_path = Path(directory) / "quicksave.ntwtf.zip"
            with ZipFile(save_path, "w") as save:
                save.writestr("state2nd.ntwtf.json", '{"playerCharacter": {}}')

            save_state = SaveState(str(save_path))
            save_state.set_resource("Skill Points", 1)
            save_state.commit(cleanup=False)
            save_state.set_resource("Skill Points", 2)
            save_state.commit(cleanup=False)

            self.assertTrue((Path(directory) / "tmp" / "state2nd.ntwtf.json").is_file())
            with ZipFile(save_path) as save:
                self.assertEqual(
                    save.read("state2nd.ntwtf.json"),
                    b'{"playerCharacter": {"SkillPoints": 2}}',
                )
