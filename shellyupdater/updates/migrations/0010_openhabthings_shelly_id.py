# Generated by Django 2.2.11 on 2020-03-20 10:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('updates', '0009_auto_20200320_1023'),
    ]

    operations = [
        migrations.AddField(
            model_name='openhabthings',
            name='shelly_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='updates.Shellies'),
        ),
    ]
