from django.conf import settings
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

from .. import app_name, __version__
from ..forms import AuthenticationForm

extra_context = {
    'webmail_url': settings.WEBMAIL_URL,
    'vendor_name': settings.VENDOR_NAME,
    'vendor_url': settings.VENDOR_URL,
    'version': '' if settings.HIDE_VERSION else __version__,
}


class CommonContextMixin(ContextMixin):
    extra_context = extra_context


class FieldsContextMixin():
    field_types = {
        model_fields.IntegerField: 'num',
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
            fields = [self.model._meta.get_field(field_name) for field_name in self.fields]
        else:
            fields = [f for f in self.model._meta.get_fields() if not f.is_relation]
        fields = {field.name: (getattr(ctx['object'], field.name), self._get_simple_type(field)) for field in fields}
        return ctx | {
            'fields': fields,
        }


class SortMixin():
    """
    default_sort will define the form field that will be sorted as default
    sort_mapping will map any form field name to one or more db fields
    sort.value, sort.name and sort.asc will be accessible from the template
    """
    def get_default_sort(self):
        if hasattr(self, 'default_sort'):
            return self.default_sort
        else:
            return ''

    def get_query_order_by(self):
        sort_name = self.sort.get('name', '')
        if sort_name:
            sort_mapping = getattr(self, 'sort_mapping', {})
            fields = sort_mapping.get(sort_name, sort_name)
            prefix = '' if self.sort.get('asc', True) else '-'
            if isinstance(fields, str):
                return f'{prefix}{fields}'
            else:
                return [f'{prefix}{field}' for field in fields]
        else:
            return []

    def get_ordering(self):
        sort_value = self.request.GET.get('sort', self.get_default_sort())
        self.sort = {
            'value': sort_value,
            'name': '',
            'asc': False,
        }
        if sort_value:
            if sort_value.startswith('-'):
                self.sort['name'] = sort_value[1:]
            else:
                self.sort['name'] = sort_value
                self.sort['asc'] = True
        order_by = self.get_query_order_by()
        return order_by

    def get_context_data(self, *args, **kwargs):
        return super().get_context_data(*args, **kwargs) | {
            'sort': self.sort,
        }


class LoginView(CommonContextMixin, OrigLoginView):
    authentication_form = AuthenticationForm
    template_name = f'{app_name}/login.html'


class LoginRequiredMixin(OrigLoginRequiredMixin):
    login_url = reverse_lazy(f'{app_name}:login')


class IndexView(View):
    def get(self, request):
        return redirect(reverse(f'{app_name}:domain-list'))
