from re import compile

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def username_validator(value):
    user_pattern = compile(r'^[a-z][-_.a-z0-9]+$')
    if not user_pattern.match(value):
        raise ValidationError(
            _("%(value)s is not valid user, only lower-cased letters, digits, dash, underscore or dot are allowed."),
            params={'value': value},
        )
