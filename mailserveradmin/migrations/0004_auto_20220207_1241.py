# Generated by Django 3.2.12 on 2022-02-07 12:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mailserveradmin', '0003_auto_20220207_0054'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='maildomain',
            options={'ordering': ['name'], 'permissions': [('add_alias', 'Can add an alias to this domain')]},
        ),
        migrations.AlterModelOptions(
            name='mailuser',
            options={'ordering': ['name', 'domain__name'], 'permissions': [('add_domain', 'Can add a new domain')]},
        ),
    ]