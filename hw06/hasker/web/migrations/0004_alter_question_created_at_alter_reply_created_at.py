# Generated by Django 4.1.4 on 2023-06-13 20:13

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0003_alter_question_created_at_alter_reply_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 6, 13, 20, 13, 10, 682307, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='reply',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 6, 13, 20, 13, 10, 682549, tzinfo=datetime.timezone.utc)),
        ),
    ]
