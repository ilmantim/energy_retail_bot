# Generated by Django 5.0 on 2023-12-19 09:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('retail', '0004_rename_detailed_address_name_remove_address_general_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='num',
            field=models.IntegerField(blank=True, null=True, verbose_name='номер кнопки'),
        ),
    ]