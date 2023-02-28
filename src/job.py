import time
import logging
import datetime
from uuid import uuid4
from enum import Enum
from functools import wraps
from typing import Optional, Any
from collections.abc import Generator, Coroutine, Callable
from abc import ABC, abstractmethod

from src.utils import string_to_timestamp
from src.exceptions import TimeLimitExceededException, MaxAttemptExceededException


def timed_run(func: Callable):
    @wraps(func)
    def inner(job: "Job", *args, **kwargs):
        start_time = time.time()
        res = func(job, *args, **kwargs)
        job.running_time += time.time() - start_time
        return res

    return inner


class JobStatus(Enum):
    NOT_STARTED = "NOT STARTED"
    STARTED = "STARTED"
    FAILED = "FAILED"
    FINISHED = "FINISHED"


class Job(ABC):
    def __init__(
        self,
        *,
        job_id: str | None = None,
        parent_id: str | None = None,
        target: Optional["Job"] = None,
        start_at: str = "",
        max_working_time: int = -1,
        tries: int = 0,
        depends_on: list["Job"] = None,
    ):
        self.job_id = job_id if job_id else str(uuid4())
        self.start_at = start_at
        self.max_working_time = max_working_time
        self.max_retries = tries
        self.running_time = 0
        self.tries = 0
        self.target = target
        self.depends_on = depends_on or []
        self.status: JobStatus = JobStatus.NOT_STARTED
        self.parent_id: str | None = parent_id
        self.gen_or_coro: Generator | Coroutine | None = None

    def run(self, data: Any = None):
        logging.debug(f"Trying to run {self.__class__.__name__} {self.job_id}.")

        if self.has_exceeded_time_limit:
            logging.warning(f"Time limit has exceeded for job {self.job_id}.")
            raise TimeLimitExceededException(
                message=f"Time limit has exceeded for job {self.job_id}."
            )

        try:
            if not self.is_ready_to_start:
                return

            self.__run(data)
        except Exception as ex:
            if self.max_retries <= 0 or type(ex) == StopIteration:
                if type(ex) != StopIteration:
                    logging.exception(ex)
                else:
                    logging.info(f"Job {self.job_id} has run it's course.")
                raise StopIteration

            logging.exception(ex)
            self.tries += 1
            if self.tries >= self.max_retries:
                logging.warning(
                    f"Job {self.job_id} reached maximum number of attempts."
                )
                raise MaxAttemptExceededException

    @timed_run
    def __run(self, data: Any = None):
        self.gen_or_coro.send(data)

    @property
    def is_ready_to_start(self) -> bool:
        if self.status == JobStatus.STARTED:
            return True
        if (
            not self.start_at
            or string_to_timestamp(self.start_at) <= datetime.datetime.now().timestamp()
        ):
            self.gen_or_coro = self.underlying()
            self.status = JobStatus.STARTED
            return True
        return False

    @property
    def has_exceeded_time_limit(self) -> bool:
        if self.max_working_time <= 0:
            return False
        return self.running_time >= self.max_working_time

    @abstractmethod
    def underlying(self, *args, **kwargs) -> Generator | Coroutine:
        raise NotImplementedError

    def stop(self) -> None:
        self.status = JobStatus.FINISHED if self.status.STARTED else self.status
        if self.gen_or_coro:
            self.gen_or_coro.close()

    def to_json(self) -> dict:
        data = self.__dict__.copy()

        data.pop("status")
        data.pop("gen_or_coro")
        data.pop("running_time")

        data["target"] = self.target.to_json() if self.target else None
        data["depends_on"] = [x.to_json() for x in self.depends_on]
        data["class_name"] = self.__class__.__name__
        return data

    def __str__(self):
        return f"{self.job_id}"
