from django import forms
from .models import ExpenditureInvoice


class ExpenditureInvoiceForm(forms.ModelForm):
    class Meta:
        model = ExpenditureInvoice
        fields = ['date', 'depositor_name', 'initial_balance']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

