# Generated by Django 4.1.4 on 2023-07-18 08:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0032_alter_reply_votes'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='voters',
            field=models.TextField(default=[]),
        ),
        migrations.AddField(
            model_name='reply',
            name='voters',
            field=models.TextField(default=[]),
        ),
    ]
