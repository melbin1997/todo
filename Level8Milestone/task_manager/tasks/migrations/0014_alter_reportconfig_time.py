# Generated by Django 4.0.3 on 2022-04-03 18:50

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0013_alter_notification_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reportconfig',
            name='time',
            field=models.TimeField(default=datetime.time(22, 0)),
        ),
    ]
