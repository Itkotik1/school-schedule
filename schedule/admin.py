from django.contrib import admin
from unfold.admin import ModelAdmin  # <-- вот это

from .models import Lesson, TimeSlot


@admin.register(Lesson)
class LessonAdmin(ModelAdmin):
    list_display = (
        "day", "lesson_number", "start_time", "end_time",
        "school_class", "subject", "teacher", "classroom",
    )
    list_filter = ("day", "lesson_number", "classroom", "teacher")
    search_fields = ("school_class", "subject", "teacher", "classroom")
    ordering = ("day", "lesson_number")


@admin.register(TimeSlot)
class TimeSlotAdmin(ModelAdmin):
    list_display = ("day", "lesson_number", "start_time", "end_time")
    list_filter = ("day",)
    ordering = ("day", "lesson_number")