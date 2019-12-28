# -*- coding: utf-8 -*-

import random
import time
from threading import Thread

import vk_api
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll

from words import words, vowels
from messages import successMessages, failureMessages
from commands import availableCommands
from keyboards import startGameKeyboard
from utils.rthread import rThread
from server import Server, vk, vk_session, longpoll
from user import User

existingUsers = []
        
def userIsExisting(mentionID):
    print(10)
    for user in existingUsers:
        if user.mentionID == mentionID:
            return user
    user = User(mentionID)
    existingUsers.append(user)
    return user

def eventHandler(event):
    try:
        if event.type == VkBotEventType.MESSAGE_NEW:
            thread = rThread(
                target=userIsExisting, args=(event.obj.message["from_id"],)
            )
            thread.start()
            user = thread.join()
            Thread(
                target=user.callAvailableCommands, args=(event.obj.message["text"],)
            ).start()
    except:
        pass
    
for event in longpoll.listen():
    try:
        print(event)
        Thread(target=eventHandler, args=(event,)).start()
    except:
        pass