from django.contrib import admin
from .models import (
    # ... (tus otras importaciones)
    Residente,
    Visitante,
    RegistroAcceso,
    UnidadHabitacional,
    Vehiculo,
    AreaComun,
    ReservaAreaComun,
    Gasto,
    Aviso
)


@admin.register(UnidadHabitacional)
class UnidadHabitacionalAdmin(admin.ModelAdmin):
    list_display = ('numero', 'propietario', 'saldo_deudor')
    search_fields = ('numero', 'propietario')


@admin.register(Residente)
class ResidenteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'cedula', 'unidad')
    search_fields = ('nombre', 'apellido', 'cedula')
    list_filter = ('unidad',)


@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):
    list_display = ('unidad', 'descripcion', 'monto',
                    'fecha_vencimiento', 'pagado')
    search_fields = ('descripcion', 'unidad__numero')
    list_filter = ('pagado', 'fecha_vencimiento', 'unidad')
    # Permite editar el estado 'pagado' desde la lista
    list_editable = ('pagado',)


@admin.register(ReservaAreaComun)
class ReservaAreaComunAdmin(admin.ModelAdmin):
    list_display = ('area_comun', 'residente', 'fecha_reserva',
                    'hora_inicio', 'hora_fin', 'pagado')
    list_filter = ('pagado', 'fecha_reserva', 'area_comun')


# Registramos los otros modelos de forma simple
admin.site.register(Visitante)
admin.site.register(RegistroAcceso)
admin.site.register(Vehiculo)
admin.site.register(AreaComun)
admin.site.register(Aviso)
