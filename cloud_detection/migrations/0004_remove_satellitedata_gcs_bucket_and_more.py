# Generated by Django 4.2.7 on 2025-07-12 14:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cloud_detection', '0003_satellitedata_gcs_bucket_satellitedata_gcs_path_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='satellitedata',
            name='gcs_bucket',
        ),
        migrations.RemoveField(
            model_name='satellitedata',
            name='gcs_path',
        ),
        migrations.RemoveField(
            model_name='satellitedata',
            name='upload_source',
        ),
    ]
