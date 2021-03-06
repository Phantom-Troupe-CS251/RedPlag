# Generated by Django 3.1.2 on 2020-12-05 16:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0004_uploadfile_filetype'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistogramFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('histoutput', models.ImageField(upload_to='')),
                ('zipfile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='files.uploadfile')),
            ],
        ),
        migrations.CreateModel(
            name='HeatMapFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hmapoutput', models.ImageField(upload_to='')),
                ('zipfile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='files.uploadfile')),
            ],
        ),
    ]
