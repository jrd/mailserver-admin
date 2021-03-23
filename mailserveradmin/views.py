from datetime import date
from json import loads
from math import ceil

from Crypto.PublicKey import RSA
from django.contrib.auth.mixins import LoginRequiredMixin as OrigLoginRequiredMixin
from django.contrib.auth.views import LoginView as OrigLoginView
from django.contrib.auth.views import LogoutView  # noqa F401
from django.db.models import Q
from django.db.models import fields as model_fields
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import (
    reverse,
    reverse_lazy,
)
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import (
    DetailView,
    ListView,
    View,
)
from django.views.generic.base import ContextMixin
from django.views.generic.edit import (
    CreateView,
    DeleteView,
    UpdateView,
)

from . import app_name
from .forms import AuthenticationForm
from .models import (
    MailAlias,
    MailDomain,
    MailUser,
)

# ##############
# ### COMMON ###
# ##############

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


class NewPrivateKeyView(View):
    def get(self, request):
        private_key_pem = RSA.generate(2048).export_key().decode('ascii')
        return JsonResponse({'private_key_pem': private_key_pem})


@method_decorator(csrf_exempt, name='dispatch')
class DkimDnsRecordView(View):
    @classmethod
    def get_dns_record(cls, selector, private_key_pem):
        dns_record = ''
        if selector and private_key_pem:
            priv_key = RSA.import_key(private_key_pem)
            pub_key = ''.join(priv_key.public_key().export_key().decode('ascii').split('\n')[1:-1])
            dns_record = f'{selector}._domainkey 300 IN TXT "v=DKIM1; h=sha256; t=s; p='
            parts = 40
            dns_record += '"\n"'.join(
                pub_key[i * parts:(i + 1) * parts] for i in range(ceil(len(pub_key) / parts))
            ) + '"'
        return dns_record

    def post(self, request):
        req = loads(request.body.decode('utf8'))
        selector = req.get('selector', '')
        private_key_pem = req.get('private_key_pem', '')
        return JsonResponse({'dns_record': self.get_dns_record(selector, private_key_pem)})


# ##############
# ### DOMAIN ###
# ##############


class DomainContextMixin(CommonContextMixin):
    extra_context = extra_context | {
        'model_name': 'domain',
    }


class DomainListView(DomainContextMixin, LoginRequiredMixin, ListView):
    model = MailDomain
    paginate_by = 10
    context_object_name = 'domain_list'

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_superuser:
            assert(self.request.user.is_admin)
            qs = qs.filter(id=self.request.user.domain_id)
        search_query = self.request.GET.get('query', '').strip()
        if search_query:
            qs = qs.filter(name__icontains=search_query)
        return qs


class DomainView(DomainContextMixin, FieldsContextMixin, LoginRequiredMixin, DetailView):
    model = MailDomain
    context_object_name = 'domain'
    fields = ['name', 'dkim_enabled', 'dkim_selector', 'dkim_private_key']

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        selector = ctx['object'].dkim_selector
        private_key_pem = ctx['object'].dkim_private_key
        dns_record = DkimDnsRecordView.get_dns_record(selector, private_key_pem)
        return ctx | {
            'dns_record': dns_record,
        }


class DomainCreateView(DomainContextMixin, LoginRequiredMixin, CreateView):
    model = MailDomain
    template_name_suffix = '_create'
    success_url = reverse_lazy(f'{app_name}:domain-list')
    fields = ['name', 'dkim_enabled', 'dkim_selector', 'dkim_private_key']

    def get_form(self):
        form = super().get_form()
        form.fields['dkim_private_key'].widget.attrs['cols'] = 80
        form.fields['dkim_private_key'].widget.attrs['rows'] = 15
        return form

    def get_initial(self):
        selector = str(date.today().year)
        private_key_pem = RSA.generate(2048).export_key().decode('ascii')
        return {
            'dkim_enabled': True,
            'dkim_selector': selector,
            'dkim_private_key': private_key_pem,
        }

    def get_context_data(self):
        ctx = super().get_context_data()
        selector = ctx['form'].initial['dkim_selector']
        private_key_pem = ctx['form'].initial['dkim_private_key']
        dns_record = DkimDnsRecordView.get_dns_record(selector, private_key_pem)
        return ctx | {
            'dns_record': dns_record,
        }


class DomainUpdateView(DomainCreateView, UpdateView):
    template_name_suffix = '_edit'


class DomainDeleteView(DomainContextMixin, LoginRequiredMixin, DeleteView):
    model = MailDomain
    success_url = reverse_lazy(f'{app_name}:domain-list')


# ############
# ### USER ###
# ############


class UserListView(LoginRequiredMixin, ListView):
    model = MailUser
    paginate_by = 50
    context_object_name = 'user_list'

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_superuser:
            assert(self.request.user.is_admin)
            qs = qs.filter(domain=self.request.user.domain)
        search_query = self.request.GET.get('query', '').strip()
        if search_query:
            qs = qs.filter(
                Q(name__icontains=search_query)
                | Q(domain__icontains=search_query)
            )
        return qs


class UserView(LoginRequiredMixin, DetailView):
    model = MailUser
    context_object_name = 'user'


class UserCreateView(LoginRequiredMixin, CreateView):
    model = MailUser
    template_name_suffix = '_create'
    fields = ['name', 'domain', 'is_superuser', 'is_admin', 'send_only', 'quota']


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = MailUser
    template_name_suffix = '_edit'
    fields = ['name', 'domain', 'is_superuser', 'is_admin', 'send_only', 'quota']


class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = MailUser
    success_url = reverse_lazy('user-list')


# #############
# ### ALIAS ###
# #############


class AliasListView(LoginRequiredMixin, ListView):
    model = MailAlias
    paginate_by = 50
    context_object_name = 'alias_list'

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_superuser:
            assert(self.request.user.is_admin)
            qs = qs.filter(domain=self.request.user.domain)
        search_query = self.request.GET.get('query', '').strip()
        if search_query:
            qs = qs.filter(
                Q(name__icontains=search_query)
                | Q(domain__icontains=search_query)
                | Q(destination__icontains=search_query)
            )
        return qs


class AliasView(LoginRequiredMixin, DetailView):
    model = MailAlias
    context_object_name = 'alias'


class AliasCreateView(LoginRequiredMixin, CreateView):
    model = MailAlias
    template_name_suffix = '_create'
    fields = ['name', 'domain', 'destination']


class AliasUpdateView(LoginRequiredMixin, UpdateView):
    model = MailAlias
    template_name_suffix = '_edit'
    fields = ['name', 'domain', 'destination']


class AliasDeleteView(LoginRequiredMixin, DeleteView):
    model = MailAlias
    success_url = reverse_lazy('alias-list')
