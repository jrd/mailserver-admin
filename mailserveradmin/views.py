from django.urls import reverse_lazy
from django.views.generic import (
    DetailView,
    ListView,
    TemplateView,
)
from django.views.generic.edit import (
    CreateView,
    DeleteView,
    UpdateView,
)

from . import app_name
# from django.contrib.auth.mixins import LoginRequiredMixin
from .models import (
    MailAlias,
    MailDomain,
    MailUser,
)


class DashboardView(TemplateView):
    template_name = f'{app_name}/dashboard.html'


# ##############
# ### DOMAIN ###
# ##############


class DomainListView(ListView):
    model = MailDomain
    paginate_by = 10
    context_object_name = 'domains'

    def get_queryset(self):
        qs = super().get_queryset()
        # if not self.request.user.is_superadmin:
        #     assert(self.request.user.is_admin)
        #     qs = qs.filter(id=self.request.user.domain_id)
        return qs


class DomainView(DetailView):
    model = MailDomain
    context_object_name = 'domain'


class DomainCreateView(CreateView):
    model = MailDomain
    fields = ['name', 'dkim_enabled', 'dkim_selector', 'dkim_private_key']


class DomainUpdateView(UpdateView):
    model = MailDomain
    fields = ['name', 'dkim_enabled', 'dkim_selector', 'dkim_private_key']


class DomainDeleteView(DeleteView):
    model = MailDomain
    success_url = reverse_lazy('domains')


# ############
# ### USER ###
# ############


class UserListView(ListView):
    model = MailUser
    paginate_by = 50
    context_object_name = 'users'

    def get_queryset(self):
        qs = super().get_queryset()
        # if not self.request.user.is_superadmin:
        #     assert(self.request.user.is_admin)
        #     qs = qs.filter(domain=self.request.user.domain)
        return qs


class UserView(DetailView):
    model = MailUser
    context_object_name = 'user'


class UserCreateView(CreateView):
    model = MailUser
    fields = ['name', 'domain', 'is_superuser', 'is_admin', 'send_only', 'quota']


class UserUpdateView(UpdateView):
    model = MailUser
    fields = ['name', 'domain', 'is_superuser', 'is_admin', 'send_only', 'quota']


class UserDeleteView(DeleteView):
    model = MailUser
    success_url = reverse_lazy('users')


# #############
# ### ALIAS ###
# #############


class AliasListView(ListView):
    model = MailAlias
    paginate_by = 50
    context_object_name = 'aliases'

    def get_queryset(self):
        qs = super().get_queryset()
        # if not self.request.user.is_superadmin:
        #     assert(self.request.user.is_admin)
        #     qs = qs.filter(domain=self.request.user.domain)
        return qs


class AliasView(DetailView):
    model = MailAlias
    context_object_name = 'alias'


class AliasCreateView(CreateView):
    model = MailAlias
    fields = ['name', 'domain', 'destination']


class AliasUpdateView(UpdateView):
    model = MailAlias
    fields = ['name', 'domain', 'destination']


class AliasDeleteView(DeleteView):
    model = MailAlias
    success_url = reverse_lazy('aliases')
