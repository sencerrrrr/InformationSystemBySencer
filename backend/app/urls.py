from django.urls import path
from . import views
from .Views import (
    UsersAPI,
    StudentsAPI, StudentsCreateAPI,
    TeachersAPI, TeachersCreateAPI,
    RolesAPI, RolesCreateAPI,
    CitiesAPI, CitiesCreateAPI,
    RegionsAPI, RegionsCreateAPI
)

urlpatterns = [
    # Пользователи
    path('users/', UsersAPI.as_view(), name='user-api'),

    # Студенты
    path('students/', StudentsAPI.as_view(), name='students-api'),
    path('students/register/', StudentsCreateAPI.as_view(), name='register-api'),
    path('students/<int:pk>/certificate/', views.StudentCertificateAPI.as_view(), name='student-certificate'),

    # Преподаватели
    path('teachers/', TeachersAPI.as_view(), name='teachers-api'),
    path('teachers/register/', TeachersCreateAPI.as_view(), name='teacher-register-api'),

    # Регионы
    path('regions/', RegionsAPI.as_view(), name='regions-api'),
    path('regions/create/', RegionsCreateAPI.as_view(), name='region-register-api'),

    # Города
    path('cities/', CitiesAPI.as_view(), name='cities-api'),
    path('cities/create/', CitiesCreateAPI.as_view(), name='city-register-api'),

    # Роли
    path('roles/', RolesAPI.as_view(), name='roles-api'),
    path('roles/create/', RolesCreateAPI.as_view(), name='roles-create-api'),

    # Авторизация
    path('auth/login/', views.LoginAPI.as_view(), name='login'),
    path('auth/logout/', views.LogoutAPI.as_view(), name='logout'),
]
