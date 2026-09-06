from datetime import date

from services.interpretador_temporal import InterpretadorTemporal


def test_separa_bloques_y_calcula_lunes_y_siguiente_dia():
    interpretador = InterpretadorTemporal()

    bloques = interpretador.extraer_bloques(
        "El lunes voy al gym y tengo una reunión. El siguiente día compro mercadería y visito a mi mamá.",
        hoy=date(2026, 9, 5),
    )

    assert [(bloque.id, bloque.fecha) for bloque in bloques] == [
        (1, date(2026, 9, 7)),
        (2, date(2026, 9, 8)),
    ]
    assert "gym" in bloques[0].texto
    assert "reunión" in bloques[0].texto
    assert "mercadería" in bloques[1].texto
    assert "mamá" in bloques[1].texto
