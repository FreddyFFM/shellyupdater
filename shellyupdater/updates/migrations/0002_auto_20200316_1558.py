# Generated by Django 2.2.11 on 2020-03-16 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('updates', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shellies',
            name='shelly_id',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
