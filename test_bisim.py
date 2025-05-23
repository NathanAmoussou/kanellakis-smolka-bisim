# /dev/null/test_bisim.py
import unittest
import os
from bisim import are_bisimilar # Assurez-vous que bisim.py est dans le PYTHONPATH

# Helper pour créer des fichiers LTS temporaires
def create_lts_file(filename, content):
    with open(filename, "w") as f:
        f.write(content)

class TestBisimilarity(unittest.TestCase):
    def setUp(self):
        # Créer les fichiers LTS pour les tests
        create_lts_file("b1.lts", "s a s1\ns a s2")
        create_lts_file("b2.lts", "t a t1\nt a t2")
        create_lts_file("nb1.lts", "s a s1\ns a s2\ns1 b s2\ns2 b s2")
        create_lts_file("nb2.lts", "t a t1\nt1 b t1")
        create_lts_file("test1_corrected.lts", "s a s1\ns a s4\ns4 b s2\ns1 b s2\ns2 c s3\ns3 c s")
        create_lts_file("test2_corrected.lts", "t a t1\nt1 b t2\nt2 c t3\nt3 c t")

        # Exemple de non-bisimilaires (différentes actions initiales)
        create_lts_file("non_b_1.lts", "s a s1")
        create_lts_file("non_b_2.lts", "s b s1")

        # Exemple de non-bisimilaires (structure différente)
        create_lts_file("non_b_struct1.lts", "s a s1\ns1 b s2")
        create_lts_file("non_b_struct2.lts", "s a s1")

        create_lts_file("empty.lts", "") # Fichier vide

    def tearDown(self):
        # Supprimer les fichiers LTS temporaires
        files = ["b1.lts", "b2.lts", "nb1.lts", "nb2.lts",
                   "test1_corrected.lts", "test2_corrected.lts",
                   "non_b_1.lts", "non_b_2.lts", "non_b_struct1.lts", "non_b_struct2.lts",
                   "empty.lts"]
        for f in files:
            if os.path.exists(f):
                os.remove(f)

    def test_bisimilar_simple(self):
        self.assertTrue(are_bisimilar("b1.lts", "b2.lts"))

    def test_nb_pair_are_actually_bisimilar(self):
        # Comme discuté, nb1 et nb2 sont bisimilaires avec le code corrigé
        self.assertTrue(are_bisimilar("nb1.lts", "nb2.lts"))

    def test_complex_bisimilar(self):
        self.assertTrue(are_bisimilar("test1_corrected.lts", "test2_corrected.lts"))

    def test_different_initial_actions(self):
        self.assertFalse(are_bisimilar("non_b_1.lts", "non_b_2.lts"))

    def test_different_structure(self):
        self.assertFalse(are_bisimilar("non_b_struct1.lts", "non_b_struct2.lts"))

    def test_empty_file(self):
        # load_lts devrait lever une ValueError, et are_bisimilar la gère
        self.assertFalse(are_bisimilar("b1.lts", "empty.lts"))
        self.assertFalse(are_bisimilar("empty.lts", "b1.lts"))

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
