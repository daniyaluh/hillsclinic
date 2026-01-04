from django.contrib import admin
from .models import Doctor


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['name', 'title', 'specialty', 'role', 'is_featured', 'is_active', 'order']
    list_filter = ['specialty', 'is_featured', 'is_active']
    search_fields = ['name', 'bio', 'role']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order', 'is_featured', 'is_active']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'title', 'specialty', 'role')
        }),
        ('Profile', {
            'fields': ('photo', 'short_bio', 'bio')
        }),
        ('Credentials', {
            'fields': ('education', 'certifications', 'experience_years', 'languages')
        }),
        ('Contact', {
            'fields': ('email', 'linkedin_url'),
            'classes': ('collapse',)
        }),
        ('Display Options', {
            'fields': ('is_featured', 'is_active', 'order')
        }),
    )
