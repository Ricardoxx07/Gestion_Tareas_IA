from models.tarea import Tarea
from repository.tarea_repository import TareaRepository

class TareaService:

    def __init__(self, repository: TareaRepository):
        self.repository = repository
        #Recibe la lista de cargar_tareas almacenada en la memoria RAM, a partir de esto tareas es una lista normal de Python
        #que ahora vive en la memoria RAM del Service. Esta lista simplemente contiene los objetos que ya leyó en cargar_tareas()
        self.tareas = repository.cargar_tareas()



    #Aquí se utiliza typeHiting para los parámetros de las funciones.
    def agregar_tarea(self, nombre: str) -> None:

        # nueva_tarea se guarda en la RAM
        #Por que nueva_tarea = Tarea(nombre), porque el programa trabaja con objetos y al hacer self.tareas.append(nombre)
        #ocurriría un error porque tareas.append() trabaja con objetos no con variables simples, simplemente el programa no entendería
        #Y luego no serviría de nada guardar_tareas, porque guardar_tareas() necesita un objeto para convertirlo luego a diccionario.
        nueva_tarea = Tarea(nombre)
        
        #Agrega a la lista local en RAM
        self.tareas.append(nueva_tarea)
        
        #Envía la lista completa.
        self.repository.guardar_tareas(self.tareas)
    

    def listar_tareas(self) -> None:

        if not self.tareas:
            print("No existe ninguna tarea en su lista.")
            return

        print("Lista de tareas:")

        for indice, tarea in enumerate(self.tareas, start=1):

            estado = "✓" if tarea.completada else " "

            print(f"{indice}. [{estado}] {tarea.nombre}")
    
    def completar_tarea(self,numero_tarea: int) -> None:

        if not self.tareas:
            print("No existe ninguna tarea en su lista.")
            return
        

        if 1 <= numero_tarea <= len(self.tareas):
            self.tareas[numero_tarea - 1].completada = True
            print(f"Tarea número {numero_tarea} completada.")
            self.repository.guardar_tareas(self.tareas)
        else:
            print("Número de tarea inválido.")
        
        
    def eliminar_tarea(self, numero_tarea: int) -> None:

        if not self.tareas:
            print("No existe ninguna tarea en su lista.")
            return


        if 1 <= numero_tarea <= len(self.tareas):
            self.tareas.pop(numero_tarea - 1)
            print("Tarea eliminada correctamente.")
            self.repository.guardar_tareas(self.tareas)
        else:
            print("Número de tarea inválido.")
        