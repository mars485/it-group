from django import forms
from django.contrib import admin

from .models import (
    CaseStudy, FAQ, Lead, NavigationItem, PageContent, ProcessStep,
    PromotionItem, RealtyFeature, Service, SiteSettings, PricingPackage,
)


admin.site.site_header = "IT GROUP · управление сайтом"
admin.site.site_title = "Панель IT GROUP"
admin.site.index_title = "Контент и заявки"
admin.site.site_url = "/"
admin.site.empty_value_display = "—"


class SiteSettingsAdminForm(forms.ModelForm):
    smtp_password = forms.CharField(
        label="SMTP-пароль приложения", required=False,
        widget=forms.PasswordInput(render_value=False),
        help_text="Оставьте пустым, чтобы сохранить текущий пароль.",
    )
    telegram_bot_token = forms.CharField(
        label="Токен Telegram-бота", required=False,
        widget=forms.PasswordInput(render_value=False),
        help_text="Оставьте пустым, чтобы сохранить текущий токен.",
    )
    clear_smtp_password = forms.BooleanField(label="Удалить сохранённый SMTP-пароль", required=False)
    clear_telegram_bot_token = forms.BooleanField(label="Удалить сохранённый токен бота", required=False)

    class Meta:
        model = SiteSettings
        fields = "__all__"

    def clean_smtp_password(self):
        return self.cleaned_data.get("smtp_password") or (self.instance.smtp_password if self.instance.pk else "")

    def clean_telegram_bot_token(self):
        return self.cleaned_data.get("telegram_bot_token") or (self.instance.telegram_bot_token if self.instance.pk else "")

    def clean_logo_icon(self):
        image = self.cleaned_data.get("logo_icon")
        if image and image.size > 2 * 1024 * 1024:
            raise forms.ValidationError("Логотип должен быть не больше 2 МБ.")
        return image

    def clean(self):
        data = super().clean()
        if data.get("clear_smtp_password"):
            data["smtp_password"] = ""
        if data.get("clear_telegram_bot_token"):
            data["telegram_bot_token"] = ""
        return data


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    form = SiteSettingsAdminForm
    fieldsets = (
        ("Бренд и адрес сайта", {"fields": ("brand_name", "brand_tagline", "site_url", "logo_icon", "footer_text")}),
        ("Контакты", {"fields": ("phone", "email", "telegram_url", "whatsapp_url", "city", "address", "work_hours", "requisites")}),
        ("Оформление публичного сайта", {"fields": ("site_theme", "font_family", "font_scale", "primary_color", "secondary_color", "background_color", "light_background_color")}),
        ("Аналитика", {"fields": ("yandex_metrika_id",)}),
        ("Заявки по email", {"fields": ("email_notifications_enabled", "notification_email", "smtp_host", "smtp_port", "smtp_use_tls", "smtp_use_ssl", "smtp_user", "smtp_password", "clear_smtp_password", "smtp_from_email")}),
        ("Заявки в Telegram", {"fields": ("telegram_notifications_enabled", "telegram_bot_token", "clear_telegram_bot_token", "telegram_chat_id")}),
        ("Интеграция с CRM", {"fields": ("crm_webhook_url",)}),
        ("Служебное", {"fields": ("updated_at",)}),
    )
    readonly_fields = ("updated_at",)

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser and not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(PageContent)
class PageContentAdmin(admin.ModelAdmin):
    list_display = ("page", "is_published", "updated_at")
    list_filter = ("is_published",)
    search_fields = ("title", "description", "content_html")
    readonly_fields = ("updated_at",)
    fieldsets = (
        ("Страница", {"fields": ("page", "is_published")} ),
        ("Поисковая выдача и соцсети", {"fields": ("title", "description")} ),
        ("Содержимое", {"fields": ("content_html",)}),
        ("Служебное", {"fields": ("updated_at",)}),
    )


@admin.register(NavigationItem)
class NavigationItemAdmin(admin.ModelAdmin):
    list_display = ("label", "url", "order", "is_visible")
    list_editable = ("order", "is_visible")
    ordering = ("order", "id")


class OrderedContentAdmin(admin.ModelAdmin):
    list_display = ("__str__", "order", "is_visible")
    list_editable = ("order", "is_visible")
    ordering = ("order", "id")
    search_fields = ("title", "text")


@admin.register(Service)
class ServiceAdmin(OrderedContentAdmin):
    list_display = ("title", "number", "url", "order", "is_visible")
    list_editable = ("order", "is_visible")
    search_fields = ("title", "text")
    fields = ("number", "title", "text", "url", "order", "is_visible")


@admin.register(ProcessStep)
class ProcessStepAdmin(OrderedContentAdmin):
    list_display = ("title", "number", "order", "is_visible")
    fields = ("number", "title", "text", "order", "is_visible")


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "order", "is_visible")
    list_editable = ("order", "is_visible")
    search_fields = ("question", "answer")
    ordering = ("order", "id")


@admin.register(RealtyFeature)
class RealtyFeatureAdmin(OrderedContentAdmin):
    list_display = ("title", "number", "order", "is_visible")
    fields = ("number", "title", "text", "order", "is_visible")


@admin.register(PromotionItem)
class PromotionItemAdmin(OrderedContentAdmin):
    list_display = ("title", "number", "order", "is_visible")
    fields = ("number", "title", "text", "order", "is_visible")


@admin.register(PricingPackage)
class PricingPackageAdmin(admin.ModelAdmin):
    list_display = ("name", "timeline", "price_note", "order", "is_visible")
    list_editable = ("order", "is_visible")
    ordering = ("order", "id")
    search_fields = ("name", "audience", "included")


@admin.register(CaseStudy)
class CaseStudyAdmin(admin.ModelAdmin):
    list_display = ("name", "niche", "is_concept", "order", "is_visible")
    list_filter = ("is_concept", "is_visible")
    list_editable = ("order", "is_visible")
    search_fields = ("name", "niche", "task", "work", "result")
    ordering = ("order", "id")


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "company", "project_type", "created_at")
    list_filter = ("project_type", "created_at")
    search_fields = ("name", "phone", "company", "description")
    readonly_fields = ("created_at", "source", "utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term")
