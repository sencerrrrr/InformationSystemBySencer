from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


# ==============================================================
# ================АБСТРАКТНЫЕ МОДЕЛИ И МЕНЕДЖЕРЫ================
# ==============================================================

class SoftDeleteManager(models.Manager):
    # Менеджер для работы с мягким удалением
    def get_queryset(self):
        # По умолчанию исключаем все удаленные объекты
        return super().get_queryset().filter(is_deleted=False)

    def all_with_deleted(self):
        # Все записи, включая удаленные
        return super().get_queryset()

    def deleted_only(self):
        # Только удаленные записи
        return super().get_queryset().filter(is_deleted=True)

    def restore(self, *args, **kwargs):
        # Восстановление удаленных данных
        qs = self.deleted_only().filter(*args, **kwargs)
        qs.update(is_deleted=False, deleted_at=None, deleted_by=None)
        return qs.count()


# Миксин для полей аудита (кто и когда удалил/обновил)
class AuditMixin(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
        editable=False,
        help_text='Устанавливается автоматически при создании',
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='created_%(class)s_set',
        verbose_name='Кем создано',
        help_text='Устанавливается автоматически при создании',
        editable=False,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления',
        help_text='Устанавливается автоматически при обновлении',
        editable=False,
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='updated_%(class)s_set',
        verbose_name='Кем обновлено',
        help_text='Устанавливается автоматически при обновлении',
        editable=False,
    )

    class Meta:
        abstract = True


# Миксин для мягкого удаления
class SoftDeleteMixin(models.Model):
    is_deleted = models.BooleanField(
        default=False,
        verbose_name='Удалено',
        help_text='Отметка об удалении (мягкое удаление)',
        db_index=True,
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата удаления',
        help_text='Дата и время удаления',
        editable=False,
    )
    deleted_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='deleted_%(class)s_set',
        verbose_name='Кем удалено',
        help_text='Пользователь удаливший запись',
        editable=False,
    )

    class Meta:
        abstract = True

    # Мягкое удаление
    def delete(self, using=None, keep_parents=False, deleted_by=None):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        if deleted_by:
            self.deleted_by = deleted_by
        self.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by'])

    # Полноценное удаление
    def hard_delete(self, using=None, keep_parents=False):
        super().delete(using=using, keep_parents=keep_parents)

    # Восстановление удаленного объекта
    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by'])


# Базовая модель с аудитом и мягким удалением
class BaseModel(AuditMixin, SoftDeleteMixin):
    objects = SoftDeleteManager()  # Кастомный менеджер для мягкого удаления
    all_objects = models.Manager()  # Стандартный менеджер (для администратора)

    class Meta:
        abstract = True

    # Автоматическое заполнение created_by/update_by при сохранении
    def save(self, *args, **kwargs):
        # Импорт происходит здесь, чтобы избежать цикличного импорта
        from django.contrib.auth import get_user

        try:
            user = get_user()
            if user and user.is_authenticated:
                if not self.pk:  # Если объект создается
                    self.created_by = user
                self.updated_by = user
            super().save(*args, **kwargs)
        except:
            # Если пользователь не доступен (например, в миграциях)
            pass

        super().save(*args, **kwargs)


# =============================================================
# ======================КОНКРЕТНЫЕ МОДЕЛИ======================
# =============================================================


class Region(BaseModel):
    name = models.CharField(
        max_length=100,
        verbose_name='Название региона',
        help_text='Введите название региона',
        unique=True,
        db_index=True,
    )

    class Meta:
        verbose_name = 'Регион'
        verbose_name_plural = 'Регионы'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_deleted', 'name']),
        ]

    def __str__(self):
        return self.name


class City(BaseModel):
    name = models.CharField(
        max_length=100,
        verbose_name='Название города',
        help_text='Введите название города',
        db_index=True,
    )
    region = models.ForeignKey(
        Region,
        on_delete=models.PROTECT,
        verbose_name='Регион',
        help_text='Выберите регион',
        related_name='cities',  # Позволит обращаться через region.cities.all()
    )

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['region']),
            models.Index(fields=['is_deleted', 'name']),
            models.Index(fields=['is_deleted', 'region']),
        ]
        unique_together = ['name', 'region']

    def __str__(self):
        return f"{self.name} ({self.region.name})"


class Teacher(BaseModel):
    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        verbose_name='Пользователь',
        help_text='Выберите пользователя',
        related_name='teacher_profile',
    )
    lastname = models.CharField(
        max_length=50,
        verbose_name='Фамилия',
        help_text='Введите фамилию',
        db_index=True,
    )
    name = models.CharField(
        max_length=50,
        verbose_name='Имя',
        help_text='Введите имя',
        db_index=True,
    )
    middlename = models.CharField(
        max_length=50,
        verbose_name='Отчество',
        help_text='Введите отчество',
        null=True,
        blank=True,
    )
    birth_date = models.DateField(
        verbose_name='Дата рождения',
        help_text='Введите дату рождения',
    )
    phone = PhoneNumberField(
        region='RU',
        verbose_name='Телефон',
        help_text='Введите номер телефона',
    )

    class Meta:
        verbose_name = 'Преподаватель'
        verbose_name_plural = 'Преподаватели'
        ordering = ['lastname', 'name', 'middlename']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['lastname']),
            models.Index(fields=['user']),
            models.Index(fields=['is_deleted', 'name', 'lastname', 'middlename']),
        ]

    def __str__(self):
        if self.middlename:
            return f"{self.lastname} {self.name} {self.middlename}"
        return f"{self.lastname} {self.name}"


class CodeSpeciality(BaseModel):
    # Валидация для кода по стандарту ХХ.ХХ.ХХ
    code_validator = RegexValidator(
        regex=r'^\d{2}\.\d{2}\.\d{2}$',
        message='Код должен быть в формате "ХХ.ХХ.ХХ"',
        code='invalid_code_format'
    )
    code = models.CharField(
        max_length=8,
        verbose_name='Код специальности',
        help_text='Введите код специальности в формате ХХ.ХХ.ХХ',
        validators=[code_validator],
        unique=True,
        db_index=True,
    )
    description = models.TextField(
        verbose_name='Дополнительная информация',
        help_text='Введите дополнительную информацию (необязательно)',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'Код специальности'
        verbose_name_plural = 'Коды специальностей'
        ordering = ['code']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_deleted', 'code']),
        ]

    def __str__(self):
        return self.code

    # Дополнительная валидация, чтобы очищались пробелы
    def clean(self):
        from django.core.exceptions import ValidationError

        if self.code:
            self.code = self.code.strip()

        super().clean()

    # Вызов clean() перед сохранением
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Speciality(BaseModel):
    code = models.OneToOneField(
        CodeSpeciality,
        on_delete=models.PROTECT,
        verbose_name='Код специальности',
        help_text='Выберите код специальности',
        related_name='speciality',
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Наименование спецаильности',
        help_text='Введите наименование специальности',
        db_index=True,
    )
    description = models.TextField(
        verbose_name='Описание специальности',
        help_text='Подробное описание специальности',
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активна',
        help_text='Специальность активна для набора',
    )

    class Meta:
        verbose_name = 'Специальность'
        verbose_name_plural = 'Специальности'
        ordering = ['code__code']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_deleted', 'is_active', 'name']),
        ]

    def __str__(self):
        return f"{self.code} ({self.name})"


class Qualification(BaseModel):
    speciality = models.ForeignKey(
        Speciality,
        on_delete=models.PROTECT,
        verbose_name='Специальность',
        help_text='Выберите специальность',
        related_name='qualifications',
    )
    name = models.CharField(
        max_length=50,
        verbose_name='Наименование квалификации',
        help_text='Введите наименование квалификации',
        db_index=True,
    )
    CHOICES = (
        ('9', 'На базе 9 классов'),
        ('11', 'На базе 11 классов')
    )
    based = models.CharField(
        max_length=2,
        choices=CHOICES,
        verbose_name='На базе скольки классов',
        help_text='Выберите на базе скольки классов',
        default='9'
    )
    duration_months = models.PositiveIntegerField(
        verbose_name='Срок обучения (в месяцах)',
        help_text='Введите срок обучения в месяцах (36 месяцев = 3 года)',
        default=36,
        validators=[
            MinValueValidator(1, message='Срок обучения должен быть не менее 1 месяца'),
            MaxValueValidator(120, message='Срок обучения должен быть не более 10 лет')
        ]
    )
    description = models.TextField(
        verbose_name='Дополнительная информация',
        help_text='Введите дополнительную информацию (необязательно)',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'Квалификация'
        verbose_name_plural = 'Квалификации'
        ordering = ['speciality__name', 'name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['speciality']),
            models.Index(fields=['based']),
            models.Index(fields=['is_deleted', 'speciality', 'based']),
        ]
        unique_together = ['speciality', 'name', 'based']

    def __str__(self):
        return self.name


class Group(BaseModel):
    name = models.CharField(
        max_length=10,
        verbose_name='Название группы',
        help_text='Введите название группы',
        unique=True,
        db_index=True,
    )
    speciality = models.ForeignKey(
        Speciality,
        on_delete=models.PROTECT,
        verbose_name='Специальность',
        help_text='Выберите специальность',
    )
    qualification = models.ForeignKey(
        Qualification,
        on_delete=models.PROTECT,
        verbose_name='Квалиифкация',
        help_text='Выберите квалификацию',
    )
    curator = models.ForeignKey(
        Teacher,
        on_delete=models.PROTECT,
        verbose_name='Куратор',
        help_text='Выберите куратора',
        null=True,
        blank=True,
    )
    start_year = models.PositiveIntegerField(
        verbose_name='Год начала обучения',
        help_text='Год начала обучения группы',
        default=timezone.now().year
    )
    end_year = models.PositiveIntegerField(
        verbose_name='Год окончания обучения',
        help_text='Расчетный год окончания обучения',
        null=True,
        blank=True
    )
    max_students = models.PositiveIntegerField(
        verbose_name='Максимальное количество студентов',
        help_text='Максимальное количество студентов в группе',
        default=25
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='Активная группа',
        help_text='Группа активна и ведет обучение'
    )

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['speciality']),
            models.Index(fields=['qualification']),
            models.Index(fields=['curator']),
            models.Index(fields=['is_active']),
            models.Index(fields=['start_year']),
            models.Index(fields=['is_deleted', 'is_active', 'start_year']),
        ]

    def __str__(self):
        return self.name

    # Автоматический расчет года окончания
    def save(self, *args, **kwargs):
        if self.qualification and self.start_year and not self.end_year:
            # Расчет года окончания на основе срока обучения
            years_to_add = self.qualification.duration_months // 12
            self.end_year = self.start_year + years_to_add
        super().save(*args, **kwargs)


class Student(BaseModel):
    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        verbose_name='Пользователь',
        help_text='Выберите пользователя',
        related_name='student_profile',
    )
    lastname = models.CharField(
        max_length=50,
        verbose_name='Фамилия',
        help_text='Введите фамилию',
        db_index=True,
    )
    name = models.CharField(
        max_length=50,
        verbose_name='Имя',
        help_text='Введите имя',
        db_index=True,
    )
    middlename = models.CharField(
        max_length=50,
        verbose_name='Отчество',
        help_text='Введите отчество',
        null=True,
        blank=True,
    )
    birth_date = models.DateField(
        verbose_name='Дата рождения',
        help_text='Введите дату рождения',
    )
    phone = PhoneNumberField(
        region='RU',
        verbose_name='Телефон',
        help_text='Введите номер телефона',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.PROTECT,
        verbose_name='Группа',
        help_text='Выберите группу',
    )

    class Meta:
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенты'
        ordering = ['name', 'lastname']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['lastname']),
            models.Index(fields=['user']),
            models.Index(fields=['is_deleted', 'name', 'lastname', 'middlename']),
        ]

    def __str__(self):
        if self.middlename:
            return f"{self.lastname} {self.name} {self.middlename}"
        return f"{self.lastname} {self.name}"

    @property
    def username(self):
        return self.user.username
