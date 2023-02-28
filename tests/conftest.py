import pytest
import pathlib


@pytest.fixture(scope="class")
def state_file_path() -> str:
    state_file = pathlib.Path.cwd().joinpath("data/state.json").resolve()
    return state_file.as_posix()


@pytest.fixture(scope="class")
def long_file_path() -> str:
    long_file = pathlib.Path.cwd().joinpath("data/long_file.txt").resolve()
    return long_file.as_posix()
