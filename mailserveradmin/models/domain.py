from pathlib import Path
from time import sleep
from re import compile

from Crypto.PublicKey import RSA
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from dns.exception import DNSException
from dns.resolver import Resolver


def dkim_validator(value):
    dkim_pattern = compile(r'^[a-z0-9]{0,50}$')
    if not dkim_pattern.match(value):
        raise ValidationError(
            _("%(value)s is not a valid dkim selector, only lower-cased letters and digits are allowed."),
            params={'value': value},
        )


class MailDomain(models.Model):
    name = models.CharField(max_length=255, unique=True)
    dkim_enabled = models.BooleanField(default=False)
    dkim_selector = models.CharField(max_length=50, null=True, blank=True, validators=[dkim_validator])
    dkim_private_key = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def dkim_validated(self):
        if self.dkim_enabled and self.dkim_selector and self.dkim_private_key:
            try:
                dkim_answer = Resolver().query(f'{self.dkim_selector}._domainkey.{self.name}', 'txt', lifetime=3)
            except DNSException:
                return False
            else:
                try:
                    dkim_text = next(iter(dkim_answer)).to_text()
                    dkim = dict(v.replace(' ', '').split('=', 1) for v in dkim_text.replace('"', '').split(';'))
                    if all((
                        dkim.get('v', '') == 'DKIM1',
                        dkim.get('h', '') == 'sha256',
                        dkim.get('t', '') == 's',
                        'p' in dkim,
                    )):
                        presented_pub_key = dkim['p']
                        priv_key = RSA.import_key(self.dkim_private_key)
                        pub_key = ''.join(priv_key.public_key().export_key().decode('ascii').split('\n')[1:-1])
                        return presented_pub_key == pub_key
                    else:
                        return False
                except Exception:
                    return False
        else:
            return False

    def get_absolute_url(self):
        return reverse('domain-detail', kwargs={'pk': self.pk})

    class Meta:
        db_table = 'mail_domain'
        ordering = ['name']
        permissions = [
            ('add_mailuser', "Can add a user to this domain"),
            ('add_mailalias', "Can add an alias to this domain"),
        ]


@receiver(models.signals.post_save, sender=MailDomain)
@receiver(models.signals.pre_delete, sender=MailDomain)
def store_pkeys_on_domain_post_update(sender, instance, **kwargs):
    if kwargs.get('raw'):
        return
    dkim_path_name = settings.DKIM_PATH
    if not dkim_path_name:
        return
    dkim_path = Path(dkim_path_name)
    dkim_path.mkdir(parents=True, exist_ok=True)
    lock_file = dkim_path / '.lock'
    # ten seconds is more than enough to update some simple text files
    # but the DNS query could take a bit of time
    MAX_WAIT_SEC = 10
    wait_sec = 0
    while lock_file.exists():
        sleep(1)
        wait_sec += 1
        if wait_sec > MAX_WAIT_SEC:
            # force to continue
            lock_file.unlink()
            break
    try:
        lock_file.touch()
        if instance.dkim_validated:
            with (dkim_path / f'{instance.name}.{instance.dkim_selector}.key').open('w', encoding='utf8') as f:
                f.write(instance.dkim_private_key)
                f.write('\n')
            with (dkim_path / 'dkim_selectors.map').open('w+', encoding='utf8') as f:
                lines = sorted(
                    [line for line in f.readlines() if not line.startswith(f'{instance.name} ')]
                    + [f'{instance.name} {instance.dkim_selector}\n']
                )
                f.seek(0)
                f.writelines(lines)
        else:
            for key in dkim_path.glob(f'{instance.name}.*.key'):
                key.unlink()
            with (dkim_path / 'dkim_selectors.map').open('w+', encoding='utf8') as f:
                lines = [line for line in f.readlines() if not line.startswith(f'{instance.name} ')]
                f.seek(0)
                f.writelines(lines)
    finally:
        lock_file.unlink()
