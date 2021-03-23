from django.db import models
from django.urls import reverse

from .common import username_validator


class MailAlias(models.Model):
    name = models.CharField(max_length=255, validators=[username_validator])
    domain = models.ForeignKey('MailDomain', on_delete=models.CASCADE, related_name="aliases")
    destination = models.EmailField()

    @property
    def source(self):
        return f"{self.name}@{self.domain.name}"

    def __str__(self):
        return f"{self.source} → {self.destination}"

    def get_absolute_url(self):
        return reverse('alias-detail', kwargs={'pk': self.pk})

    class Meta:
        db_table = 'mail_alias'
        ordering = ['name', 'domain__name']
        constraints = [
            models.UniqueConstraint(fields=['name', 'domain', 'destination'], name='alias_idx'),
        ]
