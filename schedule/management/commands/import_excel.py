import openpyxl
from django.core.management.base import BaseCommand
from schedule.models import Lesson, TimeSlot

DAY_MAP = {
    "Понедельник": 0, "Вторник": 1, "Среда": 2,
    "Четверг": 3, "Пятница": 4,
}


class Command(BaseCommand):
    help = "Импорт расписания из первого листа Excel"

    def add_arguments(self, parser):
        parser.add_argument("file", type=str, help="Путь к .xlsx")

    def handle(self, *args, **options):
        wb = openpyxl.load_workbook(options["file"], data_only=True)
        ws = wb.worksheets[0]  # первый лист

        Lesson.objects.all().delete()
        TimeSlot.objects.all().delete()

        created_lessons = 0
        seen_slots = {}

        for row in ws.iter_rows(min_row=2, values_only=True):
            day_str, num, start, end, cls, subj, teacher, room = row[:8]

            if not day_str or not cls:
                continue

            day = DAY_MAP.get(str(day_str).strip())
            if day is None:
                continue

            num = int(num)
            # 归一化时间（Excel 可能给 time 对象或字符串）
            def norm(t):
                if hasattr(t, "strftime"):
                    return t.strftime("%H:%M")
                return str(t)[:5]

            start_s, end_s = norm(start), norm(end)

            key = (day, num)
            if key not in seen_slots:
                TimeSlot.objects.get_or_create(
                    day=day, lesson_number=num,
                    defaults={"start_time": start_s, "end_time": end_s},
                )
                seen_slots[key] = True

            Lesson.objects.create(
                day=day,
                lesson_number=num,
                start_time=start_s,
                end_time=end_s,
                school_class=str(cls).strip(),
                subject=str(subj).strip() if subj else "",
                teacher=str(teacher).strip() if teacher else "",
                classroom=str(room).strip() if room else "",
            )
            created_lessons += 1

        self.stdout.write(self.style.SUCCESS(
            f"Импортировано уроков: {created_lessons}, слотов: {len(seen_slots)}"
        ))