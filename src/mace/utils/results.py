from typing import TextIO
import os


class Results:
    data: list[str]
    headers: list[str]

    def __init__(self) -> None:
        self.data = []
        self.headers = []

    def push(self, headers, values):
        self.headers.extend(list(map(str, headers)))
        self.data.extend(list(map(str, values)))

    def as_csv_line(self, delimitter: str=",", header=False) -> str:
        line = f" {delimitter}".join(self.data)
        if header:
            line = f" {delimitter}".join(self.data) + line
        return line
