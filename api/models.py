from django.db import models
import uuid

class UnidadHabitacional(models.Model):
    """Modelo para representar una casa, apartamento o unidad."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero = models.CharField(max_length=10, unique=True, help_text="Ej: A-101, Casa 25")
    propietario = models.CharField(max_length=200, help_text="Nombre del dueño legal")
    
    def __str__(self):
        return f"Unidad {self.numero}"

class Residente(models.Model):
    """Modelo para representar a los residentes del condominio."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(
        max_length=100, help_text="Nombre completo del residente")
    apellido = models.CharField(
        max_length=100, help_text="Apellido del residente")
    cedula = models.CharField(
        max_length=20, unique=True, help_text="Cédula de identidad")
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    foto_perfil = models.ImageField(
        upload_to='residentes/', help_text="Foto para reconocimiento facial")
    unidad = models.ForeignKey(UnidadHabitacional, on_delete=models.SET_NULL, null=True, blank=True, related_name='residentes')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class Visitante(models.Model):
    """Modelo para representar a los visitantes autorizados."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    cedula = models.CharField(max_length=20, unique=True)
    autorizado_por = models.ForeignKey(
        Residente, on_delete=models.CASCADE, related_name='visitantes_autorizados')
    fecha_visita = models.DateField()
    hora_entrada_prevista = models.TimeField(blank=True, null=True)
    hora_salida_prevista = models.TimeField(blank=True, null=True)
    foto_perfil = models.ImageField(
        upload_to='visitantes/', blank=True, null=True, help_text="Foto opcional para reconocimiento")

    def __str__(self):
        return f"Visitante: {self.nombre} {self.apellido} (Autorizado por: {self.autorizado_por.nombre})"


class RegistroAcceso(models.Model):
    """Modelo para registrar las entradas y salidas."""
    TIPO_ACCESO = [
        ('ENTRADA', 'Entrada'),
        ('SALIDA', 'Salida'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    residente = models.ForeignKey(
        Residente, on_delete=models.SET_NULL, null=True, blank=True)
    visitante = models.ForeignKey(
        Visitante, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(
        auto_now_add=True, help_text="Fecha y hora del evento")
    tipo = models.CharField(max_length=10, choices=TIPO_ACCESO)
    foto_capturada = models.ImageField(
        upload_to='capturas_acceso/', help_text="Foto capturada por la cámara en el momento del acceso")

    def __str__(self):
        persona = self.residente if self.residente else self.visitante
        return f"{self.tipo} de {persona} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

class Vehiculo(models.Model):
    """Modelo para representar los vehículos de los residentes."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    placa = models.CharField(max_length=10, unique=True)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    color = models.CharField(max_length=30)
    residente_asociado = models.ForeignKey(Residente, on_delete=models.CASCADE, related_name='vehiculos')

    def __str__(self):
        return f"{self.placa} ({self.marca} {self.modelo})"
