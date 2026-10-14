from django.db import models


class Lesson(models.Model):
    DAYS = [
        (0, "Понедельник"),
        (1, "Вторник"),
        (2, "Среда"),
        (3, "Четверг"),
        (4, "Пятница"),
    ]

    day = models.PositiveSmallIntegerField(choices=DAYS)
    lesson_number = models.PositiveSmallIntegerField()   # 1..12
    start_time = models.TimeField()
    end_time = models.TimeField()
    school_class = models.CharField(max_length=50)        # "5А", "11А/11Б", "Емельянова У."
    subject = models.CharField(max_length=150)            # "Мат", "Инф Зол."
    teacher = models.CharField(max_length=150)            # "Холина С.В."
    classroom = models.CharField(max_length=50)           # "105", "Зал 1", "дом"

    class Meta:
        ordering = ["day", "lesson_number"]
        indexes = [
            models.Index(fields=["day", "lesson_number"]),
            models.Index(fields=["classroom", "day", "lesson_number"]),
            models.Index(fields=["school_class", "day"]),
            models.Index(fields=["teacher", "day"]),
        ]

    def __str__(self):
        return f"{self.get_day_display()} #{self.lesson_number} | {self.school_class} | {self.subject}"

class TimeSlot(models.Model):
    day = models.PositiveSmallIntegerField()
    lesson_number = models.PositiveSmallIntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = ("day", "lesson_number")
        ordering = ["day", "lesson_number"]