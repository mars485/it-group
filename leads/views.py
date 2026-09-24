import json, time, urllib.request
from django.conf import settings
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET
from .forms import LeadForm
from .models import Lead
from .middleware import CampaignMiddleware

SERVICES = [
 {"n":"01","title":"Корпоративные сайты","text":"Для компании, которой нужно понятно показать услуги и направления.","url":"/razrabotka-sajtov/"},
 {"n":"02","title":"Лендинги","text":"Для одного продукта, услуги или рекламной кампании.","url":"/razrabotka-sajtov/"},
 {"n":"03","title":"Интернет-магазины","text":"Каталог и заказ — с составом функций под ваш процесс.","url":"/uslugi/"},
 {"n":"04","title":"Сайты для агентств недвижимости","text":"Каталоги объектов, фильтры, просмотр и CRM-интеграции.","url":"/sajty-dlya-agentstv-nedvizhimosti/"},
 {"n":"05","title":"Редизайн и доработка","text":"Обновление визуальной подачи и улучшение существующего сайта.","url":"/razrabotka-sajtov/"},
 {"n":"06","title":"SEO-продвижение","text":"Техническая подготовка и развитие страниц под спрос.","url":"/prodvizhenie-i-reklama/"},
 {"n":"07","title":"Яндекс Директ","text":"Настройка рекламы и измерение обращений.","url":"/prodvizhenie-i-reklama/"},
 {"n":"08","title":"CRM и автоматизация","text":"Передача заявок, распределение и напоминания о контакте.","url":"/uslugi/"},
 {"n":"09","title":"Техническая поддержка","text":"Обновления, исправления и сопровождение сайта после запуска.","url":"/uslugi/"},
]
PROCESS = [("01","Знакомство и анализ","Уточняем задачу, аудиторию и текущую ситуацию."),("02","Исследование","Смотрим на конкурентов и сценарии выбора клиента."),("03","Структура и прототип","Согласуем страницы, содержание и путь пользователя."),("04","Дизайн","Создаём визуальное направление и макеты."),("05","Разработка","Собираем адаптивный сайт и подключаем формы."),("06","Интеграции","Настраиваем CRM, аналитику и рекламные инструменты по задаче."),("07","Тестирование","Проверяем формы, устройства, скорость и основные сценарии."),("08","Запуск и поддержка","Публикуем сайт, месяц вносим бесплатные правки и обсуждаем развитие.")]
FAQ = [("Сколько стоит разработка сайта?","Стоимость рассчитываем после обсуждения задачи, состава страниц и интеграций. На сайте нет фиксированных цен, потому что объём проектов отличается."),("Сколько времени занимает работа?","Срок зависит от состава страниц, готовности материалов и скорости согласований. Оценим его после первичного разбора."),("Можно ли доработать существующий сайт?","Да. Сначала посмотрим на текущую структуру, техническое состояние и цель доработки."),("Работаете ли вы с клиентами из других городов?","Да, работаем с компаниями по всей России в дистанционном формате."),("Можно ли продвигать сайт после запуска?","Да. Можно подключить SEO, Яндекс Директ, аналитику и дальнейшее развитие."),("Смогу ли я самостоятельно менять информацию?","Возможность самостоятельного редактирования зависит от выбранной платформы и согласуется на этапе планирования."),("Подключаете ли вы CRM и аналитику?","Да, если это нужно проекту. Состав интеграций и доступные сервисы уточняем заранее."),("Что потребуется от клиента?","Нужны вводные о компании, услугах и клиентах. Если материалов пока нет, определим список вместе."),("Как происходит оплата?","Порядок оплаты и этапы фиксируем в предложении и договоре, если он требуется."),("Есть ли поддержка после запуска?","Да. После запуска действует месяц бесплатных правок, далее можно обсудить долгосрочное сопровождение.")]
REALTY_FEATURES = [("01","Каталог объектов","Подбор объектов и удобные карточки недвижимости."),("02","Фильтры","Цена, район, комнаты и другие параметры по задаче."),("03","Просмотр","Формы записи на просмотр и быстрый контакт."),("04","Ипотечный калькулятор","Предварительный расчёт платежа для посетителя."),("05","CRM-интеграции","Передача заявки и автоматическое распределение."),("06","Аналитика","Учёт звонков, переходов и отправок форм."),("07","Чат-бот","Первичный подбор недвижимости по условиям клиента."),("08","SEO-страницы","Районы, жилые комплексы, услуги и направления."),("09","Сценарии продаж","Напоминания менеджерам о следующем контакте.")]
PROMOTION_ITEMS = [("01","SEO-продвижение","Техническая основа, структура и развитие страниц под интерес аудитории."),("02","Яндекс Директ","Настройка рекламных кампаний, целей и контроля обращений."),("03","Аналитика","Метрика, события, UTM-метки и источники заявок."),("04","Улучшение конверсии","Проверка предложений, форм и сценариев на сайте."),("05","Коллтрекинг","Подключение учёта звонков при выборе сервиса."),("06","Отчётность","Понятная сводка по обращениям и выполненным работам.")]
def _context(request, **extra):
    return {"canonical": settings.SITE_URL + request.path, "services":SERVICES,"process":PROCESS,"faq":FAQ,"realty_features":REALTY_FEATURES,"promotion_items":PROMOTION_ITEMS, **extra}
def _lead(request):
    if request.method == "POST":
        form = LeadForm(request.POST, request.FILES)
        started = request.session.get("form_started", 0)
        if form.is_valid() and not form.cleaned_data.get("website") and time.time() - started >= 3:
            lead = form.save(commit=False); lead.source = request.META.get("HTTP_REFERER", "")[:500]; lead.save()
            body = "\n".join([f"Имя: {lead.name}", f"Телефон: {lead.phone}", f"Мессенджер: {lead.messenger}", f"Компания: {lead.company}", f"Проект: {lead.project_type}", f"Бюджет: {lead.budget}", f"Задача: {lead.description}", f"Источник: {lead.source}", f"UTM: {lead.utm_source} / {lead.utm_medium} / {lead.utm_campaign}"])
            if settings.CONTACT_EMAIL and not settings.CONTACT_EMAIL.startswith("["):
                message = EmailMessage(f"Заявка с сайта IT GROUP: {lead.project_type}", body, settings.DEFAULT_FROM_EMAIL, [settings.CONTACT_EMAIL])
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
    return render(request, "pages/home.html", _context(request, title="Разработка сайтов и цифровых решений для бизнеса — IT GROUP", description="Разрабатываем сайты, настраиваем рекламу, аналитику и автоматизацию. Специализация — агентства недвижимости.", form=form, sent=sent, errors=errors))
def _page(request, template, title, description):
    form, sent, errors = _lead(request)
    return render(request, template, _context(request,title=title,description=description,form=form,sent=sent,errors=errors))
def services(request): return _page(request,"pages/services.html","Услуги веб-студии IT GROUP","Разработка сайтов, продвижение, Яндекс Директ, SEO, CRM, аналитика и техническая поддержка.")
def development(request): return _page(request,"pages/development.html","Разработка сайтов для бизнеса — IT GROUP","Корпоративные сайты, лендинги и интернет-магазины: от анализа и прототипа до запуска и поддержки.")
def real_estate(request): return _page(request,"pages/real_estate.html","Сайты для агентств недвижимости — IT GROUP","Каталог объектов, фильтры, карточки недвижимости, формы просмотра и интеграция с CRM.")
def promotion(request): return _page(request,"pages/promotion.html","Продвижение сайтов и Яндекс Директ — IT GROUP","SEO, настройка Яндекс Директа, аналитика и улучшение обработки заявок.")
def cases(request): return _page(request,"pages/cases.html","Концепты и кейсы — IT GROUP","Раздел проектов IT GROUP. Реальные кейсы добавляются после согласования с клиентами.")
def about(request): return _page(request,"pages/about.html","О студии IT GROUP","Веб-студия полного цикла для малого и среднего бизнеса по всей России.")
def contacts(request): return _page(request,"pages/contacts.html","Контакты IT GROUP","Обсудите разработку сайта, продвижение или цифровую систему продаж с IT GROUP.")
def privacy(request): return render(request,"pages/privacy.html",_context(request,title="Политика конфиденциальности — IT GROUP",description="Политика обработки персональных данных сайта IT GROUP."))
def not_found(request, exception): return render(request,"404.html",_context(request,title="Страница не найдена — IT GROUP",description="Такой страницы нет."),status=404)
@require_GET
def robots(request): return HttpResponse(f"User-agent: *\nAllow: /\nSitemap: {settings.SITE_URL}/sitemap.xml\n",content_type="text/plain; charset=utf-8")
@require_GET
def sitemap(request):
    paths=["/","/uslugi/","/razrabotka-sajtov/","/sajty-dlya-agentstv-nedvizhimosti/","/prodvizhenie-i-reklama/","/kejsy/","/o-studii/","/kontakty/","/politika-konfidencialnosti/"]
    xml='<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f"<url><loc>{settings.SITE_URL}{p}</loc></url>" for p in paths)+'</urlset>'
    return HttpResponse(xml,content_type="application/xml; charset=utf-8")
