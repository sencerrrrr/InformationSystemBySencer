from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('check-data/', views.check_data, name='check_data'),
    path('api/test/', views.TestAPI.as_view(), name='test-api'),

    path('api/users/', views.UsersAPI.as_view(), name='user-api'),
    path('api/students/', views.StudentsAPI.as_view(), name='students-api'),
    path('api/students/register/', views.StudentsCreateAPI.as_view(), name='register-api'),

    path('api/teachers/', views.TeacherAPI.as_view(), name='teachers-api'),
    path('api/teachers/register/', views.TeacherCreateAPI.as_view(), name='register-api'),

    path('api/auth/login/', views.LoginAPI.as_view(), name='login'),
    path('api/auth/logout/', views.LogoutAPI.as_view(), name='logout'),
    path('api/auth/refresh/', views.RefreshTokenAPI.as_view(), name='token_refresh'),
    path('api/auth/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path("api/students/<int:pk>/certificate/", views.StudentCertificateAPI.as_view(), name="student-certificate"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
