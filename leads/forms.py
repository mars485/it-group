from django import forms
from django.core.validators import FileExtensionValidator
from .models import Lead
class LeadForm(forms.ModelForm):
    consent = forms.BooleanField(required=True, label="Согласен на обработку персональных данных по политике конфиденциальности")
    website = forms.CharField(required=False, widget=forms.HiddenInput())
    class Meta:
        model = Lead
        fields = ["name", "phone", "messenger", "company", "project_type", "description", "budget", "attachment", "utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term"]
        widgets = {"description": forms.Textarea(attrs={"rows": 4}), "attachment": forms.ClearableFileInput(attrs={"accept":".pdf,.doc,.docx,.jpg,.jpeg,.png,.zip"}), "utm_source": forms.HiddenInput(), "utm_medium": forms.HiddenInput(), "utm_campaign": forms.HiddenInput(), "utm_content": forms.HiddenInput(), "utm_term": forms.HiddenInput()}
        labels = {"name":"Имя", "phone":"Телефон", "messenger":"Telegram или WhatsApp", "company":"Название компании", "project_type":"Что нужно сделать?", "description":"Кратко о задаче", "budget":"Желаемый бюджет", "attachment":"Прикрепить файл"}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["attachment"].validators.append(FileExtensionValidator(["pdf", "doc", "docx", "jpg", "jpeg", "png", "zip"]))
    def clean_attachment(self):
        f = self.cleaned_data.get("attachment")
        if f and f.size > 8 * 1024 * 1024:
            raise forms.ValidationError("Файл должен быть не больше 8 МБ.")
        return f
