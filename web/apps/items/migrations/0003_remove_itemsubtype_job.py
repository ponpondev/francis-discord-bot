# Generated by Django 2.1 on 2018-08-20 04:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0002_itemsubtype_job'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='itemsubtype',
            name='job',
        ),
    ]