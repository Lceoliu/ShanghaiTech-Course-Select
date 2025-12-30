"""Course auto selection package."""

from .backends import Backends, LoginEncryptModel, ScheduleAutoSelector
from .cli import main as cli_main
from .ui import FrontWindow

__all__ = [
    "Backends",
    "LoginEncryptModel",
    "ScheduleAutoSelector",
    "cli_main",
    "FrontWindow",
]
