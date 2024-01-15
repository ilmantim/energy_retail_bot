# Generated by Django 5.0 on 2024-01-15 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('retail', '0011_bill_id_device_bill_id_indication_bill_id_tariff'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_tariff', models.IntegerField(blank=True, null=True, verbose_name='ID тарифа')),
                ('id_indication', models.IntegerField(blank=True, null=True, verbose_name='ID показания')),
                ('registration_date', models.DateTimeField(blank=True, null=True, verbose_name='Дата приёма')),
                ('readings', models.IntegerField(blank=True, null=True, verbose_name='Показания счетчика')),
            ],
        ),
        migrations.RemoveField(
            model_name='bill',
            name='id_indication',
        ),
        migrations.RemoveField(
            model_name='bill',
            name='id_tariff',
        ),
        migrations.RemoveField(
            model_name='bill',
            name='readings',
        ),
        migrations.RemoveField(
            model_name='bill',
            name='registration_date',
        ),
    ]