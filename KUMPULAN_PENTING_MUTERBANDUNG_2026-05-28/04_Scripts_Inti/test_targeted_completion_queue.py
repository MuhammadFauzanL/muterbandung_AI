import unittest

from Scripts.generate_targeted_completion_queue import generate_queue


class TestTargetedCompletionQueue(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.queue, cls.summary = generate_queue()

    def test_queue_generated_from_canonical_dataset(self):
        self.assertGreater(len(self.queue), 0)
        self.assertGreaterEqual(self.summary["location_count"], 200)
        self.assertIn("P0", self.summary["priority_counts"])
        self.assertIn("active_status_verification", self.summary["task_type_counts"])

    def test_hours_tasks_are_p0(self):
        hours = self.queue[self.queue["task_type"] == "opening_hours_completion"]
        if len(hours) > 0:
            self.assertTrue((hours["priority"] == "P0").all())
        else:
            self.assertNotIn("opening_hours_completion", self.summary["task_type_counts"])

    def test_local_candidates_are_not_auto_applied(self):
        candidate_tasks = self.queue[self.queue["candidate_status"] != ""]
        self.assertGreater(len(candidate_tasks), 0)
        self.assertTrue((candidate_tasks["auto_apply_allowed"] == "False").all())


if __name__ == "__main__":
    unittest.main()
