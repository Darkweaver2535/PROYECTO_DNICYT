from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q  # ✅ AGREGAR ESTA IMPORTACIÓN
from .models import PerfilUsuario, ConfiguracionUsuario

class UsuarioCreateForm(UserCreationForm):
    """Formulario para crear nuevos usuarios"""
    
    email = forms.EmailField(
        required=True,
        label="Email",
        help_text="Correo electrónico único del usuario"
    )
    first_name = forms.CharField(
        max_length=30, 
        required=False, 
        label="Nombres"
    )
    last_name = forms.CharField(
        max_length=30, 
        required=False, 
        label="Apellidos"
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        
        labels = {
            'username': 'Nombre de Usuario',
        }
        
        help_texts = {
            'username': 'Requerido. 150 caracteres o menos. Únicamente letras, dígitos y @/./+/-/_ permitidos.',
        }
        
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'crear-usuario-form-control',
                'placeholder': 'Nombre de usuario único'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'crear-usuario-form-control',
                'placeholder': 'correo@empresa.com'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'crear-usuario-form-control',
                'placeholder': 'Nombres'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'crear-usuario-form-control',
                'placeholder': 'Apellidos'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Aplicar clases CSS a los campos de contraseña
        self.fields['password1'].widget.attrs.update({
            'class': 'crear-usuario-form-control',
            'placeholder': 'Contraseña segura'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'crear-usuario-form-control',
            'placeholder': 'Confirme la contraseña'
        })
        
        # Personalizar labels y help_text
        self.fields['password1'].label = "Contraseña"
        self.fields['password2'].label = "Confirmar Contraseña"
        self.fields['password1'].help_text = "Mínimo 8 caracteres, no muy común"
        self.fields['password2'].help_text = "Ingrese la misma contraseña"
        
        # Hacer email obligatorio
        self.fields['email'].required = True
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("Ya existe un usuario con este email.")
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and User.objects.filter(username=username).exists():
            raise forms.ValidationError("Ya existe un usuario con este nombre de usuario.")
        return username

class PerfilUsuarioForm(forms.ModelForm):
    """Formulario para el perfil extendido del usuario"""
    
    class Meta:
        model = PerfilUsuario
        fields = [
            'rol_sistema', 'area_trabajo', 'cargo', 'telefono', 
            'supervisor', 'fecha_ingreso', 'avatar', 'recibir_notificaciones'
        ]
        
        widgets = {
            'rol_sistema': forms.Select(attrs={
                'class': 'crear-usuario-form-select'
            }),
            'area_trabajo': forms.Select(attrs={
                'class': 'crear-usuario-form-select'
            }),
            'cargo': forms.TextInput(attrs={
                'class': 'crear-usuario-form-control',
                'placeholder': 'Cargo o puesto de trabajo'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'crear-usuario-form-control',
                'placeholder': '+591 XXXXXXXX'
            }),
            'supervisor': forms.Select(attrs={
                'class': 'crear-usuario-form-select'
            }),
            'fecha_ingreso': forms.DateInput(attrs={
                'class': 'crear-usuario-form-control',
                'type': 'date'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'crear-usuario-form-control',
                'accept': 'image/*'
            }),
            'recibir_notificaciones': forms.CheckboxInput(attrs={
                'class': 'crear-usuario-checkbox'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # ✅ FILTRAR SUPERVISORES CORRECTAMENTE - incluir superusuarios y admins
        # Primero, crear perfiles para usuarios que no los tengan
        from django.contrib.auth.models import User
        for user in User.objects.filter(is_active=True):
            PerfilUsuario.objects.get_or_create(user=user)
        
        # Ahora filtrar supervisores: superusuarios O administradores
        self.fields['supervisor'].queryset = User.objects.filter(
            is_active=True
        ).filter(
            Q(is_superuser=True) | Q(perfil__rol_sistema='administrador')
        ).order_by('first_name', 'last_name')
        
        self.fields['supervisor'].empty_label = "Sin supervisor asignado"
        
        # Hacer la fecha de ingreso por defecto hoy
        from django.utils import timezone
        if not self.instance.pk:  # Solo para nuevos perfiles
            self.fields['fecha_ingreso'].initial = timezone.now().date()

class UsuarioUpdateForm(forms.ModelForm):
    """Formulario para actualizar información básica del usuario"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'is_active']
        
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'crear-usuario-form-control'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'crear-usuario-form-control'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'crear-usuario-form-control'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'crear-usuario-checkbox'
            }),
        }

class CambiarPasswordForm(forms.Form):
    """Formulario para cambiar contraseña"""
    
    password_actual = forms.CharField(
        label="Contraseña Actual",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su contraseña actual'
        })
    )
    
    password_nueva = forms.CharField(
        label="Nueva Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nueva contraseña'
        }),
        min_length=8
    )
    
    password_confirmacion = forms.CharField(
        label="Confirmar Nueva Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme la nueva contraseña'
        })
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_password_actual(self):
        password_actual = self.cleaned_data.get('password_actual')
        if not self.user.check_password(password_actual):
            raise forms.ValidationError("La contraseña actual es incorrecta.")
        return password_actual
    
    def clean(self):
        cleaned_data = super().clean()
        password_nueva = cleaned_data.get('password_nueva')
        password_confirmacion = cleaned_data.get('password_confirmacion')
        
        if password_nueva and password_confirmacion:
            if password_nueva != password_confirmacion:
                raise forms.ValidationError("Las contraseñas nuevas no coinciden.")
        
        return cleaned_data

class ConfiguracionUsuarioForm(forms.ModelForm):
    """Formulario para configuraciones del usuario"""
    
    class Meta:
        model = ConfiguracionUsuario
        fields = [
            'tema', 'mostrar_ayuda', 'elementos_por_pagina',
            'notificar_mantenimiento', 'notificar_stock_bajo', 'notificar_fallas'
        ]
        
        widgets = {
            'tema': forms.Select(attrs={'class': 'form-select'}),
            'mostrar_ayuda': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'elementos_por_pagina': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 5,
                'max': 50
            }),
            'notificar_mantenimiento': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notificar_stock_bajo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notificar_fallas': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }