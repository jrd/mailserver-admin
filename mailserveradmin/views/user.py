from django.core.exceptions import ValidationError
from django.db.models import Q
from django.forms.fields import CharField
from django.forms.models import ModelForm
from django.forms.widgets import PasswordInput
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

    @staticmethod
    def static_clean(self):
        cleaned_data = super(type(self), self).clean()
        if not cleaned_data['domain'] and not cleaned_data['is_superuser']:
            self.add_error('domain', ValidationError('Domain required when not super admin', code='domain_required'))
        pwd = cleaned_data.get('password')
        pwd2 = cleaned_data.get('password2')
        if pwd and pwd2 and pwd != pwd2:
            self.add_error('password2', ValidationError('Passwords mismatch', code='mismatch'))
        return cleaned_data

    def clean(self):
        return self.static_clean(self)

    @staticmethod
    def static_save(self, commit):
        user = super(type(self), self).save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

    def save(self, commit=True):
        return self.static_save(self, commit)

    class Meta:
        model = MailUser
        fields = ['name', 'domain',
                  'password', 'password2',
                  'is_active', 'is_admin', 'is_superuser', 'send_only', 'quota']


class UserCreateView(UserContextMixin, LoginRequiredMixin, CreateView):
    model = MailUser
    form_class = UserCreateForm
    template_name_suffix = '_create'
    success_url = reverse_lazy(f'{app_name}:user-list')


class UserEditForm(ModelForm):
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

    def clean(self):
        return UserCreateForm.static_clean(self)

    def save(self, commit=True):
        if self.cleaned_data.get('password'):
            return UserCreateForm.static_save(self, commit)
        else:
            return super().save(commit=commit)

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
