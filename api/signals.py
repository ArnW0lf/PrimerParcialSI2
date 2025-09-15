from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Gasto, UnidadHabitacional

@receiver(pre_save, sender=Gasto)
def registrar_estado_anterior_pago(sender, instance, **kwargs):
    """
    Antes de guardar, si el Gasto ya existe, guardamos su estado 'pagado' anterior.
    Esto nos permite saber si el estado cambió de False a True.
    """
    if instance.pk:
        try:
            instance._estado_anterior_pagado = Gasto.objects.get(pk=instance.pk).pagado
        except Gasto.DoesNotExist:
            instance._estado_anterior_pagado = False

@receiver(post_save, sender=Gasto)
def actualizar_saldo_deudor_unidad(sender, instance, created, **kwargs):
    """
    Después de guardar un Gasto, actualiza el saldo deudor de la UnidadHabitacional.
    """
    unidad = instance.unidad
    # Si el gasto se acaba de crear y no está pagado, sumamos al saldo deudor.
    if created and not instance.pagado:
        unidad.saldo_deudor += instance.monto
    # Si el gasto se actualizó y cambió de 'no pagado' a 'pagado'.
    elif not created and instance.pagado and not getattr(instance, '_estado_anterior_pagado', False):
        unidad.saldo_deudor -= instance.monto
    
    unidad.save()
