# Generated by Django 4.0.3 on 2022-03-25 11:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0004_task_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='priority',
            field=models.PositiveIntegerField(default=9223372036854775807),
        ),
    ]
