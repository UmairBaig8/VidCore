from core.paths import skills_dir


class SkillRegistry:

    def __init__(self):
        self.skills = []

    def load(self):
        for file in skills_dir().glob("*.py"):
            if file.name.startswith("_"):
                continue
            self.skills.append(file.stem)
        return self.skills
