# Generated by Django 2.2 on 2020-05-23 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kmd_ntx_api', '0061_auto_20200523_1650'),
    ]

    operations = [
        migrations.AddField(
            model_name='last_notarised',
            name='block_height',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]
