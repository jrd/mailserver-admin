from django.contrib.auth.mixins import LoginRequiredMixin as OrigLoginRequiredMixin
from django.contrib.auth.views import LoginView as OrigLoginView
from django.contrib.auth.views import LogoutView  # noqa F401
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect
from django.views.generic import (
    DetailView,
    ListView,
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


class LoginView(CommonContextMixin, OrigLoginView):
    authentication_form = AuthenticationForm
    template_name = f'{app_name}/login.html'


class LoginRequiredMixin(OrigLoginRequiredMixin):
    login_url = reverse_lazy(f'{app_name}:login')


def index_view(request):
    return redirect(reverse(f'{app_name}:domain-list'))


# ##############
# ### DOMAIN ###
# ##############


class DomainListView(CommonContextMixin, LoginRequiredMixin, ListView):
    model = MailDomain
    paginate_by = 10
    context_object_name = 'domain_list'
    extra_context = extra_context | {
        'model_name': 'domain',
        'title': 'Domains',
    }

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_superuser:
            assert(self.request.user.is_admin)
            qs = qs.filter(id=self.request.user.domain_id)
        return qs


class DomainView(LoginRequiredMixin, DetailView):
    model = MailDomain
    context_object_name = 'domain'


class DomainCreateView(LoginRequiredMixin, CreateView):
    model = MailDomain
    fields = ['name', 'dkim_enabled', 'dkim_selector', 'dkim_private_key']


class DomainUpdateView(LoginRequiredMixin, UpdateView):
    model = MailDomain
    fields = ['name', 'dkim_enabled', 'dkim_selector', 'dkim_private_key']


class DomainDeleteView(LoginRequiredMixin, DeleteView):
    model = MailDomain
    success_url = reverse_lazy('domain-list')


# ############
# ### USER ###
# ############


class UserListView(LoginRequiredMixin, ListView):
    model = MailUser
    paginate_by = 50
    context_object_name = 'user_list'

    def get_queryset(self):
        qs = super().get_queryset()
        # if not self.request.user.is_superadmin:
        #     assert(self.request.user.is_admin)
        #     qs = qs.filter(domain=self.request.user.domain)
        return qs


class UserView(LoginRequiredMixin, DetailView):
    model = MailUser
    context_object_name = 'user'


class UserCreateView(LoginRequiredMixin, CreateView):
    model = MailUser
    fields = ['name', 'domain', 'is_superuser', 'is_admin', 'send_only', 'quota']


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = MailUser
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
        # if not self.request.user.is_superadmin:
        #     assert(self.request.user.is_admin)
        #     qs = qs.filter(domain=self.request.user.domain)
        return qs


class AliasView(LoginRequiredMixin, DetailView):
    model = MailAlias
    context_object_name = 'alias'


class AliasCreateView(LoginRequiredMixin, CreateView):
    model = MailAlias
    fields = ['name', 'domain', 'destination']


class AliasUpdateView(LoginRequiredMixin, UpdateView):
    model = MailAlias
    fields = ['name', 'domain', 'destination']


class AliasDeleteView(LoginRequiredMixin, DeleteView):
    model = MailAlias
    success_url = reverse_lazy('alias-list')
