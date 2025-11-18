from django.contrib import admin
from .models import Dataset, Equipment


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ['name', 'original_filename', 'uploaded_by', 'uploaded_at', 'total_count']
    list_filter = ['uploaded_at', 'uploaded_by']
    search_fields = ['name', 'original_filename']
    readonly_fields = ['uploaded_at', 'total_count', 'avg_flowrate', 'avg_pressure', 'avg_temperature', 'type_distribution']


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'dataset', 'flowrate', 'pressure', 'temperature']
    list_filter = ['type', 'dataset']
    search_fields = ['name', 'type']
    readonly_fields = ['dataset']
