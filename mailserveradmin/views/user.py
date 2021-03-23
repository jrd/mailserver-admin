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
)
from .. import app_name
from ..models import MailUser


class UserContextMixin(CommonContextMixin):
    extra_context = CommonContextMixin.extra_context | {
        'model_name': 'user',
    }


class UserListView(UserContextMixin, LoginRequiredMixin, ListView):
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
                | Q(domain__name__icontains=search_query)
            )
        return qs


class UserView(UserContextMixin, FieldsContextMixin, LoginRequiredMixin, DetailView):
    model = MailUser
    context_object_name = 'user'
    fields = ['name', 'domain', 'is_active', 'is_admin', 'is_superuser', 'send_only', 'quota']


class UserCreateView(UserContextMixin, LoginRequiredMixin, CreateView):
    model = MailUser
    template_name_suffix = '_create'
    success_url = reverse_lazy(f'{app_name}:user-list')
    fields = ['name', 'domain', 'is_active', 'is_admin', 'is_superuser', 'send_only', 'quota']


class UserUpdateView(UserCreateView, UpdateView):
    template_name_suffix = '_edit'


class UserDeleteView(UserContextMixin, LoginRequiredMixin, DeleteView):
    model = MailUser
    success_url = reverse_lazy(f'{app_name}:user-list')
