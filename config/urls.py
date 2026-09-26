from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from leads import views
urlpatterns = [path("media/branding/<str:filename>", views.branding_image, name="branding_image"), path("admin/", admin.site.urls), path("", views.home, name="home"), path("uslugi/", views.services, name="services"), path("razrabotka-sajtov/", views.development, name="development"), path("sajty-dlya-agentstv-nedvizhimosti/", views.real_estate, name="real_estate"), path("prodvizhenie-i-reklama/", views.promotion, name="promotion"), path("kejsy/", views.cases, name="cases"), path("o-studii/", views.about, name="about"), path("kontakty/", views.contacts, name="contacts"), path("politika-konfidencialnosti/", views.privacy, name="privacy"), path("sitemap.xml", views.sitemap, name="sitemap"), path("robots.txt", views.robots, name="robots")]
handler404 = "leads.views.not_found"
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
