import re
import unicodedata
from datetime import date, timedelta

from models.bloque_temporal import BloqueTemporal


class InterpretadorTemporal:
    """Extrae referencias temporales deterministas sin depender del LLM."""

    DIAS_SEMANA = (
        "lunes",
        "martes",
        "miércoles",
        "jueves",
        "viernes",
        "sábado",
        "domingo",
    )
    PATRON_REFERENCIA = re.compile(
        r"\b(?:"
        r"(?:el\s+)?(?:pr[oó]ximo\s+)?(?:lunes|martes|mi[eé]rcoles|jueves|viernes|s[aá]bado|domingo)"
        r"|hoy|ma[ñn]ana"
        r"|(?:el\s+)?siguiente\s+d[ií]a"
        r"|(?:al\s+)?d[ií]a\s+siguiente"
        r")\b",
        re.IGNORECASE,
    )

    def extraer_bloques(self, texto: str, hoy: date) -> list[BloqueTemporal]:
        coincidencias = list(self.PATRON_REFERENCIA.finditer(texto))

        if not coincidencias:
            return [BloqueTemporal(id=1, texto=texto.strip(), fecha=None)]

        bloques: list[BloqueTemporal] = []
        inicio = 0
        ultima_fecha: date | None = None

        for indice, coincidencia in enumerate(coincidencias):
            if coincidencia.start() > inicio:
                texto_previo = texto[inicio:coincidencia.start()].strip(" ,.;")
                if texto_previo:
                    bloques.append(
                        BloqueTemporal(
                            id=len(bloques) + 1,
                            texto=texto_previo,
                            fecha=None,
                        )
                    )

            fin = (
                coincidencias[indice + 1].start()
                if indice + 1 < len(coincidencias)
                else len(texto)
            )
            texto_bloque = texto[coincidencia.start():fin].strip(" ,.;")
            fecha = self._resolver_referencia(
                coincidencia.group(),
                hoy,
                ultima_fecha,
            )
            ultima_fecha = fecha or ultima_fecha
            bloques.append(
                BloqueTemporal(
                    id=len(bloques) + 1,
                    texto=texto_bloque,
                    fecha=fecha,
                )
            )
            inicio = fin

        return bloques

    def _resolver_referencia(
        self,
        referencia: str,
        hoy: date,
        ultima_fecha: date | None,
    ) -> date:
        referencia_normalizada = self._normalizar(referencia)

        if "siguiente dia" in referencia_normalizada or "dia siguiente" in referencia_normalizada:
            return (ultima_fecha or hoy) + timedelta(days=1)

        if referencia_normalizada == "hoy":
            return hoy

        if referencia_normalizada == "manana":
            return hoy + timedelta(days=1)

        for indice, nombre_dia in enumerate(self.DIAS_SEMANA):
            if self._normalizar(nombre_dia) in referencia_normalizada:
                return hoy + timedelta(days=(indice - hoy.weekday()) % 7)

        return hoy

    @staticmethod
    def _normalizar(texto: str) -> str:
        return " ".join(
            "".join(
                caracter
                for caracter in unicodedata.normalize("NFD", texto.lower())
                if unicodedata.category(caracter) != "Mn"
            ).split()
        )
