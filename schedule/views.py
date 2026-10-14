from datetime import datetime
from django.shortcuts import render
from django.utils import timezone
from .models import Lesson, TimeSlot
from django.shortcuts import get_object_or_404
from urllib.parse import unquote

# добавь в импорты наверху


DAYS = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница"]


def occupancy_now(request):
    now = timezone.localtime()
    weekday = now.weekday()          # 0=Пн ... 4=Пт, 5-6 = выходные
    current_time = now.time()

    context = {
        "now": now,
        "weekday_name": DAYS[weekday] if weekday < 5 else "Выходной",
        "slot": None,
        "lessons": [],
        "free_classrooms": [],
        "busy_classrooms": [],
        "free_classes": [],
        "busy_classes": [],
    }

    # Если выходной — показываем только дату и сообщение
    if weekday > 4:
        context["message"] = "Сегодня выходной"
        return render(request, "schedule/now.html", context)

    # Ищем текущий слот: день совпадает, время попадает в интервал
    slot = TimeSlot.objects.filter(
        day=weekday,
        start_time__lte=current_time,
        end_time__gte=current_time,
    ).first()

    if not slot:
        context["message"] = "Сейчас нет урока (перемена или внеурочное время)"
        return render(request, "schedule/now.html", context)

    context["slot"] = slot

    # Все уроки в этом слоте
    lessons = Lesson.objects.filter(
        day=weekday,
        lesson_number=slot.lesson_number,
    ).select_related()

    context["lessons"] = lessons

    # Занятые кабинеты и классы
    busy_classrooms = {l.classroom for l in lessons}
    busy_classes = {l.school_class for l in lessons}

    # Все кабинеты, которые вообще встречаются в расписании
    all_classrooms = (
        Lesson.objects.values_list("classroom", flat=True).distinct()
    )
    all_classes = (
        Lesson.objects.values_list("school_class", flat=True).distinct()
    )

    context["busy_classrooms"] = sorted(busy_classrooms)
    context["free_classrooms"] = sorted(set(all_classrooms) - busy_classrooms)
    context["busy_classes"] = sorted(busy_classes)
    context["free_classes"] = sorted(set(all_classes) - busy_classes)

    return render(request, "schedule/now.html", context)

def classrooms_day(request, day):
    """Сетка кабинетов на выбранный день недели (0..4)."""
    if day < 0 or day > 4:
        from django.http import Http404
        raise Http404("Неверный день недели")

    # Все кабинеты, которые встречаются в расписании
    classrooms = sorted(
        set(Lesson.objects.values_list("classroom", flat=True))
    )

    # Все номера уроков, которые есть в этот день
    lesson_numbers = sorted(
        set(Lesson.objects.filter(day=day)
        .values_list("lesson_number", flat=True))

    )

    # Время начала/конца для каждого номера — из TimeSlot
    slots = {
        s.lesson_number: s
        for s in TimeSlot.objects.filter(day=day)
    }

    # Все уроки этого дня, сгруппируем в словарь по (кабинет, номер урока)
    lessons = Lesson.objects.filter(day=day)
    grid = {}
    for l in lessons:
        grid[(l.classroom, l.lesson_number)] = l

    # Собираем строки: для каждого кабинета — список ячеек
    rows = []
    for room in classrooms:
        cells = []
        for num in lesson_numbers:
            cells.append({
                "number": num,
                "lesson": grid.get((room, num)),
            })
        rows.append({"classroom": room, "cells": cells})

    context = {
        "day": day,
        "day_name": DAYS[day],
        "lesson_numbers": lesson_numbers,
        "slots": slots,
        "rows": rows,
        "days": [(i, DAYS[i]) for i in range(5)],
    }
    return render(request, "schedule/classrooms_day.html", context)

def class_schedule(request, class_name):
    class_name = unquote(class_name)
    """Расписание одного класса на неделю."""
    lessons = Lesson.objects.filter(
        school_class=class_name
    ).order_by("day", "lesson_number")

    # Собираем «таблицу»: строки — номера уроков, колонки — дни
    # row.cells[j] — список уроков для дня j
    lesson_numbers = sorted({l.lesson_number for l in lessons})

    # Заготовка: {(day, num): [уроки]}
    bucket = {}
    for l in lessons:
        bucket.setdefault((l.day, l.lesson_number), []).append(l)

    rows = []
    for num in lesson_numbers:
        cells = []
        for day in range(5):
            cells.append(bucket.get((day, num), []))
        rows.append({"number": num, "cells": cells})

    slots = {s.lesson_number: s for s in TimeSlot.objects.filter(day=0)}

    context = {
        "class_name": class_name,
        "days": [(i, DAYS[i]) for i in range(5)],
        "slots": slots,
        "rows": rows,
    }
    return render(request, "schedule/class_schedule.html", context)
def teacher_schedule(request, teacher_name):

    teacher_name = unquote(teacher_name)

    """Расписание одного учителя на неделю."""
    lessons = Lesson.objects.filter(
        teacher=teacher_name
    ).order_by("day", "lesson_number")

    lesson_numbers = sorted({l.lesson_number for l in lessons})

    bucket = {}
    for l in lessons:
        bucket.setdefault((l.day, l.lesson_number), []).append(l)

    rows = []
    for num in lesson_numbers:
        cells = []
        for day in range(5):
            cells.append(bucket.get((day, num), []))
        rows.append({"number": num, "cells": cells})

    slots = {s.lesson_number: s for s in TimeSlot.objects.filter(day=0)}

    context = {
        "teacher_name": teacher_name,
        "days": [(i, DAYS[i]) for i in range(5)],
        "slots": slots,
        "rows": rows,
    }
    return render(request, "schedule/teacher_schedule.html", context)

def classes_list(request):
    """Список классов и учителей — точка входа."""
    classes = sorted(
        set(Lesson.objects.values_list("school_class", flat=True))
    )
    teachers = sorted(
        set(Lesson.objects.values_list("teacher", flat=True))
    )
    return render(request, "schedule/lists.html", {
        "classes": classes,
        "teachers": teachers,
    })

def home(request):
    return render(request, "schedule/home.html")