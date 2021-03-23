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

from .common import LoginRequiredMixin
from ..models import MailAlias


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
                | Q(domain__name__icontains=search_query)
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
