from rest_framework import serializers
from .models import UnidadHabitacional, Residente, Visitante, RegistroAcceso, Vehiculo


class UnidadHabitacionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadHabitacional
        fields = '__all__'


class VehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehiculo
        fields = '__all__'


class ResidenteSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Residente.
    """
    # Muestra el número de la unidad, no solo su ID.
    unidad_numero = serializers.CharField(
        source='unidad.numero', read_only=True)
    # Muestra una lista de las placas de los vehículos del residente.
    vehiculos = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Residente
        # Usamos una lista explícita para poder añadir los campos extra.
        fields = [
            'id', 'nombre', 'apellido', 'cedula', 'email', 'telefono',
            'foto_perfil', 'unidad', 'unidad_numero', 'vehiculos',
            'fecha_creacion', 'fecha_actualizacion'
        ]
        # El campo 'unidad' es de solo escritura al crear/actualizar,
        # mientras que 'unidad_numero' es de solo lectura para visualización.
        read_only_fields = ['unidad_numero', 'vehiculos']


class VisitanteSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Visitante.
    """
    autorizado_por_nombre = serializers.CharField(
        source='autorizado_por.__str__', read_only=True)

    class Meta:
        model = Visitante
        fields = '__all__'


class RegistroAccesoSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo RegistroAcceso.
    """
    # Muestra el nombre de la persona, no solo su ID.
    persona_nombre = serializers.CharField(source='__str__', read_only=True)

    class Meta:
        model = RegistroAcceso
        fields = '__all__'
        read_only_fields = ['persona_nombre']
