# Generated by Django 3.1.2 on 2022-02-21 04:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0046_auto_20220220_0550'),
    ]

    operations = [
        migrations.AlterField(
            model_name='graphinterface',
            name='mode',
            field=models.CharField(choices=[('Income_Tax', 'Income Tax'), ('Corporate_Tax', 'Corporate Tax'), ('Welfare', 'Welfare'), ('Education', 'Education'), ('Science', 'Science'), ('Infrastructure', 'Infrastructure Spending'), ('Military', 'Military Spending'), ('MoneyPrintingArr', 'Money Printing'), ('Iron', 'Iron Prices'), ('Wheat', 'Wheat Prices'), ('Coal', 'Coal Prices'), ('Oil', 'Oil Prices'), ('Food', 'Food Prices'), ('ConsumerGoods', 'Consumer Goods Prices'), ('Steel', 'Steel Prices'), ('Machinery', 'Machinery Prices')], default='Income_Tax', max_length=20),
        ),
    ]
