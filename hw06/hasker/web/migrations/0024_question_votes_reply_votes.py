# Generated by Django 4.1.4 on 2023-07-17 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0023_alter_question_created_at_alter_reply_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='votes',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='reply',
            name='votes',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
