# Generated by Django 2.1.7 on 2019-05-20 19:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bookmark', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='restaurant',
            name='address',
        ),
        migrations.RemoveField(
            model_name='restaurant',
            name='name',
        ),
    ]
