from django.db import models


class Scan(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    celery_task_id = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'Scan ID - {self.id} :: status - {self.status}'


class CheckInfo(models.Model):
    scan = models.ForeignKey(Scan, related_name='checks', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    result = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return f'Check {self.name} :: Scan {self.scan.id}'


class Finding(models.Model):
    check_info = models.ForeignKey(CheckInfo, related_name='findings', on_delete=models.CASCADE)
    severity = models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
        return f'Finding {self.severity} :: {self.check_info.name}'
