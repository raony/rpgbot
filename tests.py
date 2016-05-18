import unittest
import mock
from rpgbot import RPGBot, dice_result_format
from diceroll import DiceRollResult, DiceRoll, SuccessRollResult

class DiceResultFormatTest(unittest.TestCase):
    def simple_roll_test(self):
        self.assertEquals('Rolling 4 dices... 1,2,3,4', dice_result_format(
            DiceRollResult(
                DiceRoll(4, 8),
                [1,2,3,4]
            )
        ))

    def simple_success_test(self):
        self.assertEquals('Rolling 4 dices... SUCCESS = 2 - 1,2,3,4', dice_result_format(
            SuccessRollResult(
                DiceRoll(4,8),
                [1,2,3,4],
                treshold = 3
            )
        ))

    def simple_fail_test(self):
        self.assertEquals('Rolling 4 dices... FAIL! - 1,2,2,2', dice_result_format(
            SuccessRollResult(
                DiceRoll(4, 8),
                [1, 2, 2, 2],
                treshold=3
            )
        ))


class RPGBotTest(unittest.TestCase):
    def invalid_command_test(self):
        target = RPGBot({})
        self.assertEquals('Invalid command.', target.command('123', 'arroz', 'any', 'parameter'))

    @mock.patch('random.randint')
    def success_roll_test(self, randint_call):
        randint_call.side_effect = [1,2,3,4,5,6,7,8,8,8]
        target = RPGBot({})
        self.assertEquals('Rolling 10 dices... SUCCESS = 3 - 1,2,3,4,5,6,7,8,8,8', target.command('123', 'r', '10d8>8'))

    def wrong_roll_pattern_test(self):
        target = RPGBot({})
        self.assertEquals('Invalid pattern.', target.command('123', 'r', 'd8>8'))

    @mock.patch('random.randint')
    def using_dice_pattern_test(self, randint_call):
        randint_call.side_effect = [1,2,3,4,5,6,7,8,8,8]
        target = RPGBot({'123': {}})
        self.assertEquals('Current dice pattern set to {0}d{1}>8.', target.command('123', 'setdice', '{0}d{1}>8'))
        self.assertEquals('Rolling 10 dices... SUCCESS = 3 - 1,2,3,4,5,6,7,8,8,8', target.command('123', 'r', '10,8'))
