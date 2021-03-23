from django.contrib.auth.mixins import LoginRequiredMixin as OrigLoginRequiredMixin
from django.contrib.auth.views import LoginView as OrigLoginView
from django.contrib.auth.views import LogoutView  # noqa F401
from django.db.models import fields as model_fields
from django.shortcuts import redirect
from django.urls import (
    reverse,
    reverse_lazy,
)
from django.views.generic import View
from django.views.generic.base import ContextMixin

from .. import app_name
from ..forms import AuthenticationForm

extra_context = {
    'webmail_url': 'https://webmail.enialis.net',
    'vendor_name': "Sources on Github",
    'vendor_url': 'https://github.com/jrd/mailserver-admin',
}


class CommonContextMixin(ContextMixin):
    extra_context = extra_context


class FieldsContextMixin():
    field_types = {
        model_fields.IntegerField: 'int',
        model_fields.BooleanField: 'bool',
        model_fields.TextField: 'textarea',
        model_fields.CharField: 'str',
    }

    def _get_simple_type(self, field):
        for field_type, simple_type in self.field_types.items():
            if isinstance(field, field_type):
                return simple_type
        else:
            return 'str'

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        if hasattr(self, 'fields'):
            fields = [f for f in self.model._meta.get_fields() if f.name in self.fields]
        else:
            fields = [f for f in self.model._meta.get_fields() if not f.is_relation]
        fields = {field.name: (getattr(ctx['object'], field.name), self._get_simple_type(field)) for field in fields}
        return ctx | {
            'fields': fields,
        }


class LoginView(CommonContextMixin, OrigLoginView):
    authentication_form = AuthenticationForm
    template_name = f'{app_name}/login.html'


class LoginRequiredMixin(OrigLoginRequiredMixin):
    login_url = reverse_lazy(f'{app_name}:login')


class IndexView(View):
    def get(self, request):
        return redirect(reverse(f'{app_name}:domain-list'))
