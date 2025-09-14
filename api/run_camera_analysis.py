import cv2
import time
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
import numpy as np

# Importamos la lógica de OCR y los modelos de la app 'api'
from api.ocr_logic import reconocer_placa
from api.models import RegistroAcceso

# --- CONFIGURACIÓN ---
VIDEO_SOURCE = "mi_video.mp4"  # 0 para la cámara web, o la ruta a un archivo de video "mi_video.mp4"
COOLDOWN_SECONDS = 30  # Tiempo en segundos para no registrar la misma placa repetidamente
# ---------------------


class Command(BaseCommand):
    help = 'Inicia el proceso de reconocimiento de placas a través de una cámara en tiempo real.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS(
            'Iniciando el sistema de vigilancia de placas...'))

        cap = cv2.VideoCapture(VIDEO_SOURCE)

        if not cap.isOpened():
            self.stdout.write(self.style.ERROR(
                f"Error: No se pudo abrir la fuente de video: {VIDEO_SOURCE}"))
            return

        # Diccionario para rastrear la última vez que se vio una placa
        last_seen_plates = {}

        while True:
            ret, frame = cap.read()
            if not ret:
                self.stdout.write(self.style.WARNING(
                    "Fin del video o error al leer el fotograma. Reiniciando captura..."))
                # Si es un archivo de video, termina. Si es una cámara, podría intentar reconectar.
                if isinstance(VIDEO_SOURCE, str):
                    break
                cap.release()
                cap = cv2.VideoCapture(VIDEO_SOURCE)
                continue

            # Llamamos a la función de reconocimiento que ya tenemos
            vehiculo_encontrado, placa_detectada = reconocer_placa(frame)

            if vehiculo_encontrado:
                current_time = time.time()
                placa = vehiculo_encontrado.placa

                # Comprobamos si la placa está en cooldown
                if placa not in last_seen_plates or (current_time - last_seen_plates[placa]) > COOLDOWN_SECONDS:
                    self.stdout.write(self.style.SUCCESS(
                        f"¡Acceso concedido! Vehículo con placa {placa} reconocido."))

                    # Guardar el frame como imagen en memoria
                    _, buffer = cv2.imencode('.jpg', frame)
                    image_content = ContentFile(
                        buffer.tobytes(), name=f'{placa}_{int(current_time)}.jpg')

                    # Crear el registro de acceso en la base de datos
                    RegistroAcceso.objects.create(
                        residente=vehiculo_encontrado.residente_asociado,
                        tipo='ENTRADA',
                        foto_capturada=image_content
                    )

                    # Actualizar el tiempo de la última vez que se vio la placa
                    last_seen_plates[placa] = current_time

            # Mostramos el video en una ventana (opcional)
            # Puedes comentar estas dos líneas si corres el script en un servidor sin pantalla
            cv2.imshow("Sistema de Vigilancia - Presiona 'q' para salir", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Liberar recursos al finalizar
        cap.release()
        cv2.destroyAllWindows()
        self.stdout.write(self.style.SUCCESS(
            'Sistema de vigilancia detenido.'))
