from datetime import date
from json import loads
from math import ceil

from Crypto.PublicKey import RSA
from django.http import JsonResponse
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
from django.views.generic.edit import (
    CreateView,
    DeleteView,
    UpdateView,
)

from .common import (
    CommonContextMixin,
    FieldsContextMixin,
    LoginRequiredMixin,
    SortMixin,
)
from .. import app_name
from ..models import MailDomain


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


class DomainContextMixin(CommonContextMixin):
    extra_context = CommonContextMixin.extra_context | {
        'model_name': 'domain',
    }


class DomainListView(DomainContextMixin, SortMixin, LoginRequiredMixin, ListView):
    model = MailDomain
    default_sort = 'name'
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

    def get_success_url(self):
        if self.request.POST.get('again', '0') == '1':
            return reverse(f'{app_name}:domain-add')
        else:
            return reverse(f'{app_name}:domain-list')


class DomainUpdateView(DomainCreateView, UpdateView):
    template_name_suffix = '_edit'


class DomainDeleteView(DomainContextMixin, LoginRequiredMixin, DeleteView):
    model = MailDomain
    success_url = reverse_lazy(f'{app_name}:domain-list')
