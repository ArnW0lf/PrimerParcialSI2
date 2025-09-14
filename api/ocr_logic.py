import pytesseract
import cv2
import re
import os
from .models import Vehiculo

# Le indicamos a pytesseract dónde encontrar el ejecutable de Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Ancho y alto mínimo del contorno para ser considerado una placa
MIN_PLATE_WIDTH = 60
MIN_PLATE_HEIGHT = 15


def validar_formato_placa(texto):
    """
    Limpia y valida si el texto extraído podría ser una placa.
    Busca patrones comunes como 3-4 números seguidos de 3 letras.
    """
    # Limpiamos el texto de caracteres no alfanuméricos y lo ponemos en mayúsculas
    texto_limpio = re.sub(r'[^A-Z0-9]', '', texto.upper())

    # Un patrón simple: busca al menos 3 letras y 3 números.
    # Puedes hacerlo más estricto si conoces el formato exacto.
    # Ejemplo: re.compile(r'^\d{3,4}[A-Z]{3}$')
    if len(texto_limpio) >= 6 and len(re.findall(r'[A-Z]', texto_limpio)) >= 3 and len(re.findall(r'\d', texto_limpio)) >= 3:
        return texto_limpio
    return None


def reconocer_placa(image):
    """
    Procesa una imagen para detectar, leer y validar una placa de vehículo.
    """
    # 1. Pre-procesamiento de la imagen
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Filtro Gaussiano para reducir el ruido
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # Binarización adaptativa para manejar condiciones de iluminación variables
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)
    
    # Operaciones morfológicas para eliminar ruido y unir caracteres
    # Esto ayuda a que el contorno de la placa sea más sólido.
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    closing = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=1)

    # 2. Detección de contornos
    contornos, _ = cv2.findContours(
        closing, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # Variable para guardar las coordenadas del rectángulo de la placa detectada
    rect_placa = None
    placa_limpia = ""
    # Iterar sobre los contornos encontrados
    for c in contornos:
        # 3. Filtrado de contornos por tamaño y forma
        (x, y, w, h) = cv2.boundingRect(c)
        aspect_ratio = w / float(h)
        if w > MIN_PLATE_WIDTH and h > MIN_PLATE_HEIGHT and 2.5 < aspect_ratio < 5.0:
            # 4. Recorte de la posible placa (ROI - Region of Interest)
            roi = gray[y:y+h, x:x+w]

            # 5. OCR con Tesseract y configuración optimizada
            config = "-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 --psm 7"
            texto_extraido = pytesseract.image_to_string(roi, config=config)

            # 6. Validación del formato de la placa
            placa_validada = validar_formato_placa(texto_extraido)
            if placa_validada:
                placa_limpia = placa_validada
                rect_placa = (x, y, w, h) # Guardamos las coordenadas
                break  # Encontramos una placa válida, salimos del bucle

    # Buscar el vehículo en la base de datos
    vehiculo = Vehiculo.objects.filter(placa=placa_limpia).first()

    return vehiculo, placa_limpia, rect_placa
