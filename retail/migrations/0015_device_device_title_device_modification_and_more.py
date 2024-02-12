# Generated by Django 5.0 on 2024-02-12 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('retail', '0014_remove_bill_address_remove_bill_id_device_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='device_title',
            field=models.TextField(blank=True, null=True, verbose_name='тип ПУ'),
        ),
        migrations.AddField(
            model_name='device',
            name='modification',
            field=models.TextField(blank=True, null=True, verbose_name='модификация ПУ'),
        ),
        migrations.AddField(
            model_name='device',
            name='serial_number',
            field=models.TextField(blank=True, null=True, verbose_name='серийный номер ПУ'),
        ),
    ]
