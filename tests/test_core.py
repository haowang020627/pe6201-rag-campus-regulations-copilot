import unittest
from pathlib import Path
from rag_copilot.core import CampusCopilot, load_documents

ROOT = Path(__file__).parents[1]

class CoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.copilot = CampusCopilot(load_documents(ROOT / "data" / "demo"))
    def test_answer_contains_citation(self):
        result = self.copilot.answer("What is the late submission penalty?")
        self.assertFalse(result["abstained"])
        self.assertIn("academic_regulations.txt, p. 2", result["citations"])
    def test_unknown_question_abstains(self):
        result = self.copilot.answer("What is the tuition refund deadline?")
        self.assertTrue(result["abstained"])
        self.assertEqual(result["citations"], [])

if __name__ == "__main__": unittest.main()
