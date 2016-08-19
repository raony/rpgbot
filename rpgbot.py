import diceroll
import re
import logging
import sys

LOGGER = logging.getLogger("RPGBot")

class RedisCache(object):
    def __init__(self, redis):
        self.redis = redis

    def __setitem__(self, key, value):
        self.redis.delete(key)
        self.redis.hmset(key, value)

    def __getitem__(self, item):
        return self.redis.hgetall(item)

    def has_key(self, key):
        return self.redis.exists(key)

def dice_result_format(result):
    str_result = 'Rolling {0} dices... '.format(unicode(result.roll.dices))
    if isinstance(result, diceroll.SuccessRollResult):
        if result.success():
            str_result += 'SUCCESS = {0} - '.format(result.success())
        else:
            str_result += 'FAIL! - '
        str_result += ','.join(map(unicode, result.rolls))
    elif isinstance(result, diceroll.SumRollResult):
        str_result += 'TOTAL = {0} ({1}+{2})'.format(result.total,
                                                     '+'.join(map(unicode, result.rolls)),
                                                     result.modifier)
    else:
        str_result += ','.join(map(unicode, result.rolls))


    return str_result


class RPGBot(object):
    def __init__(self, cache):
        self._cache = cache
        self._aliases = {
            'r': 'roll',
        }

    def _get_cmd_name(self, cmd):
        return self._aliases.get(cmd, cmd)

    def command(self, chat_id, cmd, *args):
        LOGGER.info('INCOMING %s: %s %s', chat_id, cmd, ' '.join(args))
        result = None
        try:
            cmd_name = self._get_cmd_name(cmd)
            if hasattr(self, cmd_name):
                result = getattr(self, cmd_name)(chat_id, *args)
            else:
                result = 'Invalid command.'
        except:
            LOGGER.exception('Exception occurred')
            result = 'Sorry, an error happened!'
        LOGGER.info('RESPONSE: %s', result)
        return result

    def setdice(self, chat_id, pattern):
        chat_data = self._cache[chat_id]
        chat_data['pattern'] = pattern
        self._cache[chat_id] = chat_data
        return 'Current dice pattern set to {0}.'.format(pattern)

    def roll(self, chat_id, pattern):
        try:
            pattern = unicode(pattern)
            dice_roll = diceroll.parse(pattern)
            result = dice_roll.roll()
            return dice_result_format(result)
        except ValueError:
            try:
                if self._cache.has_key(chat_id):
                    dice_roll = diceroll.parse(self._cache[chat_id]['pattern'].format(
                        *map(unicode.strip, pattern.split(','))))
                    result = dice_roll.roll()
                    return dice_result_format(result)
            except ValueError:
                pass
        return 'Invalid pattern.'