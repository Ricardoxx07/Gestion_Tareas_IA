import json
from models.tarea import Tarea

#Serialización (Guardar): Tienes una mesa montada en tu habitación (un objeto Tarea en la RAM).
#  Para guardarla en el trastero o enviarla por correo, la desarmas completamente, la metes en una caja plana y adjuntas 
# las instrucciones. La mesa ahora es solo un paquete de tablas y tornillos (un archivo JSON).
# CÓDIGO -> JSON

#Deserialización (Cargar): Abres la caja con los datos en el disco, sigues las instrucciones y vuelves a armar la mesa 
# real en tu habitación para poder usarla. Eso es lo que hizo tu código.
# JSON -> CÓDIGO

class TareaRepository:


    def __init__(self, ruta_archivo="data/tareas.json"):
        self.ruta_archivo = ruta_archivo

#Aquí devuelve una lista de tipo Tarea haciendo (Deserialización)
    def cargar_tareas(self) -> list[Tarea]:

    #Aquí abrimos el documento tareas.json para leer su contenido
        try:
            with open(self.ruta_archivo, "r") as archivo:
            # Lee el JSON desde el disco duro, lo carga en la memoria RAM como un objeto 
            # de Python (diccionario/lista) y guarda su referencia en 'datos' para usarlo en el código
                datos = json.load(archivo)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    #Se crea una lista vacía para que el documento json pueda transformarse a una lista mas adelante.
        tareas = []

    #El bucle for actúa como un traductor entre el mundo de JSON (diccionarios)
    #y el mundo de la Programación Orientada a Objetos (instancias de tu clase Tarea).
        for dato in datos:

        #tarea = Tarea(nombre=dato["nombre"], completada=dato["completada"])
        # Sacas los valores del diccionario usando sus llaves ("nombre" y "completada") 
        # y se los pasas al constructor de la clase Tarea.
            tarea = Tarea(
            nombre=dato["nombre"],
            completada=dato["completada"]
        )
        #tareas.append(tarea) Guardas ese nuevo objeto en tu lista acumuladora tareas
            tareas.append(tarea)

    #Aquí devuelve una lista de objetos Tarea en memoria RAM.
        return tareas



#Aquí paso lo contrario (Serialización) convertir cada objeto en algo que json entienda. Entonces hacemos lo contrario a 
#cargar_tareas.
    def guardar_tareas(self, lista_de_tareas: list[Tarea]) -> None:

        datos = []

        #Aquí json podría tener datos agregados que la clase Tarea no tiene, porque tranquilamente se podría agregar
        #"prioridad" = Alta, sin que la clase Tarea tenga ese atributo(PREGUNTAR Y SACARSE LA DUDA.) .
        for tarea in lista_de_tareas:
            datos.append({
            "nombre": tarea.nombre,
            "completada": tarea.completada
        })

        #Borra Json cuando hace "w" y escribe todas las tareas de nuevo.
        with open(self.ruta_archivo, "w") as archivo:
            json.dump(datos, archivo, indent=4)