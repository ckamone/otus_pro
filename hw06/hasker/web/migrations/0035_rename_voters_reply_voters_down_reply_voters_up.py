# Generated by Django 4.1.4 on 2023-07-18 09:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0034_rename_voters_question_voters_down_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='reply',
            old_name='voters',
            new_name='voters_down',
        ),
        migrations.AddField(
            model_name='reply',
            name='voters_up',
            field=models.TextField(default=[]),
        ),
    ]