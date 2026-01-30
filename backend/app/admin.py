from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import *


class SoftDeleteAdmin(admin.ModelAdmin):
    """
    Базовая админ‑панель с поддержкой мягкого удаления.
    """
    list_display = ['__str__', 'created_at', 'updated_at', 'get_is_deleted_display']
    list_filter = ['is_deleted', 'created_at', 'updated_at']
    actions = ['hard_delete_selected', 'restore_selected']
    readonly_fields = [
        'created_at',
        'created_by',
        'updated_at',
        'updated_by',
        'deleted_at',
        'deleted_by',
        'is_deleted',
    ]

    def get_queryset(self, request):
        # Используем all_objects, чтобы видеть все записи (включая удалённые)
        return self.model.all_objects.all()

    def get_is_deleted_display(self, obj):
        if obj.is_deleted:
            deleted_time = obj.deleted_at.strftime('%d.%m.%Y %H:%M') if obj.deleted_at else 'не указано'
            deleted_by = f"({obj.deleted_by})" if obj.deleted_by else ""
            display_text = f"{deleted_time} {deleted_by}".strip()

            return mark_safe(
                f'<span style="color: red; font-weight: bold;">🗑 Удалено<br><small>{display_text}</small></span>'
            )
        return mark_safe('<span style="color: green; font-weight: bold;">✓ Активно</span>')

    get_is_deleted_display.short_description = 'Статус'
    get_is_deleted_display.admin_order_field = 'is_deleted'

    @admin.action(description='Полностью удалить выбранное')
    def hard_delete_selected(self, request, queryset):
        """Полное (жёсткое) удаление выбранных объектов."""
        count = 0
        for obj in queryset:
            obj.hard_delete()
            count += 1
        self.message_user(request, f'Полностью удалено {count} записей.')

    @admin.action(description='↻ Восстановить выбранное')
    def restore_selected(self, request, queryset):
        """Восстановление мягко удалённых объектов."""
        count = queryset.filter(is_deleted=True).update(
            is_deleted=False,
            deleted_at=None,
            deleted_by=None,
        )
        self.message_user(request, f'Восстановлено {count} записей.')

    def delete_model(self, request, obj):
        """Переопределяем удаление одного объекта в админке."""
        obj.delete(deleted_by=request.user)

    def delete_queryset(self, request, queryset):
        """Переопределяем массовое удаление."""
        for obj in queryset:
            obj.delete(deleted_by=request.user)


# Обновляем все классы админки, чтобы использовать get_is_deleted_display вместо is_deleted_display
@admin.register(Region)
class RegionAdmin(SoftDeleteAdmin):
    search_fields = ['name']
    list_display = ['name']
    list_filter = ['is_deleted'] + SoftDeleteAdmin.list_filter


@admin.register(City)
class CityAdmin(SoftDeleteAdmin):
    search_fields = ['name', 'region__name']
    list_display = ['name', 'region']
    list_filter = ['region', 'is_deleted'] + SoftDeleteAdmin.list_filter


@admin.register(Student)
class StudentAdmin(SoftDeleteAdmin):
    search_fields = ['lastname', 'name', 'middlename', 'user__username']
    list_display = ['__str__', 'photo_preview',  'group']
    list_filter = ['group', 'is_deleted'] + SoftDeleteAdmin.list_filter
    readonly_fields = SoftDeleteAdmin.readonly_fields + ['photo_preview']

    def photo_preview(self, obj):
        if obj.photo:
            return mark_safe(
                f'<img src="{obj.photo.url}" style="max-height: 100px; border-radius: 5px;" />'
            )
        return "—"

    photo_preview.short_description = "Фото"


@admin.register(Teacher)
class TeacherAdmin(SoftDeleteAdmin):
    search_fields = ['lastname', 'name', 'middlename', 'user__username']
    list_display = ['__str__', 'photo_preview']
    list_filter = ['is_deleted'] + SoftDeleteAdmin.list_filter

    readonly_fields = SoftDeleteAdmin.readonly_fields + ['photo_preview']

    def photo_preview(self, obj):
        if obj.photo:
            return mark_safe(
                f'<img src="{obj.photo.url}" style="max-height: 100px; border-radius: 5px;" />'
            )
        return "—"

    photo_preview.short_description = "Фото"

@admin.register(CodeSpeciality)
class CodeSpecialityAdmin(SoftDeleteAdmin):
    search_fields = ['code', 'description']
    list_display = ['code', 'get_is_deleted_display']
    list_filter = ['is_deleted'] + SoftDeleteAdmin.list_filter


@admin.register(Speciality)
class SpecialityAdmin(SoftDeleteAdmin):
    search_fields = ['name', 'code__code']
    list_display = ['__str__', 'code', 'is_active']
    list_filter = ['is_active', 'is_deleted'] + SoftDeleteAdmin.list_filter


@admin.register(Qualification)
class QualificationAdmin(SoftDeleteAdmin):
    search_fields = ['name', 'speciality__name']
    list_display = ['name', 'speciality']
    list_filter = ['speciality', 'based', 'is_deleted'] + SoftDeleteAdmin.list_filter


@admin.register(Group)
class GroupAdmin(SoftDeleteAdmin):
    search_fields = ['name', 'speciality__name', 'curator__lastname']
    list_display = [
        'name',
        'speciality',
        'qualification',
        'curator'
    ]
    list_filter = ['speciality', 'qualification', 'curator', 'is_active', 'is_deleted'] + SoftDeleteAdmin.list_filter


admin.site.register(Role)