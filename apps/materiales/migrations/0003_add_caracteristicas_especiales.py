# Generated by Django 4.2.20 on 2025-06-11 22:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0006_alter_movimientostock_options_and_more'),
        ('materiales', '0002_alter_categoriamaterial_tipo_categoria_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='material',
            name='requiere_manejo_especial',
            field=models.BooleanField(default=False, verbose_name='Requiere Manejo Especial'),
        ),
        migrations.AddField(
            model_name='material',
            name='requiere_refrigeracion',
            field=models.BooleanField(default=False, verbose_name='Requiere Refrigeración'),
        ),
        migrations.AlterField(
            model_name='material',
            name='proveedor_principal',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='materiales_principales', to='inventario.proveedor'),
        ),
        migrations.DeleteModel(
            name='Proveedor',
        ),
    ]
