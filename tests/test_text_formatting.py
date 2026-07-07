import unittest

from tutor_fisica.utils.text_formatting import formatear_respuesta_markdown


class TestTextFormatting(unittest.TestCase):

    def test_limpia_respuesta_conceptual_forzada_a_dos_secciones(self):
        respuesta_modelo = """
1. Principio físico

La Primera Ley de Newton explica que un cuerpo mantiene su estado de reposo o movimiento rectilíneo uniforme si la fuerza neta externa es cero.

4. Ecuaciones

No se requiere ecuación.

5. Sustitución con unidades

No se requiere sustitución.

6. Desarrollo matemático

No se requiere desarrollo matemático.

7. Respuestas finales

Un ejemplo cotidiano es un automóvil que se mueve en línea recta con velocidad constante.

8. Interpretación física breve

Esto muestra que el movimiento constante no requiere una fuerza neta externa distinta de cero.
"""

        salida = formatear_respuesta_markdown(respuesta_modelo)

        self.assertIn("### Explicación conceptual", salida)
        self.assertIn("### Respuesta", salida)
        self.assertNotIn("### Interpretación", salida)
        self.assertNotIn("No se requiere", salida)
        self.assertNotIn("### 4. Ecuaciones", salida)
        self.assertNotIn("### 5. Sustitución con unidades", salida)
        self.assertIn("automóvil", salida)

    def test_ejercicio_normal_conserva_formato_ocho_pasos(self):
        respuesta_modelo = """
1. Principio físico

Aplicamos la Segunda Ley de Newton.

2. Datos del problema

Masa: 5 kg. Fuerza: 20 N.

3. Incógnitas

Aceleración.

4. Ecuaciones

F = ma

5. Sustitución con unidades

20 N = 5 kg · a

6. Desarrollo matemático

a = 20 / 5 = 4 m/s²

7. Respuestas finales

a = 4 m/s²

8. Interpretación física breve

El bloque acelera en la dirección de la fuerza aplicada.
"""

        salida = formatear_respuesta_markdown(respuesta_modelo)

        self.assertIn("### 1. Principio físico", salida)
        self.assertIn("### 2. Datos del problema", salida)
        self.assertIn("### 7. Respuestas finales", salida)
        self.assertIn("### 8. Interpretación física breve", salida)


if __name__ == "__main__":
    unittest.main()
