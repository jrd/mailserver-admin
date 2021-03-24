from django.db.models import Q
from django.urls import reverse_lazy
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
                | Q(domain__name__icontains=search_query)
                | Q(destination__icontains=search_query)
            )
        return qs


class AliasView(AliasContextMixin, FieldsContextMixin, LoginRequiredMixin, DetailView):
    model = MailAlias
    context_object_name = 'alias'
    fields = ['name', 'domain', 'destination']


class AliasCreateView(AliasContextMixin, LoginRequiredMixin, CreateView):
    model = MailAlias
    template_name_suffix = '_create'
    success_url = reverse_lazy(f'{app_name}:alias-list')
    fields = ['name', 'domain', 'destination']


class AliasUpdateView(AliasCreateView, UpdateView):
    template_name_suffix = '_edit'


class AliasDeleteView(AliasContextMixin, LoginRequiredMixin, DeleteView):
    model = MailAlias
    success_url = reverse_lazy(f'{app_name}:alias-list')
