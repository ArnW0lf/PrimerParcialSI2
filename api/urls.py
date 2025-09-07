from django.urls import path
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'api'

# Creamos un router
router = DefaultRouter()

# Registramos nuestras vistas con el router
router.register(r'unidades', views.UnidadHabitacionalViewSet)
router.register(r'residentes', views.ResidenteViewSet)
router.register(r'visitantes', views.VisitanteViewSet)
router.register(r'registros-acceso', views.RegistroAccesoViewSet)
router.register(r'vehiculos', views.VehiculoViewSet)

urlpatterns = [
    path('', include(router.urls)), # URLs del CRUD
    path('reconocer-acceso/', views.ReconocimientoFacialView.as_view(), name='reconocer-acceso'), # URL para la IA
    path('reconocer-vehiculo/', views.ReconocimientoVehiculoView.as_view(), name='reconocer-vehiculo'), # URL para OCR
]
