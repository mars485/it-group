import json, time, urllib.request
from django.conf import settings
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET
from .forms import LeadForm
from .models import CaseStudy, FAQ, Lead, PageContent, PricingPackage, ProcessStep, PromotionItem, RealtyFeature, Service, SiteSettings
from .middleware import CampaignMiddleware

def _context(request, page_key=None, **extra):
    page_content = PageContent.objects.filter(page=page_key, is_published=True).first() if page_key else None
    if page_content:
        extra["title"] = page_content.title or extra.get("title")
        extra["description"] = page_content.description or extra.get("description")
    return {
        "canonical": settings.SITE_URL + request.path,
        "page_content": page_content,
        "services": Service.objects.filter(is_visible=True),
        "process": ProcessStep.objects.filter(is_visible=True),
        "faq": FAQ.objects.filter(is_visible=True),
        "realty_features": RealtyFeature.objects.filter(is_visible=True),
        "promotion_items": PromotionItem.objects.filter(is_visible=True),
        "pricing_packages": PricingPackage.objects.filter(is_visible=True),
        "case_studies": CaseStudy.objects.filter(is_visible=True),
        **extra,
    }
def _lead(request):
    if request.method == "POST":
        form = LeadForm(request.POST, request.FILES)
        started = request.session.get("form_started", 0)
        if form.is_valid() and not form.cleaned_data.get("website") and time.time() - started >= 3:
            lead = form.save(commit=False); lead.source = request.META.get("HTTP_REFERER", "")[:500]; lead.save()
            body = "\n".join([f"Имя: {lead.name}", f"Телефон: {lead.phone}", f"Мессенджер: {lead.messenger}", f"Компания: {lead.company}", f"Проект: {lead.project_type}", f"Бюджет: {lead.budget}", f"Задача: {lead.description}", f"Источник: {lead.source}", f"UTM: {lead.utm_source} / {lead.utm_medium} / {lead.utm_campaign}"])
            site_config = SiteSettings.objects.first()
            notification_email = site_config.email if site_config and site_config.email else settings.CONTACT_EMAIL
            if notification_email and not notification_email.startswith("["):
                message = EmailMessage(f"Заявка с сайта IT GROUP: {lead.project_type}", body, settings.DEFAULT_FROM_EMAIL, [notification_email])
                if lead.attachment: message.attach(lead.attachment.name.split("/")[-1], lead.attachment.read())
                try: message.send(fail_silently=True)
                except Exception: pass
            if settings.CRM_WEBHOOK_URL:
                try:
                    req = urllib.request.Request(settings.CRM_WEBHOOK_URL, data=json.dumps({"name":lead.name,"phone":lead.phone,"messenger":lead.messenger,"company":lead.company,"project_type":lead.project_type,"description":lead.description,"budget":lead.budget,"utm_source":lead.utm_source,"utm_medium":lead.utm_medium,"utm_campaign":lead.utm_campaign,"utm_content":lead.utm_content,"utm_term":lead.utm_term,"created_at":lead.created_at.isoformat()}).encode(), headers={"Content-Type":"application/json"}, method="POST")
                    urllib.request.urlopen(req, timeout=4).read()
                except Exception: pass
            return LeadForm(), True, {}
        if form.is_valid():
            form.add_error(None, "Пожалуйста, заполните форму и отправьте её ещё раз.")
        return form, False, form.errors
    request.session["form_started"] = time.time()
    initial = {key: request.session.get(f"campaign_{key}", "") for key in CampaignMiddleware.KEYS}
    return LeadForm(initial=initial), False, {}

def home(request):
    form, sent, errors = _lead(request) if request.method in ["GET", "POST"] else (LeadForm(),False,{})
    return render(request, "pages/home.html", _context(request, "home", title="Разработка сайтов и цифровых решений для бизнеса — IT GROUP", description="Разрабатываем сайты, настраиваем рекламу, аналитику и автоматизацию. Специализация — агентства недвижимости.", form=form, sent=sent, errors=errors))
def _page(request, template, title, description, page_key):
    form, sent, errors = _lead(request)
    return render(request, template, _context(request,page_key,title=title,description=description,form=form,sent=sent,errors=errors))
def services(request): return _page(request,"pages/services.html","Услуги веб-студии IT GROUP","Разработка сайтов, продвижение, Яндекс Директ, SEO, CRM, аналитика и техническая поддержка.","services")
def development(request): return _page(request,"pages/development.html","Разработка сайтов для бизнеса — IT GROUP","Корпоративные сайты, лендинги и интернет-магазины: от анализа и прототипа до запуска и поддержки.","development")
def real_estate(request): return _page(request,"pages/real_estate.html","Сайты для агентств недвижимости — IT GROUP","Каталог объектов, фильтры, карточки недвижимости, формы просмотра и интеграция с CRM.","real_estate")
def promotion(request): return _page(request,"pages/promotion.html","Продвижение сайтов и Яндекс Директ — IT GROUP","SEO, настройка Яндекс Директа, аналитика и улучшение обработки заявок.","promotion")
def cases(request): return _page(request,"pages/cases.html","Концепты и кейсы — IT GROUP","Раздел проектов IT GROUP. Реальные кейсы добавляются после согласования с клиентами.","cases")
def about(request): return _page(request,"pages/about.html","О студии IT GROUP","Веб-студия полного цикла для малого и среднего бизнеса по всей России.","about")
def contacts(request): return _page(request,"pages/contacts.html","Контакты IT GROUP","Обсудите разработку сайта, продвижение или цифровую систему продаж с IT GROUP.","contacts")
def privacy(request): return render(request,"pages/privacy.html",_context(request,"privacy",title="Политика конфиденциальности — IT GROUP",description="Политика обработки персональных данных сайта IT GROUP."))
def not_found(request, exception): return render(request,"404.html",_context(request,title="Страница не найдена — IT GROUP",description="Такой страницы нет."),status=404)
@require_GET
def robots(request): return HttpResponse(f"User-agent: *\nAllow: /\nSitemap: {settings.SITE_URL}/sitemap.xml\n",content_type="text/plain; charset=utf-8")
@require_GET
def sitemap(request):
    paths=["/","/uslugi/","/razrabotka-sajtov/","/sajty-dlya-agentstv-nedvizhimosti/","/prodvizhenie-i-reklama/","/kejsy/","/o-studii/","/kontakty/","/politika-konfidencialnosti/"]
    xml='<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f"<url><loc>{settings.SITE_URL}{p}</loc></url>" for p in paths)+'</urlset>'
    return HttpResponse(xml,content_type="application/xml; charset=utf-8")
