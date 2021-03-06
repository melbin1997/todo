import sys
from django.db import models

from django.contrib.auth.models import User

STATUS_CHOICES = (
    ("PENDING", "PENDING"),
    ("IN_PROGRESS", "IN_PROGRESS"),
    ("COMPLETED", "COMPLETED"),
    ("CANCELLED", "CANCELLED"),
)

class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    completed = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank= True)
    priority = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=100, choices= STATUS_CHOICES, default=STATUS_CHOICES[0][0])

    __old_status = None
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__old_status = self.status

    def save(self, force_insert = False, force_update = False,  *args, **kwargs):
        if self.status != self.__old_status:
            TaskStatusChange(old_status=self.__old_status, new_status=self.status, task=self).save()
        super().save(force_insert, force_update, *args, **kwargs)
        self.__old_status = self.status

    def __str__(self):
        return self.title

class TaskStatusChange(models.Model):
    old_status = models.CharField(max_length=100, choices = STATUS_CHOICES)
    new_status = models.CharField(max_length=100, choices=STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)

    def __str__(self):
        return f'Task {self.task.id} : {self.old_status} -> {self.new_status}'