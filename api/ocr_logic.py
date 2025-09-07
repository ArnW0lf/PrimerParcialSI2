import pytesseract
import cv2
import re
import os
from .models import Vehiculo

# Le indicamos a pytesseract dónde encontrar el ejecutable de Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def reconocer_placa(image):
    """
    Detecta una placa en la imagen, la recorta y extrae el texto con Tesseract.
    """
    # Convertir a escala de grises para mejorar la precisión de OCR
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Cargar el clasificador Haar para detectar placas
    # __file__ es la ruta de este archivo (ocr_logic.py)
    cascade_path = os.path.join(os.path.dirname(
        __file__), 'haarcascade_russian_plate_number.xml')
    plate_cascade = cv2.CascadeClassifier(cascade_path)

    # Detectar placas en la imagen
    plates = plate_cascade.detectMultiScale(
        gray_image, scaleFactor=1.1, minNeighbors=5)

    texto_extraido = ""
    # Iterar sobre las placas detectadas (normalmente será una)
    for (x, y, w, h) in plates:
        # Recortar la imagen para obtener solo la placa
        plate_image = gray_image[y:y+h, x:x+w]

        # Usar Tesseract para extraer texto de la placa recortada
        # El config '--psm 8' asume que la imagen es una sola palabra.
        texto_extraido = pytesseract.image_to_string(
            plate_image, config='--psm 8')

        # Si encontramos texto, salimos del bucle
        if texto_extraido:
            break

    # Limpiar el texto: eliminar caracteres no alfanuméricos y convertir a mayúsculas
    placa_limpia = re.sub(r'[^A-Z0-9]', '', texto_extraido).upper()

    # Buscar el vehículo en la base de datos
    vehiculo = Vehiculo.objects.filter(placa=placa_limpia).first()

    return vehiculo, placa_limpia
