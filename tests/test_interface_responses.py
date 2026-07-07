import unittest

from tutor_fisica.utils.interface_responses import buscar_respuesta_interfaz


class TestInterfaceResponses(unittest.TestCase):

    def test_saludo_responde_desde_json(self):
        resultado = buscar_respuesta_interfaz("hola")
        self.assertTrue(resultado.encontrada)
        self.assertEqual(resultado.categoria, "saludo")
        self.assertIn("Tutor de Física EPN", resultado.respuesta)

    def test_identidad_responde_desde_json(self):
        resultado = buscar_respuesta_interfaz("como te llamas")
        self.assertTrue(resultado.encontrada)
        self.assertEqual(resultado.categoria, "identidad")

    def test_creador_responde_desde_json(self):
        resultado = buscar_respuesta_interfaz("quien te creo")
        self.assertTrue(resultado.encontrada)
        self.assertEqual(resultado.categoria, "creador_sistema")

    def test_java_fuera_de_dominio(self):
        resultado = buscar_respuesta_interfaz("sabes que es java")
        self.assertTrue(resultado.encontrada)
        self.assertEqual(resultado.categoria, "fuera_dominio")

    def test_angular_tecnologia_fuera_de_dominio(self):
        resultado = buscar_respuesta_interfaz("conoces sobre la tecnologia de angular")
        self.assertTrue(resultado.encontrada)
        self.assertEqual(resultado.categoria, "fuera_dominio")

    def test_velocidad_angular_no_se_bloquea(self):
        resultado = buscar_respuesta_interfaz("que es velocidad angular")
        self.assertFalse(resultado.encontrada)

    def test_gravedad_no_se_bloquea(self):
        resultado = buscar_respuesta_interfaz("como calculo la gravedad de un sitio")
        self.assertFalse(resultado.encontrada)

    def test_ejercicio_fisica_no_se_bloquea(self):
        resultado = buscar_respuesta_interfaz(
            "Un bloque de 5 kg recibe una fuerza de 20 N. Calcula su aceleración."
        )
        self.assertFalse(resultado.encontrada)


if __name__ == "__main__":
    unittest.main()
