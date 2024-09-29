import unittest
from agent import generate_lesson_plan, graph_struct, LessonPlanState

class TestLessonPlanGeneration(unittest.TestCase):

    def test_generate_lesson_plan(self):
        topic = "Refraction"
        age = 15
        result = generate_lesson_plan(topic, age)

        self.assertIn("Learning Objectives", result)
        self.assertIn("Key Vocabulary", result)
        self.assertIn("Activities", result)
        self.assertIn("Main Activities", result)
        self.assertIn("Content Summary", result)
        self.assertIn("Plenary", result)

        # Check that generated content is a string and not empty
        for section in result:
            self.assertIsInstance(result[section], str)
            self.assertGreater(len(result[section]), 0)

    def test_graph_compilation(self):
        graph = graph_struct()
        self.assertIsNotNone(graph)
        self.assertTrue(hasattr(graph, 'invoke'))

    def test_graph_execution(self):
        test_state = LessonPlanState(topic="Test", age=10, lesson_plan=None)
        graph = graph_struct()
        result = graph.invoke(test_state)
        self.assertIn('lesson_plan', result)
        self.assertIsNotNone(result['lesson_plan'])

if __name__ == "__main__":
    unittest.main()
