# Generated by Django 4.1.4 on 2023-06-24 09:07

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0020_alter_question_created_at_alter_reply_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 6, 24, 9, 7, 28, 804117, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='reply',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 6, 24, 9, 7, 28, 804644, tzinfo=datetime.timezone.utc)),
        ),
    ]