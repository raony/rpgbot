import diceroll
import re
import logging
import sys

LOGGER = logging.getLogger("RPGBot")

class DicePatternDict(dict):
    pattern_arguments = re.compile(r'\{\d+\}')

    def _replace_arguments(self, pattern):
        return DicePatternDict.pattern_arguments.sub('1', pattern)

    def __setitem__(self, key, value):
        replaced_value = self._replace_arguments(value)
        if diceroll.validate_dice_pattern(replaced_value):
            return super(DicePatternDict, self).__setitem__(key, value)
        else:
            raise ValueError('invalid pattern')

    def __getitem__(self, item):
        return super(DicePatternDict, self).__getitem__(item)

def dice_result_format(result):
    str_result = 'Rolling {0} dices... '.format(unicode(result.roll.dices))
    if isinstance(result, diceroll.SuccessRollResult):
        if result.success():
            str_result += 'SUCCESS = {0} - '.format(result.success())
        else:
            str_result += 'FAIL! - '
    str_result += ','.join(map(unicode, result.rolls))

    return str_result


class RPGBot(object):
    def __init__(self):
        self._cache = DicePatternDict()
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
        try:
            self._cache[chat_id] = pattern
            return 'Current dice pattern set to {0}.'.format(pattern)
        except ValueError:
            return 'Invalid pattern.'

    def roll(self, chat_id, pattern):
        try:
            dice_roll = diceroll.parse(pattern)
            result = dice_roll.roll()
            return dice_result_format(result)
        except ValueError:
            try:
                if self._cache.has_key(chat_id):
                    dice_roll = diceroll.parse(self._cache[chat_id].format(*map(str.strip, pattern.split(','))))
                    result = dice_roll.roll()
                    return dice_result_format(result)
            except ValueError:
                pass
        return 'Invalid pattern.'