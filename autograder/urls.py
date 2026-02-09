# autograder/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    # Student API
    path('grade/', views.grade_answer, name='grade_answer'),
    
    # Student Interface
    path('', views.student_interface, name='student_interface'),
    
    # Teacher Interfaces
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/add-question/', views.add_teacher_question, name='add_teacher_question'),
    path('teacher/delete/<str:question_id>/', views.delete_teacher_question, name='delete_teacher_question'),

     # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='student_interface'), name='logout'),
]