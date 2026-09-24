from django.db import models
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
