"""Scheduling helpers for automated course selection."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional


class ScheduleAutoSelector:
    """Keeps course ids and their associated trigger times ordered."""

    def __init__(self, delay_seconds: int = 30) -> None:
        self.schedule: List[str] = []
        self.schedule_timelist: List[datetime] = []
        self.delay_seconds = delay_seconds

    def add_schedule(self, course_id: str, order: int = -1) -> None:
        if order == -1:
            self.schedule.append(course_id)
        else:
            self.schedule.insert(order, course_id)

    def remove_schedule(self, course_id: str) -> None:
        if course_id in self.schedule:
            self.schedule.remove(course_id)

    def add_schedule_time(self, trigger_time: datetime) -> None:
        self.schedule_timelist.append(trigger_time)
        self.schedule_timelist.sort()

    def get_remaining_seconds(self) -> Optional[float]:
        self.remove_passed_time()
        if not self.schedule_timelist:
            return None
        next_time = self.schedule_timelist[0]
        return (next_time - datetime.now()).total_seconds()

    def remove_passed_time(self) -> None:
        threshold = datetime.now() - timedelta(seconds=self.delay_seconds)
        self.schedule_timelist = [time for time in self.schedule_timelist if time > threshold]

    def clear_schedule(self) -> None:
        self.schedule.clear()
        self.schedule_timelist.clear()
