from src.domain.entities.content import Content


class RegisterContentCommand:
    def __init__(self, content: Content):
        self.content = content
