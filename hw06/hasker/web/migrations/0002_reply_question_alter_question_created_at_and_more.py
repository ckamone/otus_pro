# Generated by Django 4.1.4 on 2023-06-13 20:07

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='reply',
            name='question',
            field=models.OneToOneField(default=None, on_delete=django.db.models.deletion.PROTECT, to='web.question'),
        ),
        migrations.AlterField(
            model_name='question',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 6, 13, 20, 7, 13, 900817, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='reply',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 6, 13, 20, 7, 13, 901121, tzinfo=datetime.timezone.utc)),
        ),
    ]
