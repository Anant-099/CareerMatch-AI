import unittest

from main import (
    find_skills,
    get_skill_weight,
    classify_skill_importance,
)


class TestSkillDetection(unittest.TestCase):
    def test_javascript_does_not_match_java(self):
        skills = find_skills(
            "We need a developer with JavaScript experience."
        )
        self.assertIn("javascript", skills)
        self.assertNotIn("java", skills)

    def test_java_is_detected(self):
        skills = find_skills("We need a Java developer.")
        self.assertIn("java", skills)
        self.assertNotIn("javascript", skills)

    def test_react_js_is_detected(self):
        skills = find_skills("Experience with React.js is required.")
        self.assertIn("react", skills)

    def test_duplicate_skills_are_not_returned(self):
        skills = find_skills(
            "Python developer with Python and Python experience."
        )
        self.assertEqual(skills.count("python"), 1)

    def test_unknown_text_returns_no_skills(self):
        skills = find_skills(
            "I enjoy reading books and walking outdoors."
        )
        self.assertEqual(skills, [])


class TestSkillWeighting(unittest.TestCase):
    def test_preferred_skill_gets_weight_one(self):
        self.assertEqual(
            get_skill_weight("docker", "Docker is preferred."),
            1,
        )

    def test_required_skill_gets_weight_two(self):
        self.assertEqual(
            get_skill_weight("python", "Python is required."),
            2,
        )

    def test_unrelated_preferred_sentence_does_not_change_weight(self):
        description = (
            "Python is required. Docker is nice to have."
        )
        self.assertEqual(get_skill_weight("python", description), 2)
        self.assertEqual(get_skill_weight("docker", description), 1)

    def test_required_occurrence_wins_if_skill_is_repeated(self):
        description = (
            "Docker is nice to have. Docker is required for deployment."
        )
        self.assertEqual(get_skill_weight("docker", description), 2)

    def test_generic_heading_resets_to_standard(self):
        description = (
            "Required skills:\n"
            "Python, SQL\n"
            "Preferred skills:\n"
            "Docker\n"
            "Other technologies mentioned:\n"
            "Git\n"
        )

        self.assertEqual(
            classify_skill_importance("git", description),
            "Standard",
        )

if __name__ == "__main__":
    unittest.main()
