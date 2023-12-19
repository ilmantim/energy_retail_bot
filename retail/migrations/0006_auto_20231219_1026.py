# Generated by Django 5.0 on 2023-12-19 07:26

from django.db import migrations
from dictionary_migration import info


def fill_up_mros(apps, schema_editor):
    Mro = apps.get_model('retail', 'Mro')
    Address = apps.get_model('retail', 'Address')
    for mro in info:
        mro_here = Mro.objects.create(name=mro)
        mro_here.general = info[mro]['general']
        mro_here.save()
        print(mro)
        if 'detailed' in info[mro]:
            for key, value in info[mro]['detailed'].items():
                address_here = Address.objects.create(name=value, num=key)
                address_here.department = mro_here
                address_here.save()


class Migration(migrations.Migration):

    dependencies = [
        ('retail', '0005_address_num'),
    ]

    operations = [
        migrations.RunPython(fill_up_mros)
    ]
