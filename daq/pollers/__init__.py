from daq.pollers import roundrobin
from daq import IPoller
from enum import Enum
from typing import Annotated


class Pollers(Enum):
    """
    Enum to enumerate the supported sensors
    """
    ROUND_ROBIN = Annotated[int, "Round Robin implementation for the Poller"]


def PollerBuilder(val: Pollers, name: str, logger: object) -> IPoller.IPoller:
    """
    Poller Builder Factory

    This function is a factory function to generate the sensors and implement
    them without accessing to the classes directly
    """
    if (val == Pollers.ROUND_ROBIN):
        return roundrobin.RoundRobinPoller(name, logger)
    return None
