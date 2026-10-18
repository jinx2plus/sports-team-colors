"""Copy the repository's canonical /data JSON files into built wheels."""

from pathlib import Path
from shutil import copy2
from setuptools import setup
from setuptools.command.build_py import build_py


class BuildWithCatalog(build_py):
    def run(self):
        super().run()
        source = Path(__file__).resolve().parent / "data"
        target = Path(self.build_lib) / "sports_colors" / "data"
        target.mkdir(parents=True, exist_ok=True)
        for league in ("mlb", "nba", "nfl", "epl"):
            copy2(source / f"{league}.json", target / f"{league}.json")


setup(cmdclass={"build_py": BuildWithCatalog})
