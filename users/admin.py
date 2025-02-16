from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Teacher, Student

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'name', 'phone', 'role', 'is_active', 'is_staff')
    search_fields = ('email', 'username', 'name', 'phone')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {'fields': ('name', 'phone', 'is_active', 'is_staff')}),
        ('Roles & Permissions', {'fields': ('role', 'controller_type', 'is_superuser')}),
        ('Identification', {'fields': ('pan_number', 'upi_id', 'aadhar_number')}),
        ('Location', {'fields': ('latitude', 'longitude')}),
    )

    # ✅ Updated `add_fieldsets` to include all fields (only required ones are necessary)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'username', 'name', 'phone', 'password1', 'password2', 'role',
                'controller_type', 'is_staff', 'is_superuser',  # Permissions
                'pan_number', 'upi_id', 'aadhar_number',        # Identification
                'latitude', 'longitude',                        # Location
            ),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)

# ✅ Teacher Model Admin
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'school_id', 'location')
    search_fields = ('user__email', 'user__name', 'school_id', 'location')
    filter_horizontal = ('subjects',)  # ✅ Allow selecting multiple subjects easily
    ordering = ('user__email',)

admin.site.register(Teacher, TeacherAdmin)

# ✅ Student Model Admin
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'class_name', 'school_id', 'location', 'date_of_birth')
    search_fields = ('user__email', 'user__name', 'school_id', 'location', 'class_name')
    list_filter = ('class_name',)
    ordering = ('user__email',)

admin.site.register(Student, StudentAdmin)
