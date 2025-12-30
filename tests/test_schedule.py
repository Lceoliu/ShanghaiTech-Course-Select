"""Sanity checks for schedule helper."""

import datetime

from course_auto_select.backends.schedule import ScheduleAutoSelector


def test_schedule_ordering() -> None:
    scheduler = ScheduleAutoSelector()
    now = datetime.datetime.now()
    first = now + datetime.timedelta(minutes=1)
    second = now + datetime.timedelta(minutes=2)

    scheduler.add_schedule_time(second)
    scheduler.add_schedule_time(first)

    assert scheduler.get_remaining_seconds() is not None
    assert scheduler.schedule_timelist[0] == first


def test_clear_schedule() -> None:
    scheduler = ScheduleAutoSelector()
    scheduler.add_schedule("demo")
    scheduler.add_schedule_time(datetime.datetime.now())

    scheduler.clear_schedule()

    assert scheduler.schedule == []
    assert scheduler.schedule_timelist == []

if __name__ == "__main__":
    test_schedule_ordering()
    test_clear_schedule()
    print("schedule tests passed")
