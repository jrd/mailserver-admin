from django.db.models import Q
from django.forms.models import ModelForm
from django.urls import (
    reverse,
    reverse_lazy,
)
from django.views.generic import (
    DetailView,
    ListView,
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
from ..models import MailAlias


class AliasContextMixin(CommonContextMixin):
    extra_context = CommonContextMixin.extra_context | {
        'model_name': 'alias',
    }


class AliasListView(AliasContextMixin, SortMixin, LoginRequiredMixin, ListView):
    model = MailAlias
    default_sort = 'source'
    sort_mapping = {
        'source': ('name', 'domain__name'),
    }
    paginate_by = 10
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
                | Q(domain__name__icontains=search_query)
                | Q(destination__icontains=search_query)
            )
        return qs


class AliasView(AliasContextMixin, FieldsContextMixin, LoginRequiredMixin, DetailView):
    model = MailAlias
    context_object_name = 'alias'
    fields = ['name', 'domain', 'destination']


class AliasCreateForm(ModelForm):
    def __init__(self, *args, user, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        if not user.is_superuser:
            self.fields.pop('domain', None)

    def set_domain(self, alias):
        if not self.user.is_superuser:
            alias.domain = self.user.domain

    def save(self, commit=True):
        alias = super().save(commit=False)
        self.set_domain(alias)
        if commit:
            alias.save()
        return alias

    class Meta:
        model = MailAlias
        fields = ['name', 'domain', 'destination']


class AliasCreateView(AliasContextMixin, LoginRequiredMixin, CreateView):
    model = MailAlias
    form_class = AliasCreateForm
    template_name_suffix = '_create'
    success_url = reverse_lazy(f'{app_name}:alias-list')

    def get_form_kwargs(self):
        return super().get_form_kwargs() | {
            'user': self.request.user,
        }

    def get_success_url(self):
        if self.request.POST.get('again', '0') == '1':
            return reverse(f'{app_name}:alias-add')
        else:
            return reverse(f'{app_name}:alias-list')


class AliasEditForm(AliasCreateForm):
    pass


class AliasUpdateView(AliasCreateView, UpdateView):
    form_class = AliasEditForm
    template_name_suffix = '_edit'


class AliasDeleteView(AliasContextMixin, LoginRequiredMixin, DeleteView):
    model = MailAlias
    success_url = reverse_lazy(f'{app_name}:alias-list')
