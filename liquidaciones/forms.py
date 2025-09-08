from django import forms
from django.forms import inlineformset_factory
from .models import Liquidacion, LiquidacionItem, Proveedor
from items.models import Item


class LiquidacionForm(forms.ModelForm):
    class Meta:
        model = Liquidacion
        exclude = ['procedencia']
        widgets = {
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cliente': forms.HiddenInput(),
            'numero_liquidacion': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_despacho': forms.TextInput(attrs={'class': 'form-control'}),
            'clase': forms.Select(attrs={'class': 'form-control'}),
            'numero_factura_comercial': forms.TextInput(attrs={'class': 'form-control'}),
            'partida_arancelaria': forms.TextInput(attrs={'class': 'form-control'}),
            'ad_valorem': forms.TextInput(attrs={'class': 'form-control'}),
            'valor_imponible': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'moneda_valor_imponible': forms.Select(attrs={'class': 'form-control'}),
            'equivalente_gs': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tipo_cambio': forms.TextInput(attrs={'class': 'form-control'}),
            'proveedor': forms.Select(attrs={
                'class': 'form-control',
                'data-live-search': 'true',
                'data-size': '5'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize proveedor queryset to show procedencia
        self.fields['proveedor'].queryset = Proveedor.objects.select_related('procedencia').all()
        # The label_from_instance method will be used for display
        self.fields['proveedor'].label_from_instance = self._proveedor_label
    
    def _proveedor_label(self, obj):
        """Custom label for proveedor with procedencia"""
        if obj.procedencia:
            return f"{obj.nombre} ({obj.procedencia.nombre})"
        else:
            return f"{obj.nombre} (Sin especificar)"


class LiquidacionItemForm(forms.ModelForm):
    class Meta:
        model = LiquidacionItem
        fields = ['item', 'monto', 'iva', 'retencion']
        widgets = {
            'item': forms.HiddenInput(),
            'monto': forms.TextInput(attrs={
                'class': 'form-control monto-input formatted-number', 
                'style': 'text-align:right', 
                'placeholder': '0',
                'data-original-value': ''
            }),
            'iva': forms.TextInput(attrs={
                'class': 'form-control iva-input formatted-number', 
                'style': 'text-align:right', 
                'placeholder': '0',
                'data-original-value': ''
            }),
            'retencion': forms.TextInput(attrs={
                'class': 'form-control retencion-input formatted-number', 
                'style': 'text-align:right', 
                'placeholder': '0',
                'data-original-value': ''
            }),
        }

    subtotal = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control subtotal-display formatted-number', 
                'style': 'text-align:right', 
                'readonly': True,
                'placeholder': '0'
            }), 
        label="Subtotal",
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['item'].queryset = Item.objects.all()
        
        # Make fields optional for formset validation
        self.fields['item'].required = False
        self.fields['retencion'].required = False
        
        # Initialize subtotal if instance exists
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.initial['subtotal'] = instance.subtotal


LiquidacionItemFormSet = inlineformset_factory(
    Liquidacion, 
    LiquidacionItem,
    form=LiquidacionItemForm,
    extra=0,  # No extra forms by default
    can_delete=True
)