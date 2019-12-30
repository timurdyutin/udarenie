import argparse
import random
from commands import availableCommands
from threading import Thread

import vk_api
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from keyboards import startGameKeyboard
from messages import failureMessages, successMessages
from utils.rthread import rThread
from words import vowels, words
from achievements import achievements

parser = argparse.ArgumentParser(description="Необходимы: токен и ID группы ВК")
parser.add_argument("token", help="Введи токен группы ВК")
parser.add_argument("groupID", help="Введи ID группы ВК")
args = parser.parse_args()

existingUsers = []

class Server:
    def __init__(self, token, groupID):
        self.token = token
        self.groupID = str(groupID)
        self.vk_session = None
        self.vk = None
        self.longpoll = None

    def connectToVKApi(self):
        try:
            self.vk_session = vk_api.VkApi(token=self.token)
            self.vk = self.vk_session.get_api()
            self.longpoll = VkBotLongPoll(self.vk_session, self.groupID)
            print("Бот успешно подключился к VK")
        except:
            print("Не удалось подключиться к VK")


class User:
    def __init__(self, mentionID):
        self.mentionID = mentionID
        self.gameIsActive = False
        self.selectWordKeyboard = VkKeyboard(one_time=False)
        self.guessedWordsCount = 0
        self.word = None
        self.rightWord = None
        self.wrongWords = []

    def callAvailableCommands(self, request):
        availableCommands = {
            "Начать": self.sendIntroductionMessage,
            "Начать игру": self.startGame,
            "Выйти из игры": self.quitGame,
        }
        if (
            self.gameIsActive is True or self.gameIsActive is False
        ) and request in availableCommands:
            availableCommands[request]()
        if self.gameIsActive is True and request not in availableCommands:
            self.checkAnswer(request)

    def sendIntroductionMessage(self):
        vk.messages.send(
            peer_id=self.mentionID,
            message="О, привет! \n Хочешь начать играть? Нажми на кнопку 'Начать игру'!",
            random_id=random.getrandbits(32),
            keyboard=startGameKeyboard.get_keyboard(),
        )

    def startGame(self):
        if self.gameIsActive is True:
            vk.messages.send(
                peer_id=self.mentionID,
                message="Ты уже начал играть со мной. \n Хочешь выйти? Нажми на кнопку 'Выйти из игры'",
                random_id=random.getrandbits(32),
            )
        else:
            self.gameIsActive = True
            self.generateWord()
            vk.messages.send(
                peer_id=self.mentionID,
                message=f"Поставьте ударение в слове '{''.join(self.word)}''",
                random_id=random.getrandbits(32),
                keyboard=self.selectWordKeyboard.get_keyboard(),
            )

    def quitGame(self):
        if self.gameIsActive is False:
            vk.messages.send(
                peer_id=self.mentionID,
                message=f"Нельзя выйти оттуда, где ты никогда не был. \n (C) Физика",
                random_id=random.getrandbits(32),
                keyboard=startGameKeyboard.get_keyboard(),
            )
        else:
            self.gameIsActive = False
            vk.messages.send(
                peer_id=self.mentionID,
                message=f"Ты вышел из игры. Надеемся, что ты вернёшься!",
                random_id=random.getrandbits(32),
                keyboard=startGameKeyboard.get_keyboard(),
            )

    def generateWord(self):
        self.selectWordKeyboard = VkKeyboard(one_time=False)
        self.word = random.choice(list(words.keys()))
        self.rightWord = words[self.word]
        self.word = list(self.word)
        for i in range(len(self.word)):
            if self.word[i] in vowels:
                self.word[i] = self.word[i].upper()
                self.wrongWords.append("".join(self.word))
                self.selectWordKeyboard.add_button(
                    "".join(self.word), color=VkKeyboardColor.PRIMARY
                )
                self.selectWordKeyboard.add_line()
                self.word[i] = self.word[i].lower()
        self.selectWordKeyboard.add_button(
            "Выйти из игры", color=VkKeyboardColor.NEGATIVE
        )

    def checkAnswer(self, word):
        if word == self.rightWord:
            vk.messages.send(
                peer_id=self.mentionID,
                message=f"{random.choice(successMessages)} ударение в слове {self.rightWord} падает на {self.rightWord.index([symbol for symbol in self.rightWord if symbol.isupper() is True][0]) + 1} букву",
                random_id=random.getrandbits(32),
                keyboard=self.selectWordKeyboard.get_keyboard(),
            )
            self.guessedWordsCount += 1
            if self.guessedWordsCount in achievements.keys():
                vk.messages.send(
                    peer_id=self.mentionID,
                    message=f"Поздравляем! Получено новое достижение: {achievements[self.guessedWordsCount]}.",
                    random_id=random.getrandbits(32),
                    keyboard=self.selectWordKeyboard.get_keyboard(),
                )
            self.gameIsActive = False
            self.startGame()
        else:
            vk.messages.send(
                peer_id=self.mentionID,
                message=f"{random.choice(failureMessages)}",
                random_id=random.getrandbits(32),
                keyboard=self.selectWordKeyboard.get_keyboard(),
            )

server = Server(args.token, args.groupID)
server.connectToVKApi()
vk_session, vk, longpoll = server.vk_session, server.vk, server.longpoll

def userIsExisting(mentionID):
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


if longpoll is not None:
    for event in longpoll.listen():
        try:
            Thread(target=eventHandler, args=(event,)).start()
        except:
            pass
