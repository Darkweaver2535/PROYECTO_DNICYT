from django import forms
from .models import Equipo

class EquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = [
            'codigo_udb', 'codigo_interno', 'nombre', 'modelo', 'serie', 'fabricante', 'año_fabricacion',
            'potencia', 'capacidad', 'ubicacion_fisica', 'seccion', 'tipo_equipo', 'estado',
            'foto', 'responsable', 'observaciones'
        ]
        widgets = {
            'codigo_udb': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'EMI - LPZ\n1-22386\n2025',
                'class': 'form-control'
            }),
            # ...otros widgets...
        }