from django.contrib import admin
from .models import CustomUser, Job, JobApplication

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email')

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'category', 'location', 'employment_type', 'is_active', 'created_at')  # Duplicates olib tashlandi
    list_filter = ('category', 'employment_type', 'is_active')  # Duplicates olib tashlandi
    search_fields = ('title', 'company', 'location')

    def is_active(self, obj):
        return obj.is_active

    is_active.boolean = True  # Admin panelda 'is_active' maydonini belgi sifatida ko‘rsatadi


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'surname', 'job', 'status', 'applied_at')
    list_filter = ('status', 'job__category')
    search_fields = ('name', 'surname', 'job__title', 'email')

