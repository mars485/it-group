from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models


class SiteSettings(models.Model):
    brand_name = models.CharField("Название бренда", max_length=120, default="IT GROUP")
    brand_tagline = models.CharField("Короткое описание", max_length=240, default="Сайты и цифровые решения для бизнеса")
    THEME_CHOICES = [("dark", "Тёмная"), ("light", "Светлая")]
    FONT_CHOICES = [
        ("dm_sans", "DM Sans + Manrope"),
        ("manrope", "Manrope"),
        ("inter", "Inter"),
        ("system", "Системный шрифт"),
        ("georgia", "Georgia"),
    ]
    FONT_SCALE_CHOICES = [(90, "Компактный · 90%"), (100, "Стандартный · 100%"), (110, "Крупный · 110%"), (120, "Очень крупный · 120%")]

    site_url = models.URLField("Публичный адрес сайта", blank=True, help_text="Например, https://karpiev.ru. Если пусто, используется SITE_URL из .env.")
    logo_icon = models.ImageField("Логотип-иконка", upload_to="branding/", blank=True, help_text="PNG, JPG или WebP до 2 МБ. Отображается в шапке, подвале и админке.")
    phone = models.CharField("Телефон", max_length=80, blank=True)
    email = models.EmailField("Email", blank=True)
    telegram_url = models.URLField("Ссылка на Telegram", blank=True)
    whatsapp_url = models.URLField("Ссылка на WhatsApp", blank=True)
    city = models.CharField("Город", max_length=120, blank=True)
    address = models.CharField("Адрес", max_length=240, blank=True)
    work_hours = models.CharField("График работы", max_length=160, blank=True)
    requisites = models.TextField("Реквизиты", blank=True)
    footer_text = models.CharField("Текст в подвале", max_length=300, blank=True, default="Сайты и цифровые решения, связанные с задачами бизнеса.")
    site_theme = models.CharField("Тема публичного сайта", max_length=5, choices=THEME_CHOICES, default="dark")
    font_family = models.CharField("Шрифт сайта", max_length=20, choices=FONT_CHOICES, default="dm_sans")
    font_scale = models.PositiveSmallIntegerField("Размер текста", choices=FONT_SCALE_CHOICES, default=100)
    light_background_color = models.CharField("Цвет фона светлой темы", max_length=7, default="#F7F9FC", validators=[RegexValidator(r"^#[0-9A-Fa-f]{6}$", "Укажите цвет в формате #RRGGBB")])
    primary_color = models.CharField("Основной акцентный цвет", max_length=7, default="#417CFF", validators=[RegexValidator(r"^#[0-9A-Fa-f]{6}$", "Укажите цвет в формате #RRGGBB")])
    secondary_color = models.CharField("Дополнительный акцентный цвет", max_length=7, default="#52D6DC", validators=[RegexValidator(r"^#[0-9A-Fa-f]{6}$", "Укажите цвет в формате #RRGGBB")])
    background_color = models.CharField("Цвет фона тёмной темы", max_length=7, default="#0A0D14", validators=[RegexValidator(r"^#[0-9A-Fa-f]{6}$", "Укажите цвет в формате #RRGGBB")])
    yandex_metrika_id = models.CharField("ID Яндекс Метрики", max_length=40, blank=True)
    notification_email = models.EmailField("Email для заявок", blank=True, help_text="Если пусто, используется контактный email или CONTACT_EMAIL из .env.")
    email_notifications_enabled = models.BooleanField("Отправлять заявки на email", default=True)
    smtp_host = models.CharField("SMTP-сервер", max_length=255, blank=True, help_text="Если пусто, используются настройки SMTP из .env.")
    smtp_port = models.PositiveIntegerField("SMTP-порт", default=587)
    smtp_use_tls = models.BooleanField("STARTTLS (обычно порт 587)", default=True)
    smtp_use_ssl = models.BooleanField("SSL (обычно порт 465)", default=False)
    smtp_user = models.CharField("SMTP-логин", max_length=255, blank=True)
    smtp_password = models.CharField("SMTP-пароль приложения", max_length=255, blank=True)
    smtp_from_email = models.EmailField("Адрес отправителя", blank=True)
    telegram_notifications_enabled = models.BooleanField("Отправлять заявки в Telegram", default=True)
    telegram_bot_token = models.CharField("Токен Telegram-бота", max_length=255, blank=True)
    telegram_chat_id = models.CharField("ID чата Telegram", max_length=80, blank=True)
    crm_webhook_url = models.URLField("Webhook CRM", blank=True, help_text="URL для передачи новых заявок. Если пусто, используется CRM_WEBHOOK_URL из .env.")
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Настройки сайта"
        verbose_name_plural = "Настройки сайта"

    def __str__(self):
        return "Общие настройки сайта"

    def clean(self):
        super().clean()
        if self.smtp_host and self.smtp_use_tls and self.smtp_use_ssl:
            raise ValidationError("Для SMTP выберите только один режим: STARTTLS или SSL.")

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)


class PageContent(models.Model):
    PAGE_CHOICES = [(key, label) for key, label in [
        ("home", "Главная"), ("services", "Услуги"), ("development", "Разработка сайтов"),
        ("real_estate", "Сайты для агентств недвижимости"), ("promotion", "Продвижение и реклама"),
        ("cases", "Кейсы"), ("about", "О студии"), ("contacts", "Контакты"), ("privacy", "Политика конфиденциальности"),
    ]]
    page = models.CharField("Страница", max_length=32, choices=PAGE_CHOICES, unique=True)
    title = models.CharField("SEO Title", max_length=180, blank=True)
    description = models.CharField("SEO Description", max_length=320, blank=True)
    content_html = models.TextField("Содержимое страницы (HTML)", blank=True, help_text="Необязательно. Если заполнить, это содержимое заменит стандартный макет выбранной страницы. Разрешён HTML; редактируйте только доверенным пользователям.")
    is_published = models.BooleanField("Страница опубликована", default=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Содержимое страницы"
        verbose_name_plural = "Страницы сайта"
        ordering = ["page"]

    def __str__(self):
        return self.get_page_display()


class NavigationItem(models.Model):
    label = models.CharField("Название пункта", max_length=80)
    url = models.CharField("Ссылка", max_length=240, help_text="Например: /uslugi/ или https://example.ru")
    order = models.PositiveSmallIntegerField("Порядок", default=0)
    is_visible = models.BooleanField("Показывать", default=True)

    class Meta:
        verbose_name = "Пункт меню"
        verbose_name_plural = "Меню сайта"
        ordering = ["order", "id"]

    def __str__(self):
        return self.label


class Service(models.Model):
    number = models.CharField("Номер", max_length=8, default="01")
    title = models.CharField("Услуга", max_length=140)
    text = models.TextField("Кому и какую задачу решает", blank=True)
    url = models.CharField("Ссылка", max_length=240, default="/uslugi/")
    order = models.PositiveSmallIntegerField("Порядок", default=0)
    is_visible = models.BooleanField("Показывать", default=True)

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class ProcessStep(models.Model):
    number = models.CharField("Номер", max_length=8, default="01")
    title = models.CharField("Этап", max_length=140)
    text = models.TextField("Описание", blank=True)
    order = models.PositiveSmallIntegerField("Порядок", default=0)
    is_visible = models.BooleanField("Показывать", default=True)

    class Meta:
        verbose_name = "Этап работы"
        verbose_name_plural = "Этапы работы"
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class FAQ(models.Model):
    question = models.CharField("Вопрос", max_length=240)
    answer = models.TextField("Ответ")
    order = models.PositiveSmallIntegerField("Порядок", default=0)
    is_visible = models.BooleanField("Показывать", default=True)

    class Meta:
        verbose_name = "Вопрос и ответ"
        verbose_name_plural = "Частые вопросы"
        ordering = ["order", "id"]

    def __str__(self):
        return self.question


class RealtyFeature(models.Model):
    number = models.CharField("Номер", max_length=8, default="01")
    title = models.CharField("Возможность", max_length=140)
    text = models.TextField("Описание", blank=True)
    order = models.PositiveSmallIntegerField("Порядок", default=0)
    is_visible = models.BooleanField("Показывать", default=True)

    class Meta:
        verbose_name = "Функция для недвижимости"
        verbose_name_plural = "Возможности для недвижимости"
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class PromotionItem(models.Model):
    number = models.CharField("Номер", max_length=8, default="01")
    title = models.CharField("Направление", max_length=140)
    text = models.TextField("Описание", blank=True)
    order = models.PositiveSmallIntegerField("Порядок", default=0)
    is_visible = models.BooleanField("Показывать", default=True)

    class Meta:
        verbose_name = "Услуга продвижения"
        verbose_name_plural = "Продвижение и реклама"
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class PricingPackage(models.Model):
    name = models.CharField("Пакет", max_length=100)
    audience = models.CharField("Кому подходит", max_length=240, blank=True)
    included = models.TextField("Что входит (каждый пункт с новой строки)", blank=True)
    timeline = models.CharField("Примерный срок", max_length=120, blank=True)
    price_note = models.CharField("Стоимость", max_length=160, default="Стоимость после оценки задачи")
    order = models.PositiveSmallIntegerField("Порядок", default=0)
    is_visible = models.BooleanField("Показывать", default=True)

    class Meta:
        verbose_name = "Пакет работ"
        verbose_name_plural = "Пакеты и тарифы"
        ordering = ["order", "id"]

    def __str__(self):
        return self.name


class CaseStudy(models.Model):
    name = models.CharField("Название проекта", max_length=160)
    niche = models.CharField("Ниша", max_length=120, blank=True)
    is_concept = models.BooleanField("Это концепт", default=True)
    task = models.TextField("Исходная задача", blank=True)
    work = models.TextField("Что сделано", blank=True)
    result = models.TextField("Результат", blank=True, help_text="Указывайте только подтверждённые результаты; можно оставить пустым.")
    technologies = models.CharField("Технологии", max_length=240, blank=True)
    project_url = models.URLField("Ссылка на проект", blank=True)
    image_url = models.URLField("URL изображения", blank=True)
    order = models.PositiveSmallIntegerField("Порядок", default=0)
    is_visible = models.BooleanField("Показывать", default=True)

    class Meta:
        verbose_name = "Кейс или концепт"
        verbose_name_plural = "Кейсы и концепты"
        ordering = ["order", "id"]

    def __str__(self):
        return self.name


class Lead(models.Model):
    PROJECT_CHOICES = [(x,x) for x in ["Новый сайт", "Редизайн", "Лендинг", "Продвижение", "Яндекс Директ", "SEO", "CRM и автоматизация", "Поддержка", "Другое"]]
    name = models.CharField("Имя", max_length=120)
    phone = models.CharField("Телефон", max_length=60)
    messenger = models.CharField("Telegram или WhatsApp", max_length=120, blank=True)
    company = models.CharField("Компания", max_length=160, blank=True)
    project_type = models.CharField("Тип проекта", max_length=80, choices=PROJECT_CHOICES, default="Новый сайт")
    description = models.TextField("Задача", blank=True)
    budget = models.CharField("Бюджет", max_length=80, blank=True)
    attachment = models.FileField("Файл", upload_to="lead-files/%Y/%m/", blank=True)
    source = models.CharField("Источник", max_length=500, blank=True)
    utm_source = models.CharField(max_length=160, blank=True)
    utm_medium = models.CharField(max_length=160, blank=True)
    utm_campaign = models.CharField(max_length=160, blank=True)
    utm_content = models.CharField(max_length=160, blank=True)
    utm_term = models.CharField(max_length=160, blank=True)
    created_at = models.DateTimeField("Создана", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"

    def __str__(self):
        return f"{self.name} — {self.project_type}"
