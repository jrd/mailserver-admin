from django.contrib.auth.views import (
    LoginView,
    LogoutView,
)
from django.urls import path

from . import app_name  # noqa F401
from .forms import AuthenticationForm
from .views import (
    AliasCreateView,
    AliasDeleteView,
    AliasListView,
    AliasUpdateView,
    AliasView,
    DashboardView,
    DomainCreateView,
    DomainDeleteView,
    DomainListView,
    DomainUpdateView,
    DomainView,
    UserCreateView,
    UserDeleteView,
    UserListView,
    UserUpdateView,
    UserView,
)

urlpatterns = [
    path('', DashboardView.as_view(), name='index'),
    path('login', LoginView.as_view(
        authentication_form=AuthenticationForm,
        template_name=f'{app_name}/login.html',
    ), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('domains', DomainListView.as_view(), name='domains'),
    path('domain/add', DomainCreateView.as_view(), name='domain-add'),
    path('domain/<int:pk>', DomainView.as_view(), name='domain-detail'),
    path('domain/<int:pk>/update', DomainUpdateView.as_view(), name='domain-update'),
    path('domain/<int:pk>/delete', DomainDeleteView.as_view(), name='domain-delete'),
    path('users', UserListView.as_view(), name='users'),
    path('user/add', UserCreateView.as_view(), name='user-add'),
    path('user/<int:pk>', UserView.as_view(), name='user-detail'),
    path('user/<int:pk>/update', UserUpdateView.as_view(), name='user-update'),
    path('user/<int:pk>/delete', UserDeleteView.as_view(), name='user-delete'),
    path('aliases', AliasListView.as_view(), name='aliases'),
    path('alias/add', AliasCreateView.as_view(), name='alias-add'),
    path('alias/<int:pk>', AliasView.as_view(), name='alias-detail'),
    path('alias/<int:pk>/update', AliasUpdateView.as_view(), name='alias-update'),
    path('alias/<int:pk>/delete', AliasDeleteView.as_view(), name='alias-delete'),
]
