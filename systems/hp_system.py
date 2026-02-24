class HPSystem:
    def __init__(self, max_hp=3):
        self.max_hp = max_hp
        self.hp = max_hp

    def take_damage(self):
        self.hp -= 1
        return self.hp <= 0