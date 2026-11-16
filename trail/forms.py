from django import forms
from .models import Report


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ["condition", "note", "photo"]
        widgets = {
            "condition": forms.RadioSelect,
            "note": forms.TextInput(attrs={"placeholder": "Optional: describe what you see"}),
        }