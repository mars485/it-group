from django.contrib import admin

from .models import (
    CaseStudy, FAQ, Lead, NavigationItem, PageContent, ProcessStep,
    PromotionItem, RealtyFeature, Service, SiteSettings, PricingPackage,
)


admin.site.site_header = "IT GROUP · управление сайтом"
admin.site.site_title = "Панель IT GROUP"
admin.site.index_title = "Контент и заявки"
admin.site.site_url = "/"\nadmin.site.empty_value_display = "—"


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Бренд", {"fields": ("brand_name", "brand_tagline", "footer_text")} ),
        ("Контакты", {"fields": ("phone", "email", "telegram_url", "whatsapp_url", "city", "address", "work_hours", "requisites")} ),
        ("Оформление", {"fields": ("primary_color", "secondary_color", "background_color")} ),
        ("Аналитика", {"fields": ("yandex_metrika_id",)}),
        ("Служебное", {"fields": ("updated_at",)}),
    )
    readonly_fields = ("updated_at",)

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

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
