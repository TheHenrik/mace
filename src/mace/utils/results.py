from typing import TextIO
import os


class Results:
    data: list[str]
    headers: list[str]

    def __init__(self) -> None:
        self.data = []
        self.headers = []

    def push(self, headers, values):
        """Adds headers and values to itself

        Args:
            headers (any): A single name or a list of names of data
            values (any): A single value or a list of values of data
        """
        self.headers.extend(list(map(str, headers)))
        self.data.extend(list(map(str, values)))

    def as_csv_line(self, delimitter: str=",", header=False) -> str:
        """Returns the collected data in a string using the given delimiters for use in a csv file

        Args:
            delimitter (str, optional): The chosen delimitter for the csv. Defaults to ",".
            header (bool, optional): also returns the header if selected. Defaults to False.

        Returns:
            str: csv usable string of the collected data
        """
        line = f" {delimitter}".join(self.data)
        if header:
            line = f" {delimitter}".join(self.data) + line
        return line
