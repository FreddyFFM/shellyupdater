# Generated by Django 2.2.11 on 2020-03-23 11:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('updates', '0012_shellysettings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shellysettings',
            name='shelly_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='shelly2infos', to='updates.Shellies'),
        ),
    ]
