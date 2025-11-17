from django.conf import settings
from django.contrib.admin import AdminSite

from db.apps.adminoverwrites.forms import AdminTurnstileAuthForm


class MyAdminSite(AdminSite):
    login_form = AdminTurnstileAuthForm
    login_template = 'admin/custom_login.html'

    def each_context(self, request):
        ctx = super().each_context(request)
        ctx['TURNSTILE_SITE_KEY'] = settings.TURNSTILE_SITE_KEY
        return ctx


custom_site = MyAdminSite()
