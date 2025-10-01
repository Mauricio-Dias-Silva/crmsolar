from django.contrib import admin
from .models import Course, Module, Lesson, Material

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'workload_hours', 'start_date', 'is_active')
    list_filter = ('is_active', 'start_date')
    search_fields = ('name', 'code')
    filter_horizontal = ('professors',)

class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 1

class MaterialInline(admin.StackedInline):
    model = Material
    extra = 1

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)
    inlines = [LessonInline]

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'duration_minutes')
    inlines = [MaterialInline]

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'uploaded_at')