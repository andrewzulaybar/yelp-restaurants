# Generated by Django 2.1.7 on 2019-05-08 04:27

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Restaurant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('address', models.CharField(max_length=100)),
                ('business_id', models.CharField(max_length=100)),
                ('visited', models.BooleanField()),
                ('bookmark', models.BooleanField()),
            ],
        ),
    ]
