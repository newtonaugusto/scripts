import unittest
from main import soma

class TestStringMethods(unittest.TestCase):
    def test_soma(self):
        teste = soma(2,2)
        self.assertEqual(teste, 4, "O valor deve ser igual a 4")

    def test_soma2(self):
        teste = soma(2,2)
        self.assertEqual(teste, 5, "O valor deve ser igual a 4")

if __name__ == '__main__':
    unittest.main()