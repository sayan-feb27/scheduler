# How-to

- Create `setup_jobs.py` file.
- Setup jobs.
- Create variable `JOBS` of type `list`.
- Add jobs into that variable.
- Import `JOBS` in `main.py`.

```python
__all__ = ["JOBS"]

import pathlib

from src.jobs import CreateFileJob, WriteFileJob, ReadFileJob

file_creator_job = ReadFileJob(
        filepath=pathlib.Path("./log1.txt").resolve().as_posix(),
        tries=-1,
        max_working_time=1,
        target=WriteFileJob(
                filepath="/Users/space_monkey/Desktop/tmp1.txt"
        ),
        depends_on=[
            CreateFileJob(
                    filepath="/Users/space_monkey/Desktop/tmp1.txt",
            ),
        ],
)


JOBS = [
    file_creator_job
]
```