from django.db import migrations


def forwards(apps, schema_editor):
    MailAlias = apps.get_model('mailserveradmin', 'MailAlias')
    MailDomain = apps.get_model('mailserveradmin', 'MailDomain')
    MailAlias.objects.all().update(domain=MailDomain.objects.first())


def backwards(apps, schema_editor):
    ...


class Migration(migrations.Migration):
    dependencies = [
        ('mailserveradmin', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
