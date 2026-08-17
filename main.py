from services.tarea_service import TareaService
from repository.tarea_repository  import TareaRepository
from utils.input_utils import obtener_entero
from utils.menu_utils import mostrar_menu

#Se crea una referencia de Service.
service = TareaService(TareaRepository())

nombre_usuario = input ("Hola coloca tu nombre: ")

print (f"Hola {nombre_usuario} , bienvenido al gestor de tareas")

while True:
    mostrar_menu()

    opcion = obtener_entero("Seleccione una opción: ")

    if opcion is None:
        continue
    
    match opcion:

        case 1:
            nombre_tarea = input("Coloque el nombre de la tarea: ")
            service.agregar_tarea( nombre_tarea)
        case 2:
            service.listar_tareas()
        case 3:

            service.listar_tareas()
            opcion_tarea = obtener_entero("¿Qué tarea desea seleccionar? ")

            if opcion_tarea is None:
                continue

            service.completar_tarea(opcion_tarea)
        case 4:
            service.listar_tareas()
            opcion_tarea= obtener_entero("¿Qué tarea desea seleccionar? ")

            if opcion_tarea is None:
                continue

            service.eliminar_tarea(opcion_tarea)
        case 5:
            print(f"Adiós {nombre_usuario}, hasta luego!")
            break

        case _:
            print(f"Opción no válida")
            break
            







