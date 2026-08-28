import json

from models.tarea import Tarea



class TareaRepository():

    def __init__(self, ruta_archivo="data/tareas.json"):
        self.ruta_archivo = ruta_archivo

    def cargar_tareas(self) -> list[Tarea]:
        try:
            with open(self.ruta_archivo, "r") as archivo:
                datos = json.load(archivo)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

        tareas = []

        for dato in datos:
            tarea = Tarea(
                id=dato["id"],
                nombre=dato["nombre"],
                completada=dato["completada"]
            )
            tareas.append(tarea)

        return tareas

    def guardar_tareas(self, lista_de_tareas: list[Tarea]) -> None:
        datos = []

        for tarea in lista_de_tareas:
            datos.append({
                "id": tarea.id,
                "nombre": tarea.nombre,
                "completada": tarea.completada
            })

        with open(self.ruta_archivo, "w") as archivo:
            json.dump(datos, archivo, indent=4)