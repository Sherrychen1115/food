"""當日已攝取熱量:全頻道合計,以這台電腦的本地日期為準,換日歸零。"""

from datetime import date, datetime


class DailyTotal:
    def __init__(self, today: date, kcal: float = 0.0):
        self.date = today
        self.kcal = kcal

    def add(self, now: datetime, kcal: float = 0.0) -> float:
        if now.date() != self.date:
            self.date, self.kcal = now.date(), 0.0
        self.kcal += kcal
        return self.kcal
