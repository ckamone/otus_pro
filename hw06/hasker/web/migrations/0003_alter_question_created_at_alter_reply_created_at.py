# Generated by Django 4.1.4 on 2023-06-13 20:12

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0002_reply_question_alter_question_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 6, 13, 20, 12, 12, 367929, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='reply',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 6, 13, 20, 12, 12, 368265, tzinfo=datetime.timezone.utc)),
        ),
    ]