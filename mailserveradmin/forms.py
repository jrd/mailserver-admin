from django.contrib.auth.forms import AuthenticationForm as OrigAuthenticationForm
from django.core.exceptions import ValidationError
from django.forms.fields import EmailField


class AuthenticationForm(OrigAuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super(OrigAuthenticationForm, self).__init__(*args, **kwargs)
        # Set the max length and label for the "username" field.
        self.username_field = EmailField(label="email", help_text="Email address")
        self.username_field.verbose_name = 'Email'
        username_max_length = 255
        self.fields['username'].max_length = username_max_length
        self.fields['username'].widget.attrs['maxlength'] = username_max_length
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'Email or username'
        self.fields['username'].label = 'Email'
        self.fields['password'].widget.attrs['class'] = 'form-control'
        self.fields['password'].widget.attrs['placeholder'] = 'Password'

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not (user.is_admin or user.is_superuser):
            raise ValidationError(
                "Not a administrator user",
                code='not_admin',
            )
