# Generated by Django 5.1.6 on 2025-02-14 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0002_alter_user_full_name_alter_user_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='matric_number',
            field=models.CharField(blank=True, default='N/A', max_length=9, null=True),
        ),
    ]
