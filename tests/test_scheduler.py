import pathlib

from src.scheduler import Scheduler
from src.jobs import CreateFileJob, ReadFileJob, WriteFileJob
from src.exceptions import TimeLimitExceededException


class TestScheduler:
    def test_restore(self, state_file_path: str):
        """Test scheduler's ability to restore state from a file."""
        scheduler = Scheduler()
        scheduler.restore_state(filepath=state_file_path)

    def test_timeout(self, long_file_path: str):
        """
        Set minimal timeout for a long-running job.
        TimeLimitExceededException should be thrown.
        """
        temp_file_path = "/tmp/tmp1.txt"
        scheduler = Scheduler()
        file_creator_job = ReadFileJob(
            filepath=long_file_path,
            tries=3,
            max_working_time=0.0000000001,
            target=WriteFileJob(
                filepath=temp_file_path
            ),
            depends_on=[
                CreateFileJob(
                    filepath=temp_file_path,
                ),
            ],
        )
        scheduler.schedule(file_creator_job)
        exception = None
        try:
            scheduler.run(atomic=True)
        except Exception as ex:
            exception = ex

        pathlib.Path(temp_file_path).unlink(missing_ok=True)
        assert type(exception) == TimeLimitExceededException
