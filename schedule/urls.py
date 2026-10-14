from django.urls import path
from . import views

app_name = "schedule"

urlpatterns = [
    path("", views.home, name="home"),
    path("now/", views.occupancy_now, name="now"),
    path("classrooms/<int:day>/", views.classrooms_day, name="classrooms_day"),
    path("classes/", views.classes_list, name="classes_list"),
    path("classes/<path:class_name>/", views.class_schedule, name="class_schedule"),
    path("teachers/<path:teacher_name>/", views.teacher_schedule, name="teacher_schedule"),

]