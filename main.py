import argparse

from src.scheduler import Scheduler
from src.utils import setup_logging


def main(state_filepath: str, restore: bool = False):
    scheduler = Scheduler()

    if restore:
        scheduler.restore_state(state_filepath)
    else:
        from setup_jobs import JOBS

        # see EXAMPLE.md file
        for job in JOBS:
            scheduler.schedule(job)
    try:
        scheduler.run()
    except KeyboardInterrupt:
        scheduler.exit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Scheduler", description="Async Python: Sprint № 2"
    )
    parser.add_argument("-r", "--restore", action="store_true", default=False)
    parser.add_argument("-f", "--state-file", default="state.json")
    parser.add_argument("--log-config", default="logging.yml")

    args = parser.parse_args()

    setup_logging(logging_config_path=args.log_config)
    main(restore=args.restore, state_filepath=args.state_file)
