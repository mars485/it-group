from django.conf import settings
def site_settings(request):
    return {"SITE_URL":settings.SITE_URL,"CONTACT_EMAIL":settings.CONTACT_EMAIL,"TELEGRAM_URL":settings.TELEGRAM_URL,"WHATSAPP_URL":settings.WHATSAPP_URL,"YANDEX_METRIKA_ID":settings.YANDEX_METRIKA_ID}
