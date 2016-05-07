import random

class DiceRoll(object):
    def __init__(self, dices):
        self.dices = dices
        self.roll = self._roll_with_explode(dices)

    def _roll_with_explode(self, dices):
        if not dices:
            return []
        result = [random.randint(1,10) for n in xrange(dices)]
        exploded = len([x for x in result if x == 10])
        return result + self._roll_with_explode(exploded)

    def successes(self):
        return len([value for value in self.roll if value >= 8])