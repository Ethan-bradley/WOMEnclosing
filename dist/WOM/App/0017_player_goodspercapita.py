# Generated by Django 3.1.2 on 2021-01-13 06:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0016_auto_20210113_0516'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='GoodsPerCapita',
            field=models.ImageField(default='', upload_to=''),
        ),
    ]
