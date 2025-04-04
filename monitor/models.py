from django.db import models

# Create your models here.


class Warning(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField()

    def __str__(self):
        return f"{self.timestamp}: {self.message}"
        # Custom table name
    class Meta:
        db_table = 'warnings'
