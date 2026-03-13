class DifficultySystem:
    def __init__(self):
        self.speed = 200

    def increase_speed(self):
        self.speed += 50

    def get_speed(self):
        return self.speed