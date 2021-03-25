from django.core.exceptions import ValidationError
from django.db.models import Q
from django.forms.fields import CharField
from django.forms.models import ModelForm
from django.forms.widgets import PasswordInput
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
from ..models import MailUser


class UserContextMixin(CommonContextMixin):
    extra_context = CommonContextMixin.extra_context | {
        'model_name': 'user',
    }


class UserListView(UserContextMixin, SortMixin, LoginRequiredMixin, ListView):
    model = MailUser
    default_sort = 'email'
    sort_mapping = {
        'email': ('name', 'domain__name'),
        'enabled': 'is_active',
        'admin': 'is_admin',
        'superadmin': 'is_superuser',
    }
    paginate_by = 10
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


class UserCreateForm(ModelForm):
    password = CharField(
        max_length=255, label="Password",
        widget=PasswordInput(attrs={
            'autocomplete': "new-password",
            'placeholder': "Choose a complex password",
        }),
    )
    password2 = CharField(
        max_length=255, label="Confirm password",
        widget=PasswordInput(attrs={
            'autocomplete': "new-password",
            'placeholder': "Repeat password",
        }),
    )

    def __init__(self, *args, user, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        if not user.is_superuser:
            self.fields.pop('domain', None)

    def clean(self):
        cleaned_data = super().clean()
        if self.user.is_superuser and not cleaned_data['is_superuser'] and not cleaned_data['domain']:
            self.add_error('domain', ValidationError('Domain required when not super admin', code='domain_required'))
        pwd = cleaned_data.get('password')
        pwd2 = cleaned_data.get('password2')
        if pwd and pwd2 and pwd != pwd2:
            self.add_error('password2', ValidationError('Passwords mismatch', code='mismatch'))
        return cleaned_data

    def set_domain(self, user):
        if not self.user.is_superuser:
            user.domain = self.user.domain

    def set_password(self, user):
        user.set_password(self.cleaned_data['password'])

    def save(self, commit=True):
        user = super().save(commit=False)
        self.set_domain(user)
        self.set_password(user)
        if commit:
            user.save()
        return user

    class Meta:
        model = MailUser
        fields = ['name', 'domain',
                  'password', 'password2',
                  'is_active', 'is_admin', 'is_superuser', 'send_only', 'quota']


class UserCreateView(UserContextMixin, LoginRequiredMixin, CreateView):
    model = MailUser
    form_class = UserCreateForm
    template_name_suffix = '_create'

    def get_form_kwargs(self):
        return super().get_form_kwargs() | {
            'user': self.request.user,
        }

    def get_success_url(self):
        if self.request.POST.get('again', '0') == '1':
            return reverse(f'{app_name}:user-add')
        else:
            return reverse(f'{app_name}:user-list')


class UserEditForm(UserCreateForm):
    password = CharField(
        max_length=255, required=False, label="New password",
        widget=PasswordInput(attrs={
            'autocomplete': "new-password",
            'placeholder': "Empty to keep password",
        })
    )
    password2 = CharField(
        max_length=255, required=False, label="Confirm password",
        widget=PasswordInput(attrs={
            'autocomplete': "new-password",
            'placeholder': "Repeat password",
        }),
    )

    def set_password(self, user):
        if self.cleaned_data.get('password'):
            super().set_password(user)

    class Meta:
        model = MailUser
        fields = ['name', 'domain', 'is_active', 'is_admin', 'is_superuser', 'send_only', 'quota',
                  'password', 'password2']


class UserUpdateView(UserCreateView, UpdateView):
    form_class = UserEditForm
    template_name_suffix = '_edit'


class UserDeleteView(UserContextMixin, LoginRequiredMixin, DeleteView):
    model = MailUser
    success_url = reverse_lazy(f'{app_name}:user-list')
