class HPSystem:
    def __init__(self, max_hp=3):
        self.max_hp = max_hp
        self.current_hp = max_hp

    def take_damage(self, amount=1):
        self.current_hp -= amount
        if self.current_hp < 0:
            self.current_hp = 0

    def is_dead(self):
        return self.current_hp <= 0

    def reset(self):
        self.current_hp = self.max_hp