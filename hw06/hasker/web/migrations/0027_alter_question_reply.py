# Generated by Django 4.1.4 on 2023-07-17 17:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0026_alter_question_reply'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='reply',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.PROTECT, to='web.reply'),
        ),
    ]
