from daq.outputs import csv
from daq import IOutput
from enum import Enum
from typing import Annotated


class Outputs(Enum):
    """
    Enum to enumerate the supported output mechanisms
    """
    CSV_FILE_WRITTER = Annotated[int, "CSV File Writter"](0)


def OutputBuilder(val: Outputs, name: str, logger: object) -> IOutput.IOutput:
    """
    Output Builder Factory

    This function is a factory function to generate the outputs and implement
    them without accessing to the classes directly
    """
    if (val == Outputs.CSV_FILE_WRITTER):
        return csv.CSVFileWriter(name, logger)
    return None
