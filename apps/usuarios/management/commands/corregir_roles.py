from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.usuarios.models import PerfilUsuario

class Command(BaseCommand):
    help = 'Corrige los roles de usuarios basándose en sus permisos'

    def handle(self, *args, **options):
        usuarios_corregidos = 0
        
        for user in User.objects.all():
            perfil, created = PerfilUsuario.objects.get_or_create(user=user)
            
            # Determinar el rol correcto
            rol_correcto = 'administrador' if (user.is_superuser or user.username == 'admin') else 'operario'
            
            if perfil.rol_sistema != rol_correcto:
                perfil.rol_sistema = rol_correcto
                perfil.save()
                usuarios_corregidos += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ {user.username} -> {rol_correcto.upper()}')
                )
            else:
                self.stdout.write(f'✓ {user.username} ya tiene el rol correcto: {rol_correcto}')
        
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 {usuarios_corregidos} usuarios corregidos')
        )