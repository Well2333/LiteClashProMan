import argparse
import shutil
from pathlib import Path

from .config import Config

parser = argparse.ArgumentParser(description="run LiteClashProMan")
parser.add_argument(
    "--config", "-c", default="config.yaml", help="Path to the config file"
)
args = parser.parse_args()


def main():
    # check dirs and files
    static_dir = Path(__file__).parent.joinpath("static")
    data_dir = Path("data")
    provider_dir = data_dir.joinpath("provider")
    template_dir = data_dir.joinpath("template")

    for dir in [data_dir, provider_dir, template_dir]:
        if not dir.exists():
            dir.mkdir(0o755, parents=True, exist_ok=True)
        assert dir.is_dir(), f"{dir.as_posix()} should be folder"

    if not any(template_dir.glob("*")):
        shutil.copytree(
            static_dir.joinpath("template"), template_dir, dirs_exist_ok=True
        )

    Config.load(Path(args.config))

    from .main import main as run_main

    run_main()
