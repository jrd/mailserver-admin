from .common import (
    IndexView,
    LoginView,
    LogoutView,
)
from .domain import (
    DkimDnsRecordView,
    DomainCreateView,
    DomainDeleteView,
    DomainListView,
    DomainUpdateView,
    DomainView,
    NewPrivateKeyView,
)
from .user import (
    UserCreateView,
    UserDeleteView,
    UserListView,
    UserUpdateView,
    UserView,
)
from .alias import (
    AliasCreateView,
    AliasDeleteView,
    AliasListView,
    AliasUpdateView,
    AliasView,
)
__all__ = [
    'AliasCreateView',
    'AliasDeleteView',
    'AliasListView',
    'AliasUpdateView',
    'AliasView',
    'DkimDnsRecordView',
    'DomainCreateView',
    'DomainDeleteView',
    'DomainListView',
    'DomainUpdateView',
    'DomainView',
    'IndexView',
    'LoginView',
    'LogoutView',
    'NewPrivateKeyView',
    'UserCreateView',
    'UserDeleteView',
    'UserListView',
    'UserUpdateView',
    'UserView',
]
