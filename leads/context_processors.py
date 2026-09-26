from django.conf import settings
from django.templatetags.static import static
from .models import NavigationItem, SiteSettings


FONT_STACKS = {
    "dm_sans": ("'DM Sans', Arial, sans-serif", "'Manrope', 'DM Sans', Arial, sans-serif"),
    "manrope": ("'Manrope', Arial, sans-serif", "'Manrope', Arial, sans-serif"),
    "inter": ("'Inter', Arial, sans-serif", "'Inter', Arial, sans-serif"),
    "system": ("system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif", "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"),
    "georgia": ("Georgia, 'Times New Roman', serif", "Georgia, 'Times New Roman', serif"),
}


def site_settings(request):
    config = SiteSettings.objects.first()
    phone = config.phone if config and config.phone else "[УКАЗАТЬ ТЕЛЕФОН]"
    email = config.email if config and config.email else settings.CONTACT_EMAIL
    navigation = NavigationItem.objects.filter(is_visible=True)
    site_url = (config.site_url if config and config.site_url else settings.SITE_URL).rstrip("/")
    logo_url = config.logo_icon.url if config and config.logo_icon else static("graphics/it-group-lion.png")
    theme = config.site_theme if config else "dark"
    font, display = FONT_STACKS.get(config.font_family if config else "dm_sans", FONT_STACKS["dm_sans"])
    return {
        "SITE_URL": site_url,
        "site_theme": theme,
        "site_font_family": font,
        "site_display_family": display,
        "site_font_scale": (config.font_scale if config else 100) / 100,
        "site_logo_url": logo_url,
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
        "site_background_color": (config.light_background_color if config else "#F7F9FC") if theme == "light" else (config.background_color if config else "#0A0D14"),
    }
