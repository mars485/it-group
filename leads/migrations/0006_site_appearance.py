from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):
    dependencies = [("leads", "0005_site_settings_integrations")]

    operations = [
        migrations.AddField(model_name="sitesettings", name="site_theme", field=models.CharField(choices=[("dark", "Тёмная"), ("light", "Светлая")], default="dark", max_length=5, verbose_name="Тема публичного сайта")),
        migrations.AddField(model_name="sitesettings", name="font_family", field=models.CharField(choices=[("dm_sans", "DM Sans + Manrope"), ("manrope", "Manrope"), ("inter", "Inter"), ("system", "Системный шрифт"), ("georgia", "Georgia")], default="dm_sans", max_length=20, verbose_name="Шрифт сайта")),
        migrations.AddField(model_name="sitesettings", name="font_scale", field=models.PositiveSmallIntegerField(choices=[(90, "Компактный · 90%"), (100, "Стандартный · 100%"), (110, "Крупный · 110%"), (120, "Очень крупный · 120%")], default=100, verbose_name="Размер текста")),
        migrations.AddField(model_name="sitesettings", name="light_background_color", field=models.CharField(default="#F7F9FC", max_length=7, validators=[django.core.validators.RegexValidator("^#[0-9A-Fa-f]{6}$", "Укажите цвет в формате #RRGGBB")], verbose_name="Цвет фона светлой темы")),
        migrations.AlterField(model_name="sitesettings", name="background_color", field=models.CharField(default="#0A0D14", max_length=7, validators=[django.core.validators.RegexValidator("^#[0-9A-Fa-f]{6}$", "Укажите цвет в формате #RRGGBB")], verbose_name="Цвет фона тёмной темы")),
    ]
