# yourapp/utils.py
import requests
from django.conf import settings
from django.core.exceptions import ValidationError


def validate_turnstile(token):
    resp = requests.post(
        "https://challenges.cloudflare.com/turnstile/v0/siteverify",
        data={"secret": settings.TURNSTILE_SECRET_KEY, "response": token},
        timeout=5,
    ).json()
    if not resp.get("success"):
        raise ValidationError("Human verification failed.")

    return resp
