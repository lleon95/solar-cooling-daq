from daq.outputs import csv, console
from daq import IOutput
from enum import Enum
from typing import Annotated


class Outputs(Enum):
    """
    Enum to enumerate the supported output mechanisms
    """
    CSV_FILE_WRITER = Annotated[int, "CSV File Writer"](0)
    CONSOLE_WRITER = Annotated[int, "Console Writer"](1)


def OutputBuilder(val: Outputs, name: str, logger: object) -> IOutput.IOutput:
    """
    Output Builder Factory

    This function is a factory function to generate the outputs and implement
    them without accessing to the classes directly
    """
    if (val == Outputs.CSV_FILE_WRITER):
        return csv.CSVFileWriter(name, logger)
    elif (val == Outputs.CONSOLE_WRITER):
        return console.ConsoleWriter(name, logger)
    return None
