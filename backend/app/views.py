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
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import Student, Region, City, Teacher
from .serializers import *


class LoginAPI(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)  # всё равно нужен, но мы используем только access
            access_token = str(refresh.access_token)

            response = JsonResponse({
                'message': 'Успешный вход',
                'user': {
                    'id': user.id,
                    'username': user.username
                }
            })

            # Устанавливаем только access_token в куку
            response.set_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE'],
                value=access_token,
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].seconds,
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
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

        return response


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
        p.drawString(x_left, y_top, f'СПРАВКА № 44667 от {timezone.now().strftime("%d.%m.%Y")}')

        p.setFont('Roboto-Regular', 12)
        y = y_top - 40

        full_name = student.__str__()
        start_of_study = student.group.start_year
        speciality = student.group.speciality
        course = student.course
        duration_display = student.group.qualification.duration_display

        lines = [
            f'Выдана {full_name}',
            f'в том, что он в {start_of_study} году поступил, имея основное общее образование в ГАПОУ',
            f'"Альметьевский политехнический техникум" по имеющей государственную',
            f'аккредитацию образовательной программы среднего профессионального',
            f'образования {speciality} от 11 ноября 2015 года (бессрочно в',
            f'соответствии с ч.12 ст.92 ФЗ от 29.12.2012г. №273 ФЗ "Об образовании в РФ")',
            f'выданную Министерством образования и науки Республики Татарстан.',
            f'  В настоящее время обучается на {course} курсе по очной форме обучения, по',
            f'специальности среднего профессионального образования {speciality}',
            '',
            f'  Срок получения образования по образовательной программе среднего',
            f'профессионального образования по очной форме обучения {duration_display}',
            f'Справка выдана для предоставления в военный комиссариат РТ,',
            f'Лениногорский р-н с. Нижняя Чершила',
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
