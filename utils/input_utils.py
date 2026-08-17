def obtener_entero(mensaje: str) -> int | None:
    try:
        return int(input(mensaje))
    except ValueError:
        print("El dato debe de ser un número.")
        return None