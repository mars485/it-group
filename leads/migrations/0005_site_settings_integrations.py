from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("leads", "0004_seed_cms_content")]

    operations = [
        migrations.AddField(model_name="sitesettings", name="site_url", field=models.URLField(blank=True, help_text="Например, https://karpiev.ru. Если пусто, используется SITE_URL из .env.", verbose_name="Публичный адрес сайта")),
        migrations.AddField(model_name="sitesettings", name="logo_icon", field=models.ImageField(blank=True, help_text="PNG, JPG или WebP до 2 МБ. Отображается в шапке, подвале и админке.", upload_to="branding/", verbose_name="Логотип-иконка")),
        migrations.AddField(model_name="sitesettings", name="notification_email", field=models.EmailField(blank=True, max_length=254, help_text="Если пусто, используется контактный email или CONTACT_EMAIL из .env.", verbose_name="Email для заявок")),
        migrations.AddField(model_name="sitesettings", name="email_notifications_enabled", field=models.BooleanField(default=True, verbose_name="Отправлять заявки на email")),
        migrations.AddField(model_name="sitesettings", name="smtp_host", field=models.CharField(blank=True, help_text="Если пусто, используются настройки SMTP из .env.", max_length=255, verbose_name="SMTP-сервер")),
        migrations.AddField(model_name="sitesettings", name="smtp_port", field=models.PositiveIntegerField(default=587, verbose_name="SMTP-порт")),
        migrations.AddField(model_name="sitesettings", name="smtp_use_tls", field=models.BooleanField(default=True, verbose_name="STARTTLS (обычно порт 587)")),
        migrations.AddField(model_name="sitesettings", name="smtp_use_ssl", field=models.BooleanField(default=False, verbose_name="SSL (обычно порт 465)")),
        migrations.AddField(model_name="sitesettings", name="smtp_user", field=models.CharField(blank=True, max_length=255, verbose_name="SMTP-логин")),
        migrations.AddField(model_name="sitesettings", name="smtp_password", field=models.CharField(blank=True, max_length=255, verbose_name="SMTP-пароль приложения")),
        migrations.AddField(model_name="sitesettings", name="smtp_from_email", field=models.EmailField(blank=True, max_length=254, verbose_name="Адрес отправителя")),
        migrations.AddField(model_name="sitesettings", name="telegram_notifications_enabled", field=models.BooleanField(default=True, verbose_name="Отправлять заявки в Telegram")),
        migrations.AddField(model_name="sitesettings", name="telegram_bot_token", field=models.CharField(blank=True, max_length=255, verbose_name="Токен Telegram-бота")),
        migrations.AddField(model_name="sitesettings", name="telegram_chat_id", field=models.CharField(blank=True, max_length=80, verbose_name="ID чата Telegram")),
        migrations.AddField(model_name="sitesettings", name="crm_webhook_url", field=models.URLField(blank=True, help_text="URL для передачи новых заявок. Если пусто, используется CRM_WEBHOOK_URL из .env.", verbose_name="Webhook CRM")),
    ]
