from core.paths import agents_dir


class AgentLoader:

    def __init__(self):
        self.agents = {}

    def load(self):
        for file in agents_dir().glob("*.md"):
            self.agents[file.stem] = file.read_text()
        return self.agents
