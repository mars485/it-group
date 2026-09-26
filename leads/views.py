import html, json, logging, mimetypes, time, urllib.request
from django.conf import settings
from django.core.mail import EmailMessage, get_connection
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET
from .forms import LeadForm
from .models import CaseStudy, FAQ, Lead, PageContent, PricingPackage, ProcessStep, PromotionItem, RealtyFeature, Service, SiteSettings
from .middleware import CampaignMiddleware

logger = logging.getLogger(__name__)

def _notify_telegram_lead(lead, site_config):
    if site_config and not site_config.telegram_notifications_enabled:
        return
    if site_config and (site_config.telegram_bot_token or site_config.telegram_chat_id):
        token, chat_id = site_config.telegram_bot_token, site_config.telegram_chat_id
    else:
        token, chat_id = settings.TELEGRAM_BOT_TOKEN, settings.TELEGRAM_CHAT_ID
    if not token or not chat_id:
        return

    def safe(value, limit=500):
        value = str(value or "—").strip()
        if len(value) > limit:
            value = value[:limit - 1] + "…"
        return html.escape(value)

    lines = [
        "<b>Новая заявка с сайта IT GROUP</b>",
        f"<b>Имя:</b> {safe(lead.name)}",
        f"<b>Телефон:</b> {safe(lead.phone)}",
        f"<b>Проект:</b> {safe(lead.project_type)}",
        f"<b>Мессенджер:</b> {safe(lead.messenger)}",
        f"<b>Компания:</b> {safe(lead.company)}",
        f"<b>Бюджет:</b> {safe(lead.budget)}",
        f"<b>Задача:</b> {safe(lead.description, 1600)}",
        f"<b>Источник:</b> {safe(lead.source, 450)}",
        f"<b>UTM:</b> {safe(' / '.join(filter(None, [lead.utm_source, lead.utm_medium, lead.utm_campaign])), 350)}",
    ]
    if lead.attachment:
        lines.append(f"<b>Приложен файл:</b> {safe(lead.attachment.name.split('/')[-1], 180)}")
    payload = {"chat_id": chat_id, "text": "\n".join(lines), "parse_mode": "HTML", "disable_web_page_preview": True}
    request = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=6) as response:
            result = json.loads(response.read().decode("utf-8"))
        if not result.get("ok"):
            logger.warning("Telegram lead notification was rejected by the API")
    except Exception as exc:
        logger.warning("Telegram lead notification failed (%s)", type(exc).__name__)

def _notify_email_lead(lead, site_config, body):
    if site_config and not site_config.email_notifications_enabled:
        return
    recipient = ((site_config.notification_email or site_config.email) if site_config else "") or settings.CONTACT_EMAIL
    if not recipient or recipient.startswith("["):
        return

    if site_config and site_config.smtp_host:
        host, port = site_config.smtp_host, site_config.smtp_port
        use_tls, use_ssl = site_config.smtp_use_tls, site_config.smtp_use_ssl
        username, password = site_config.smtp_user, site_config.smtp_password
        sender = site_config.smtp_from_email or username or settings.DEFAULT_FROM_EMAIL
    else:
        host, port = settings.EMAIL_HOST, settings.EMAIL_PORT
        use_tls, use_ssl = settings.EMAIL_USE_TLS, settings.EMAIL_USE_SSL
        username, password = settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD
        sender = settings.DEFAULT_FROM_EMAIL

    if not host:
        logger.warning("Lead email notification skipped: SMTP host is not configured")
        return
    if use_tls and use_ssl:
        logger.warning("Lead email notification skipped: both TLS and SSL are enabled")
        return
    try:
        connection = get_connection(
            "django.core.mail.backends.smtp.EmailBackend",
            host=host, port=port, username=username, password=password,
            use_tls=use_tls, use_ssl=use_ssl, timeout=10,
        )
        message = EmailMessage(
            f"Заявка с сайта IT GROUP: {lead.project_type}",
            body, sender, [recipient], connection=connection,
        )
        if lead.attachment:
            with lead.attachment.open("rb") as attached:
                message.attach(lead.attachment.name.split("/")[-1], attached.read())
        message.send(fail_silently=False)
    except Exception as exc:
        logger.warning("Lead email notification failed (%s)", type(exc).__name__)


def _site_url():
    config = SiteSettings.objects.first()
    return (config.site_url if config and config.site_url else settings.SITE_URL).rstrip("/")


@require_GET
def branding_image(request, filename):
    config = SiteSettings.objects.first()
    if not config or not config.logo_icon or config.logo_icon.name != f"branding/{filename}":
        raise Http404
    try:
        image = config.logo_icon.open("rb")
    except OSError:
        raise Http404 from None
    content_type = mimetypes.guess_type(config.logo_icon.name)[0] or "application/octet-stream"
    response = FileResponse(image, content_type=content_type)
    response["Cache-Control"] = "public, max-age=60"
    response["X-Content-Type-Options"] = "nosniff"
    return response


def _context(request, page_key=None, **extra):
    page_content = PageContent.objects.filter(page=page_key, is_published=True).first() if page_key else None
    if page_content:
        extra["title"] = page_content.title or extra.get("title")
        extra["description"] = page_content.description or extra.get("description")
    return {
        "canonical": _site_url() + request.path,
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
            _notify_email_lead(lead, site_config, body)
            _notify_telegram_lead(lead, site_config)
            crm_webhook_url = (site_config.crm_webhook_url if site_config and site_config.crm_webhook_url else settings.CRM_WEBHOOK_URL)
            if crm_webhook_url:
                try:
                    req = urllib.request.Request(crm_webhook_url, data=json.dumps({"name":lead.name,"phone":lead.phone,"messenger":lead.messenger,"company":lead.company,"project_type":lead.project_type,"description":lead.description,"budget":lead.budget,"utm_source":lead.utm_source,"utm_medium":lead.utm_medium,"utm_campaign":lead.utm_campaign,"utm_content":lead.utm_content,"utm_term":lead.utm_term,"created_at":lead.created_at.isoformat()}).encode(), headers={"Content-Type":"application/json"}, method="POST")
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
def robots(request): return HttpResponse(f"User-agent: *\nAllow: /\nSitemap: {_site_url()}/sitemap.xml\n",content_type="text/plain; charset=utf-8")
@require_GET
def sitemap(request):
    paths=["/","/uslugi/","/razrabotka-sajtov/","/sajty-dlya-agentstv-nedvizhimosti/","/prodvizhenie-i-reklama/","/kejsy/","/o-studii/","/kontakty/","/politika-konfidencialnosti/"]
    site_url = _site_url()
    xml='<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f"<url><loc>{site_url}{p}</loc></url>" for p in paths)+'</urlset>'
    return HttpResponse(xml,content_type="application/xml; charset=utf-8")
