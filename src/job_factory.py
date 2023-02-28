from abc import ABC

from src.job import Job
from src.jobs import CreateFileJob, WriteFileJob, ReadFileJob


class JobFactory(ABC):
    JOBS = {
        CreateFileJob.__name__: CreateFileJob,
        WriteFileJob.__name__: WriteFileJob,
        ReadFileJob.__name__: ReadFileJob,
    }

    @classmethod
    def from_json(cls, data: dict) -> Job:
        data["target"] = (
            cls.from_json(data.get("target")) if data.get("target", None) else None
        )
        data["depends_on"] = [cls.from_json(x) for x in data.get("depends_on", [])]
        constructor = cls.JOBS.get(data.pop("class_name"))
        return constructor(**data)
