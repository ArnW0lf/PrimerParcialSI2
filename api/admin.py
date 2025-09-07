from django.contrib import admin
from .models import Residente, Visitante, RegistroAcceso, UnidadHabitacional, Vehiculo

# Register your models here.

admin.site.register(Residente)
admin.site.register(Visitante)
admin.site.register(RegistroAcceso)
admin.site.register(UnidadHabitacional)
admin.site.register(Vehiculo)
