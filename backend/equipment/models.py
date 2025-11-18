from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import json
import os


class Dataset(models.Model):
    """Model for storing uploaded CSV datasets."""
    name = models.CharField(max_length=255)
    original_filename = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    csv_file = models.FileField(upload_to='uploads/')
    
    # Computed statistics
    total_count = models.IntegerField(default=0)
    avg_flowrate = models.FloatField(null=True, blank=True)
    avg_pressure = models.FloatField(null=True, blank=True)
    avg_temperature = models.FloatField(null=True, blank=True)
    type_distribution = models.JSONField(default=dict, blank=True)
    preview_rows = models.JSONField(default=list, blank=True)  # Store first 100 rows
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Dataset'
        verbose_name_plural = 'Datasets'
    
    def __str__(self):
        return f"{self.name} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"
    
    def save(self, *args, **kwargs):
        """
        Override save to ensure only the last 5 datasets are kept.
        """
        super().save(*args, **kwargs)
        self.prune_old_datasets()
    
    def prune_old_datasets(self):
        """
        Keep only the last 5 datasets, deleting older ones.
        This is called after saving a new dataset.
        """
        # Get all datasets ordered by upload date (newest first)
        all_datasets = Dataset.objects.order_by('-uploaded_at')
        
        # If we have more than 5 datasets, delete the older ones
        if all_datasets.count() > 5:
            # Get datasets to delete (older than the 5th most recent)
            datasets_to_delete = all_datasets[5:]
            for old_dataset in datasets_to_delete:
                # Delete the associated file if it exists
                if old_dataset.csv_file:
                    try:
                        if os.path.exists(old_dataset.csv_file.path):
                            os.remove(old_dataset.csv_file.path)
                    except (ValueError, OSError):
                        # File might not exist or path might be relative
                        pass
                # Delete the database record
                old_dataset.delete()


class Equipment(models.Model):
    """Model for individual equipment records."""
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='equipment')
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=100)
    flowrate = models.FloatField()
    pressure = models.FloatField()
    temperature = models.FloatField()
    
    class Meta:
        verbose_name = 'Equipment'
        verbose_name_plural = 'Equipment'
    
    def __str__(self):
        return f"{self.name} ({self.type})"
