""" room.py """

'''
from tbot import bot
from Battle import MSG_ID


def checkUser(func):
    def inner(call):
        if MSG_ID.get(call.from_user.id) == call.message.message_id:
            return func(call)
        else:
            bot.answer_callback_query(callback_query_id = call.id, text = "Can't use this operation")

    return inner
'''
