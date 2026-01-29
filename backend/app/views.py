import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse, Http404, FileResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import Student, Region, City, Teacher
from .serializers import HelloSerializer, StudentSerializer, UserSerializer, StudentCreateSerializer, TeacherSerializer, \
    TeacherCreateSerializer


# Проверка работы бэка. Позже удалить
def check_data(request):
    """Временный view для проверки данных"""
    output = []

    output.append("<h1>Проверка данных в базе</h1>")

    # Счетчики
    output.append(f"<p>Регионов: {Region.objects.count()}</p>")
    output.append(f"<p>Городов: {City.objects.count()}</p>")

    # Список регионов и городов
    output.append("<h2>Регионы и города:</h2>")
    for region in Region.objects.all().order_by('name'):
        cities = region.cities.all()
        city_list = ", ".join([city.name for city in cities])
        output.append(f"<p><b>{region.name}</b>: {city_list}</p>")

    return HttpResponse("\n".join(output))


# Проверка работы бэка. Позже удалить
class TestAPI(APIView):
    def get(self, request):
        data = {
            'message': 'Привет от Django Backend! 👋',
            'status': 'OK',
            'timestamp': timezone.now(),
            'method': 'GET'
        }
        serializer = HelloSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = HelloSerializer(data=request.data)
        if serializer.is_valid():
            return Response({
                'received': serializer.validated_data,
                'response': 'POST получен!',
                'timestamp': timezone.now()
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPI(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)

            response = JsonResponse({
                'message': 'Успешный вход',
                'user': {
                    'id': user.id,
                    'username': user.username
                }
            })

            # Устанавливаем куки с токенами
            response.set_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE'],
                value=str(refresh.access_token),
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].seconds,
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            )

            response.set_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
                value=str(refresh),
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].days * 24 * 3600,
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE']
            )

            return response

        return Response(
            {'error': 'Неверные учетные данные'},
            status=status.HTTP_401_UNAUTHORIZED,
        )


class LogoutAPI(APIView):
    def post(self, request):
        response = JsonResponse({'message': 'Успешный выход'})

        # Удаляем куки с токенами
        response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE'])
        response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])

        return response


class RefreshTokenAPI(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])

        if refresh_token:
            try:
                refresh = RefreshToken(refresh_token)
                new_access_token = str(refresh.access_token)

                response = JsonResponse({'message': 'Токен обновлен'})

                response.set_cookie(
                    key=settings.SIMPLE_JWT['AUTH_COOKIE'],
                    value=new_access_token,
                    httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                    max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].seconds,
                    samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
                    secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE']
                )

                return response
            except Exception as e:
                return Response(
                    {'error': 'Невалидный refresh token'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

        return Response(
            {'error': 'Refresh token не найден'},
            status=status.HTWT_400_BAD_REQUEST
        )


class UsersAPI(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StudentsAPI(APIView):
    def get(self, request):
        students = Student.objects.all()
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StudentsCreateAPI(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = StudentCreateSerializer(data=request.data)
        if serializer.is_valid():
            student = serializer.save()
            return Response({
                'message': 'Студент успешно создан',
                'student_id': student.id,
                'name': student.name,
                'username': student.user.username,
                'user_id': student.user.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeacherAPI(APIView):
    def get(self, request):
        teachers = Teacher.objects.all()
        serializer = TeacherSerializer(teachers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TeacherCreateAPI(APIView):
    def post(self, request):
        serializer = TeacherCreateSerializer(data=request.data)
        if serializer.is_valid():
            teacher = serializer.save()
            return Response({
                'message': 'Учитель успешно создан',
                'teacher_id': teacher.id,
                'name': teacher.name,
                'username': teacher.user.username,
                'user_id': teacher.user.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentCertificateAPI(APIView):
    permission_classes = [AllowAny]
    # Импортируем здесь
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    import os

    # Регистрируем шрифты
    font_path = "/app/app/fonts/Roboto-Regular.ttf"
    bold_font_path = "/app/app/fonts/Roboto-Bold.ttf"

    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont("Roboto-Regular", font_path))
        pdfmetrics.registerFont(TTFont("Roboto-Bold", bold_font_path))

    def get(self, request, pk):
        try:
            student = Student.objects.select_related('group').get(pk=pk)
        except Student.DoesNotExist:
            raise Http404('Студент не найден')

        # Буфер в памяти для PDF
        buffer = io.BytesIO()

        # Создаем PDF
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        x_left = 50
        y_top = height - 80

        p.setFont('Roboto-Bold', 16)
        p.drawString(x_left, y_top, 'СПРАВКА')

        p.setFont('Roboto-Regular', 12)
        y = y_top - 40

        full_name = student.__str__()
        group_name = student.group.name if hasattr(student.group, 'name') else str(student.group)

        lines = [
            f"Настоящая справка выдана {full_name},",
            f"дата рождения: {student.birth_date.strftime('%d.%m.%Y')}.",
            f"Является студентом группы {group_name}",
            "",
            "Справка по месту требования.",
        ]

        for line in lines:
            p.drawString(x_left, y, line)
            y -= 20

        # Подписи
        y -= 40
        p.drawString(x_left, y, "Руководитель _______________________")
        y -= 20
        p.drawString(x_left, y, "М.П.")

        # Завершаем страницу и PDF
        p.showPage()
        p.save()

        buffer.seek(0)

        filename = f"spravka_student_{student.id}.pdf"
        return FileResponse(buffer, as_attachment=True, filename=filename)
