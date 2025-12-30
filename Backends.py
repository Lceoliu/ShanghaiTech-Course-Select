"""Backward-compatible exports for backend components."""

from course_auto_select.backends import (
    Backends,
    LoginEncryptModel,
    ScheduleAutoSelector,
)

__all__ = ["Backends", "LoginEncryptModel", "ScheduleAutoSelector"]
