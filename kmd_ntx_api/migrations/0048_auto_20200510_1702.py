# Generated by Django 2.2 on 2020-05-10 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kmd_ntx_api', '0047_auto_20200510_1656'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notarised_chain_daily',
            name='season',
        ),
        migrations.AddField(
            model_name='notarised_chain_daily',
            name='ntx_count',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]
