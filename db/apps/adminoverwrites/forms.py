from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .utils import validate_turnstile


class AdminTurnstileAuthForm(AuthenticationForm):
    def clean(self):
        token = self.data.get("cf-turnstile-response")
        if not token:
            raise forms.ValidationError("Human verification failed.")

        validate_turnstile(token)

        return super().clean()
