from django import forms
from .models import Cliente


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'ruc', 'email', 'numero_liquidacion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre del cliente'
            }),
            'ruc': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el RUC del cliente'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'ejemplo@correo.com'
            }),
            'numero_liquidacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de liquidación (opcional)'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = False
        self.fields['numero_liquidacion'].required = False
        
        # Add labels
        self.fields['nombre'].label = 'Nombre'
        self.fields['ruc'].label = 'RUC'
        self.fields['email'].label = 'Email'
        self.fields['numero_liquidacion'].label = 'Número de Liquidación'