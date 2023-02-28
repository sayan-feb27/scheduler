import pathlib
from collections.abc import Generator, Coroutine

from src.utils import coroutine
from src.mixins.files import FilesJobMixin
from src.job import Job


class CreateFileJob(FilesJobMixin, Job):
    def underlying(self) -> Generator:
        yield
        pathlib.Path(self.filepath).touch(mode=755, exist_ok=True)


class WriteFileJob(FilesJobMixin, Job):
    @coroutine
    def underlying(self) -> Coroutine:
        with open(self.filepath, "w") as f:
            while line := (yield):
                f.write(line)


class ReadFileJob(FilesJobMixin, Job):
    @coroutine
    def underlying(self) -> Coroutine:
        with open(self.filepath, "r") as f:
            for line in f:
                if self.target:
                    self.target.run(line)
                yield
        if self.target:
            self.target.stop()
