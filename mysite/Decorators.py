""" decorators.py """

from tbot import bot

def loadingFixed(func):
    def inner(call):
        # print(call)
        rv = func(call)

        bot.answer_callback_query(callback_query_id = call.id)
        return rv

    return inner
