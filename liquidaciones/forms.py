from django import forms
from django.forms import inlineformset_factory
from .models import Liquidacion, LiquidacionItem, Proveedor, Pago, Banco, Procedencia, PlanillaGastos, PlanillaGastosItem
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
            'planilla_gastos': forms.HiddenInput(),
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


class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['liquidacion', 'banco', 'fecha', 'monto', 'referencia', 'concepto']
        widgets = {
            'liquidacion': forms.HiddenInput(),
            'banco': forms.Select(attrs={'class': 'form-control'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'monto': forms.TextInput(attrs={
                'class': 'form-control formatted-number', 
                'style': 'text-align:right'
            }),
            'referencia': forms.TextInput(attrs={'class': 'form-control'}),
            'concepto': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['banco'].queryset = Banco.objects.all()
        self.fields['referencia'].required = False
        self.fields['concepto'].required = False


class BancoForm(forms.ModelForm):
    class Meta:
        model = Banco
        fields = ['nombre', 'titular', 'numero_cuenta']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre del banco'
            }),
            'titular': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el titular de la cuenta'
            }),
            'numero_cuenta': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el número de cuenta'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nombre'].label = 'Nombre del Banco'
        self.fields['titular'].label = 'Titular de la Cuenta'
        self.fields['numero_cuenta'].label = 'Número de Cuenta'


class ProcedenciaForm(forms.ModelForm):
    class Meta:
        model = Procedencia
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre del país/procedencia'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nombre'].label = 'Nombre'


class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'procedencia']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre del proveedor'
            }),
            'procedencia': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nombre'].label = 'Nombre del Proveedor'
        self.fields['procedencia'].label = 'Procedencia'
        self.fields['procedencia'].required = False
        self.fields['procedencia'].queryset = Procedencia.objects.all().order_by('nombre')


class PlanillaGastosForm(forms.ModelForm):
    class Meta:
        model = PlanillaGastos
        fields = ['fecha', 'numero_planilla']
        widgets = {
            'fecha': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'numero_planilla': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el número de planilla'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha'].label = 'Fecha'
        self.fields['numero_planilla'].label = 'Número de Planilla'


class PlanillaGastosItemForm(forms.ModelForm):
    class Meta:
        model = PlanillaGastosItem
        fields = ['descripcion', 'monto']
        widgets = {
            'descripcion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción del gasto'
            }),
            'monto': forms.TextInput(attrs={
                'class': 'form-control formatted-number',
                'style': 'text-align:right',
                'placeholder': '0',
                'data-original-value': ''
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['descripcion'].label = 'Descripción'
        self.fields['monto'].label = 'Monto'
        
        # Make fields optional for formset validation
        self.fields['descripcion'].required = False
        self.fields['monto'].required = False
        
    
    def clean_monto(self):
        monto = self.cleaned_data.get('monto')
        
        if isinstance(monto, str) and monto.strip():
            # Handle both Paraguay formatting and plain numbers
            cleaned_monto = monto.strip()
            
            # If it contains dots and/or commas, assume Paraguay format
            if '.' in cleaned_monto or ',' in cleaned_monto:
                # Remove Paraguay formatting (dots for thousands, comma for decimal)
                cleaned_monto = cleaned_monto.replace('.', '').replace(',', '.')
            
            try:
                from decimal import Decimal
                return Decimal(cleaned_monto)
            except (ValueError, TypeError):
                raise forms.ValidationError('Ingrese un monto válido')
        elif monto == '' or monto is None:
            from decimal import Decimal
            return Decimal('0')
        
        return monto


PlanillaGastosItemFormSet = inlineformset_factory(
    PlanillaGastos,
    PlanillaGastosItem,
    form=PlanillaGastosItemForm,
    extra=0,  # No extra forms by default
    can_delete=True
)