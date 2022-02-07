from re import compile

from Crypto.PublicKey import RSA
from django.core.exceptions import ValidationError
from django.db import models
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
