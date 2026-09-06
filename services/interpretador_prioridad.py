"""Reconoce órdenes de prioridad expresados explícitamente por el usuario."""

from dataclasses import dataclass
import re
import unicodedata


@dataclass(frozen=True)
class PrioridadExplicita:
    """Posición de una tarea dentro de una lista explícita de prioridades."""

    orden: int
    total: int


class InterpretadorPrioridad:
    """Aplica reglas deterministas únicamente a listas de prioridad inequívocas."""

    PATRON_LISTA = re.compile(
        r"(?:lo\s+m[aá]s\s+importante(?:\s+para\s+m[ií])?|"
        r"mi\s+prioridad(?:\s+principal)?|mis\s+prioridades?)\s+"
        r"(?:es|son)\s+([^\.\n]+)",
        re.IGNORECASE,
    )
    PATRON_SEPARADOR = re.compile(
        r"\s*,?\s*(?:y\s+)?(?:despu[eé]s|luego|a\s+continuaci[oó]n|"
        r"por\s+[uú]ltimo|finalmente)\s+",
        re.IGNORECASE,
    )
    PATRON_ACLARACION = re.compile(
        r"\s+(?:aunque|pero|porque)\s+.*$",
        re.IGNORECASE,
    )
    PALABRAS_IGNORADAS = {
        "a", "al", "de", "del", "el", "en", "la", "las", "lo", "los",
        "mi", "mis", "para", "por", "un", "una", "y",
    }
    ALIAS = {"gym": "gimnasio"}

    def interpretar(
        self,
        texto: str,
        nombres_tareas: list[str],
    ) -> dict[str, PrioridadExplicita]:
        coincidencia = self.PATRON_LISTA.search(texto)
        if not coincidencia:
            return {}

        elementos = self._separar_elementos(coincidencia.group(1))
        if not elementos:
            return {}

        prioridades: dict[str, PrioridadExplicita] = {}
        nombres_disponibles = set(nombres_tareas)
        total = len(elementos)

        for orden, elemento in enumerate(elementos, start=1):
            nombre = self._encontrar_tarea(elemento, nombres_disponibles)
            if nombre is not None:
                prioridades[nombre] = PrioridadExplicita(orden, total)
                nombres_disponibles.remove(nombre)

        return prioridades

    def _separar_elementos(self, lista: str) -> list[str]:
        lista_sin_aclaracion = self.PATRON_ACLARACION.sub("", lista)
        partes = self.PATRON_SEPARADOR.split(lista_sin_aclaracion)
        elementos = []

        for parte in partes:
            elementos.extend(fragmento.strip() for fragmento in parte.split(","))

        return [elemento for elemento in elementos if elemento]

    def _encontrar_tarea(
        self,
        elemento: str,
        nombres_disponibles: set[str],
    ) -> str | None:
        palabras_elemento = self._palabras_significativas(elemento)
        if not palabras_elemento:
            return None

        coincidencias = []
        for nombre in nombres_disponibles:
            palabras_nombre = self._palabras_significativas(nombre)
            comunes = palabras_elemento & palabras_nombre
            puntaje = len(comunes) / len(palabras_elemento)
            coincidencias.append((puntaje, nombre))

        puntaje, nombre = max(coincidencias, default=(0, None))
        return nombre if puntaje >= 0.6 else None

    def _palabras_significativas(self, texto: str) -> set[str]:
        texto_normalizado = unicodedata.normalize("NFD", texto.lower())
        sin_tildes = "".join(
            caracter
            for caracter in texto_normalizado
            if unicodedata.category(caracter) != "Mn"
        )
        palabras = re.findall(r"[a-z0-9]+", sin_tildes)

        return {
            self.ALIAS.get(palabra, palabra)
            for palabra in palabras
            if palabra not in self.PALABRAS_IGNORADAS
        }
