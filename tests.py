import unittest
import mock
import redis
from rpgbot import RPGBot, dice_result_format, RedisCache
from diceroll import DiceRollResult, DiceRoll, SuccessRollResult, SumRollResult


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

    def simple_sum_test(self):
        self.assertEquals('Rolling 4 dices... TOTAL = 14 (1+2+4+3+4)', dice_result_format(
            SumRollResult(
                DiceRoll(4, 8),
                [1, 2, 4, 3],
                4
            )
        ))

class RPGBotTest(unittest.TestCase):
    def invalid_command_test(self):
        target = RPGBot(RedisCache(mock.create_autospec(redis.StrictRedis)))
        self.assertEquals('Invalid command.', target.command('123', 'arroz', 'any', 'parameter'))

    @mock.patch('random.randint')
    def success_roll_test(self, randint_call):
        randint_call.side_effect = [1,2,3,4,5,6,7,8,8,8]
        target = RPGBot(RedisCache(mock.create_autospec(redis.StrictRedis)))
        self.assertEquals('Rolling 10 dices... SUCCESS = 3 - 1,2,3,4,5,6,7,8,8,8', target.command('123', 'r', '10d8>8'))

    @mock.patch('random.randint')
    def sum_roll_test(self, randint_call):
        randint_call.side_effect = [1, 2, 3, 4]
        target = RPGBot(RedisCache(mock.create_autospec(redis.StrictRedis)))
        self.assertEquals('Rolling 4 dices... TOTAL = 15 (1+2+3+4+5)', target.command('123', 'r', '4d8+5'))

    def wrong_roll_pattern_test(self):
        redis_mock = mock.create_autospec(redis.StrictRedis)
        redis_mock.exists.return_value = False
        target = RPGBot(RedisCache(redis_mock))
        self.assertEquals('Invalid pattern.', target.command('123', 'r', 'd8>8'))

    @mock.patch('random.randint')
    def using_dice_pattern_test(self, randint_call):
        mock_cache = {}
        redis_mock = mock.create_autospec(redis.StrictRedis)
        redis_mock.exists.return_value = True
        redis_mock.hgetall.return_value = mock_cache
        randint_call.side_effect = [1,2,3,4,5,6,7,8,8,8]
        target = RPGBot(RedisCache(redis_mock))
        self.assertEquals('Current dice pattern set to {0}d{1}>8.', target.command('123', 'setdice', '{0}d{1}>8'))
        self.assertEquals('Rolling 10 dices... SUCCESS = 3 - 1,2,3,4,5,6,7,8,8,8', target.command('123', 'r', '10,8'))
