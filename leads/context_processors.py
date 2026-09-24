from django.conf import settings
from .models import NavigationItem, SiteSettings


def site_settings(request):
    config = SiteSettings.objects.first()
    phone = config.phone if config and config.phone else "[УКАЗАТЬ ТЕЛЕФОН]"
    email = config.email if config and config.email else settings.CONTACT_EMAIL
    navigation = NavigationItem.objects.filter(is_visible=True)
    return {
        "SITE_URL": settings.SITE_URL,
        "site_config": config,
        "site_brand": config.brand_name if config else "IT GROUP",
        "site_tagline": config.brand_tagline if config else "Сайты и цифровые решения для бизнеса",
        "site_footer_text": config.footer_text if config else "Сайты и цифровые решения, связанные с задачами бизнеса.",
        "site_phone": phone,
        "site_phone_link": "tel:" + "".join(x for x in phone if x.isdigit() or x == "+") if phone and not phone.startswith("[") else "",
        "CONTACT_EMAIL": email,
        "TELEGRAM_URL": config.telegram_url if config and config.telegram_url else settings.TELEGRAM_URL,
        "WHATSAPP_URL": config.whatsapp_url if config and config.whatsapp_url else settings.WHATSAPP_URL,
        "YANDEX_METRIKA_ID": config.yandex_metrika_id if config and config.yandex_metrika_id else settings.YANDEX_METRIKA_ID,
        "site_navigation": navigation,
        "site_primary_color": config.primary_color if config else "#417CFF",
        "site_secondary_color": config.secondary_color if config else "#52D6DC",
        "site_background_color": config.background_color if config else "#0A0D14",
    }
