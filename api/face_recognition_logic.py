import face_recognition
import numpy as np
from .models import Residente, RegistroAcceso

def get_residentes_encodings():
    """
    Obtiene los encodings faciales de todos los residentes registrados.
    """
    residentes = Residente.objects.filter(foto_perfil__isnull=False).exclude(foto_perfil__exact='')
    known_face_encodings = []
    known_face_ids = []

    for residente in residentes:
        try:
            # Carga la imagen del residente desde su ruta de archivo
            image = face_recognition.load_image_file(residente.foto_perfil.path)
            # Obtiene el encoding facial (asumimos una sola cara por foto)
            encoding = face_recognition.face_encodings(image)[0]
            known_face_encodings.append(encoding)
            known_face_ids.append(residente.id)
        except (FileNotFoundError, IndexError) as e:
            # Ignora residentes si su foto no existe o no se detecta una cara
            print(f"Error procesando la foto del residente {residente.id}: {e}")
            continue
            
    return known_face_encodings, known_face_ids

def reconocer_rostro(image_to_check):
    """
    Compara una imagen dada con las de los residentes registrados.
    """
    known_encodings, known_ids = get_residentes_encodings()

    if not known_encodings:
        return None # No hay residentes contra los que comparar

    unknown_encoding = face_recognition.face_encodings(image_to_check)[0]
    
    matches = face_recognition.compare_faces(known_encodings, unknown_encoding)
    
    if True in matches:
        first_match_index = matches.index(True)
        residente_id = known_ids[first_match_index]
        return Residente.objects.get(id=residente_id)

    return None # No se encontró ninguna coincidencia