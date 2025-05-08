import logging

from dotenv import load_dotenv
from app.watcher import PandaWatcher


def main() -> None:
    """
    Sets up logging and environment, then runs the PANDA watcher.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    load_dotenv()
    watcher = PandaWatcher()
    watcher.run()


if __name__ == "__main__":
    main()