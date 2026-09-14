from models.descomposicion_tarea import DescomposicionTarea, Subtarea
from services.descomposicion_tarea_service import DescomposicionTareaService


class ProveedorIAEspia:
    def __init__(self, respuesta: DescomposicionTarea):
        self.respuesta = respuesta
        self.texto_recibido: str | None = None

    def descomponer_tarea(self, texto: str) -> DescomposicionTarea:
        self.texto_recibido = texto
        return self.respuesta


def test_delega_la_descomposicion_y_conserva_la_tarea_original():
    proveedor = ProveedorIAEspia(
        DescomposicionTarea(
            tarea_original="Texto alterado por el proveedor",
            subtareas=[
                Subtarea(1, "Investigar requisitos", "Define qué se debe construir."),
                Subtarea(2, "Implementar solución", "Convierte los requisitos en trabajo."),
            ],
        )
    )
    service = DescomposicionTareaService(proveedor)

    resultado = service.descomponer_tarea("Construir integración con IA")

    assert proveedor.texto_recibido == "Construir integración con IA"
    assert resultado.tarea_original == "Construir integración con IA"
    assert [subtarea.orden for subtarea in resultado.subtareas] == [1, 2]
