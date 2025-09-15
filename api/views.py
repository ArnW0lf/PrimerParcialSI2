from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
import numpy as np
import cv2

from .models import (
    UnidadHabitacional,
    Residente,
    Visitante,
    RegistroAcceso,
    Vehiculo,
    AreaComun,
    ReservaAreaComun,
    Gasto,
    Aviso
)
from .serializers import (
    UnidadHabitacionalSerializer,
    ResidenteSerializer,
    VisitanteSerializer,
    RegistroAccesoSerializer,
    VehiculoSerializer,
    AreaComunSerializer,
    ReservaAreaComunSerializer,
    GastoSerializer,
    AvisoSerializer
)


class UnidadHabitacionalViewSet(viewsets.ModelViewSet):
    queryset = UnidadHabitacional.objects.all()
    serializer_class = UnidadHabitacionalSerializer
    permission_classes = [IsAuthenticated] # <-- Añadir esta línea


class ResidenteViewSet(viewsets.ModelViewSet):
    queryset = Residente.objects.all()
    serializer_class = ResidenteSerializer
    permission_classes = [IsAuthenticated] # <-- Añadir esta línea


class VisitanteViewSet(viewsets.ModelViewSet):
    queryset = Visitante.objects.all()
    serializer_class = VisitanteSerializer
    permission_classes = [IsAuthenticated] # <-- Añadir esta línea


class VehiculoViewSet(viewsets.ModelViewSet):
    queryset = Vehiculo.objects.all()
    serializer_class = VehiculoSerializer
    permission_classes = [IsAuthenticated] # <-- Añadir esta línea


class RegistroAccesoViewSet(viewsets.ModelViewSet):
    queryset = RegistroAcceso.objects.all()
    serializer_class = RegistroAccesoSerializer
    permission_classes = [IsAuthenticated] # <-- Añadir esta línea


class AreaComunViewSet(viewsets.ModelViewSet):
    queryset = AreaComun.objects.all()
    serializer_class = AreaComunSerializer
    permission_classes = [IsAuthenticated]


class ReservaAreaComunViewSet(viewsets.ModelViewSet):
    queryset = ReservaAreaComun.objects.all()
    serializer_class = ReservaAreaComunSerializer
    permission_classes = [IsAuthenticated]


class GastoViewSet(viewsets.ModelViewSet):
    queryset = Gasto.objects.all()
    serializer_class = GastoSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='generar-expensas')
    def generar_expensas(self, request):
        """
        Genera los gastos de expensas mensuales para todas las unidades habitacionales.
        Espera un JSON con 'monto', 'descripcion' y 'dias_vencimiento'.
        Ej: {"monto": 100.50, "descripcion": "Expensas Mes de Julio", "dias_vencimiento": 15}
        """
        from datetime import date, timedelta

        monto = request.data.get('monto')
        descripcion = request.data.get('descripcion')
        dias_vencimiento = request.data.get('dias_vencimiento')

        if not all([monto, descripcion, dias_vencimiento]):
            return Response(
                {"error": "Faltan los parámetros 'monto', 'descripcion' o 'dias_vencimiento'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        unidades = UnidadHabitacional.objects.all()
        fecha_emision = date.today()
        fecha_vencimiento = fecha_emision + timedelta(days=int(dias_vencimiento))
        
        gastos_creados = []
        for unidad in unidades:
            gasto = Gasto.objects.create(
                unidad=unidad,
                monto=monto,
                descripcion=descripcion,
                fecha_vencimiento=fecha_vencimiento
            )
            gastos_creados.append(self.get_serializer(gasto).data)

        return Response(
            {"mensaje": f"Se generaron {len(gastos_creados)} gastos de expensas.", "gastos": gastos_creados},
            status=status.HTTP_201_CREATED
        )


class AvisoViewSet(viewsets.ModelViewSet):
    queryset = Aviso.objects.all()
    serializer_class = AvisoSerializer
    permission_classes = [IsAuthenticated] # <-- Añadir esta línea


class ReconocimientoFacialView(APIView):
    """
    Endpoint para recibir una imagen y realizar reconocimiento facial.
    """
    # Dejamos estos endpoints públicos por ahora, ya que serían usados por cámaras
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        # El archivo de imagen se espera en el campo 'image' del form-data
        file_obj = request.data.get('image')

        if not file_obj:
            return Response({"error": "No se proporcionó ninguna imagen."}, status=status.HTTP_400_BAD_REQUEST)

        # Convertir el archivo en un array de numpy que cv2/face_recognition pueda leer
        nparr = np.frombuffer(file_obj.read(), np.uint8)
        image_to_check = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image_to_check is None:
            return Response({"error": "El archivo proporcionado no es una imagen válida."}, status=status.HTTP_400_BAD_REQUEST)

        # Importación local para evitar conflictos de DLL en el arranque
        from .face_recognition_logic import reconocer_rostro
        try:
            residente_encontrado = reconocer_rostro(image_to_check)
        except IndexError:
            return Response({"error": "No se detectó ninguna cara en la imagen enviada."}, status=status.HTTP_400_BAD_REQUEST)

        if residente_encontrado:
            # Usamos el serializer para una respuesta más rica
            serializer = ResidenteSerializer(residente_encontrado)
            # Si se encuentra, creamos un registro de acceso
            RegistroAcceso.objects.create(
                residente=residente_encontrado, tipo='ENTRADA', foto_capturada=file_obj)
            return Response({
                "status": "Acceso concedido",
                "residente": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({"status": "Acceso denegado", "error": "Residente no reconocido."}, status=status.HTTP_403_FORBIDDEN)


class ReconocimientoVehiculoView(APIView):
    """
    Endpoint para recibir una imagen de un vehículo y reconocer su placa.
    """
    # Dejamos estos endpoints públicos por ahora, ya que serían usados por cámaras
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_obj = request.data.get('image')

        if not file_obj:
            return Response({"error": "No se proporcionó ninguna imagen."}, status=status.HTTP_400_BAD_REQUEST)

        nparr = np.frombuffer(file_obj.read(), np.uint8)
        image_to_check = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image_to_check is None:
            return Response({"error": "El archivo proporcionado no es una imagen válida."}, status=status.HTTP_400_BAD_REQUEST)

        # Importación local para evitar conflictos de DLL en el arranque
        from .ocr_logic import reconocer_placa
        vehiculo_encontrado, placa_detectada = reconocer_placa(image_to_check)

        if vehiculo_encontrado:
            # Si se encuentra, creamos un registro de acceso para el residente asociado
            RegistroAcceso.objects.create(
                residente=vehiculo_encontrado.residente_asociado, tipo='ENTRADA', foto_capturada=file_obj)
            serializer = VehiculoSerializer(vehiculo_encontrado)
            return Response({
                "status": "Acceso de vehículo concedido",
                "placa_detectada": placa_detectada,
                "vehiculo": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({"status": "Acceso de vehículo denegado", "placa_detectada": placa_detectada, "error": "Vehículo no registrado."}, status=status.HTTP_403_FORBIDDEN)
