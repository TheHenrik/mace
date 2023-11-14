from typing import TextIO
import os


class Results:
    data: list[str]

    def __init__(self, *args, empty=False) -> None:
        if empty == True:
            pass

    def write(self, file: TextIO):
        file.write(self.data)
        file.flush()
        os.fsync(file.fileno())