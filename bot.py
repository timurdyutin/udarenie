# -*- coding: utf-8 -*-
import random
import time
from threading import Thread
from requests import *
import vk_api
from vk_api import VkUpload
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import os
from keyboards import (
    startGameKeyboard,
    selectFriendGameKeyboard,
    cancelSearchUserKeyboard,
)
from messages import failureMessages, successMessages
from utils.rthread import rThread
from words import vowels, words
from achievements import achievements
from generateInventationCode import generateInventationCode

existingUsers = {}
randomGamesUsers = []
codes = {}

admin = 172244532
try:

    class Server:
        def __init__(self, token=None, groupID=None):
            self.token = "70cb1f8026e1adf42d7e9534edab8c8ca8e6c0796f23fa71ab338f196b7f2d853182b179d13c97f179acf"
            self.groupID = "186661962"
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

        def checkCodeDuration(self):
            while True:
                for user in list(existingUsers.values()):
                    if user.codeDuration is not None and user.code is not None:
                        if time.time() - user.codeDuration > 60:
                            self.sendCodeIsExpiredMessage(user)

        def sendCodeIsExpiredMessage(self, userObject):
            vk.messages.send(
                peer_id=userObject.mentionID,
                message=f"Срок действия твоего кода: {userObject.code} истёк.",
                random_id=random.getrandbits(32),
            )
            userObject.codeDuration = None
            userObject.code = None
            time.sleep(1)

        def newUserEvent(self, realName):
            vk.messages.send(
                peer_id=admin,
                message=f"Новый пользователь: {realName}",
                random_id=random.getrandbits(32),
            )

        def leaveUserEvent(self, mentionID):
            attachments = []
            image = open(r"{}.PNG".format(random.choice(range(1, 3))), "rb")
            photo = upload.photo_messages(photos=image.raw)[0]
            attachments.append("photo{}_{}".format(photo["owner_id"], photo["id"]))
            vk.messages.send(
                random_id=random.randrange(32),
                peer_id=mentionID,
                message=f"Пока, {vk.users.get(user_ids=event.obj['user_id'])[0]['first_name']}. \n /ударение будет скучать по тебе!",
                attachment=",".join(attachments),
            )

    class singleGame:
        def __init__(self, mentionID):
            self.mentionID = mentionID
            self.selectWordKeyboard = VkKeyboard(one_time=False)
            self.guessedWordsCount = 0
            self.wrongWords = []
            self.word = None
            self.rightWord = None
            self.availableCommands = {"Выйти из игры": self.quitGame}

        def callAvailableCommands(self, request):
            if request in self.availableCommands.keys():
                self.availableCommands[request]()
            else:
                self.checkAnswer(request)

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
                        "".join(self.word), color=VkKeyboardColor.DEFAULT
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
                self.startGame()
            else:
                if word in self.wrongWords:
                    vk.messages.send(
                        peer_id=self.mentionID,
                        message=f"{random.choice(failureMessages)}",
                        random_id=random.getrandbits(32),
                        keyboard=self.selectWordKeyboard.get_keyboard(),
                    )

        def startGame(self):
            self.generateWord()
            vk.messages.send(
                peer_id=self.mentionID,
                message=f"Поставь ударение в слове '{''.join(self.word)}''",
                random_id=random.getrandbits(32),
                keyboard=self.selectWordKeyboard.get_keyboard(),
            )

        def quitGame(self):
            existingUsers[self.mentionID].singleGameMode = False
            existingUsers[self.mentionID].userMode = True
            vk.messages.send(
                peer_id=self.mentionID,
                message=f"Ты вышел из игры 'Одиночная игра'",
                random_id=random.getrandbits(32),
                keyboard=startGameKeyboard.get_keyboard(),
            )

    class friendGame(singleGame):
        def __init__(self, firstUser, secondUser=None):
            self.firstUser = firstUser
            self.secondUser = secondUser
            self.firstMessageMode = True
            self.selectWordKeyboard = VkKeyboard(one_time=False)
            self.guessedWordsCount = 0
            self.wrongWords = []
            self.word = None
            self.rightWord = None
            self.availableCommands = {"Выйти из игры": self.quitGame}

        def callAvailableCommands(self, request, mentionID):
            if request in self.availableCommands.keys():
                self.availableCommands[request](mentionID)
            else:
                self.checkAnswer(request, mentionID)

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
                        "".join(self.word), color=VkKeyboardColor.DEFAULT
                    )
                    self.selectWordKeyboard.add_line()
                    self.word[i] = self.word[i].lower()
            self.selectWordKeyboard.add_button(
                "Выйти из игры", color=VkKeyboardColor.NEGATIVE
            )

        def sendSuccessMessage(self, f):
            vk.messages.send(
                peer_id=f,
                message=f"{random.choice(successMessages)} ударение в слове {self.rightWord} падает на {self.rightWord.index([symbol for symbol in self.rightWord if symbol.isupper() is True][0]) + 1} букву",
                random_id=random.getrandbits(32),
                keyboard=self.selectWordKeyboard.get_keyboard(),
            )

        def sendFailureMessage(self, s):
            vk.messages.send(
                peer_id=s,
                message=f"Ой, ты не успел ответить.",
                random_id=random.getrandbits(32),
                keyboard=self.selectWordKeyboard.get_keyboard(),
            )

        def checkAnswer(self, word, mentionID):
            f, s = self.getPos(mentionID)
            if word == self.rightWord:
                Thread(target=self.sendSuccessMessage, args=(f,)).start()
                Thread(target=self.sendFailureMessage, args=(s,)).start()
                self.firstMessageMode = False
                self.startGame()
            else:
                if word in self.wrongWords:
                    vk.messages.send(
                        peer_id=f,
                        message=f"{random.choice(failureMessages)}",
                        random_id=random.getrandbits(32),
                        keyboard=self.selectWordKeyboard.get_keyboard(),
                    )

        def getPos(self, mentionID):
            if mentionID == self.firstUser:
                return self.firstUser, self.secondUser
            else:
                return self.secondUser, self.firstUser

        def startGame(self):
            self.generateWord()
            firstUserName = vk.users.get(user_ids=self.firstUser)
            secondUserName = vk.users.get(user_ids=self.secondUser)
            firstText = f"Ты успешно подключился к игре с {firstUserName[0]['first_name']} {firstUserName[0]['last_name'][0]}."
            secondText = (
                f"Ты успешно подключился к игре с {secondUserName[0]['first_name']} {secondUserName[0]['last_name'][0]}.",
            )
            if self.firstMessageMode is True:
                vk.messages.send(
                    peer_id=self.secondUser,
                    message=firstText,
                    random_id=random.getrandbits(32),
                )
                vk.messages.send(
                    peer_id=self.firstUser,
                    message=secondText,
                    random_id=random.getrandbits(32),
                )
            vk.messages.send(
                peer_id=self.firstUser,
                message=f"Поставь ударение в слове '{''.join(self.word)}''",
                random_id=random.getrandbits(32),
                keyboard=self.selectWordKeyboard.get_keyboard(),
            )
            vk.messages.send(
                peer_id=self.secondUser,
                message=f"Поставь ударение в слове '{''.join(self.word)}''",
                random_id=random.getrandbits(32),
                keyboard=self.selectWordKeyboard.get_keyboard(),
            )

        def quitGame(self, mentionID):
            f, s = self.getPos(mentionID)
            """codes.pop(existingUsers[self.firstUser].code)"""
            existingUsers[self.firstUser].friendGameMode = False
            existingUsers[self.firstUser].userMode = True
            existingUsers[self.firstUser].code = None
            existingUsers[self.secondUser].friendGameMode = False
            existingUsers[self.secondUser].userMode = True
            existingUsers[self.secondUser].code = None
            vk.messages.send(
                peer_id=s,
                message=f"Ты был отключен от игры, потому что игрок {vk.users.get(user_ids=f)[0]['first_name']} {vk.users.get(user_ids=f)[0]['last_name'][0]} решил выйти из игры.",
                random_id=random.getrandbits(32),
                keyboard=startGameKeyboard.get_keyboard(),
            )
            vk.messages.send(
                peer_id=f,
                message=f"Ты вышел из игры 'Сыграть с другом'",
                random_id=random.getrandbits(32),
                keyboard=startGameKeyboard.get_keyboard(),
            )

    class randomGame(friendGame):
        def __init__(self, firstUser, secondUser):
            self.firstUser = firstUser
            self.secondUser = secondUser
            super().__init__(self.firstUser, self.secondUser)

        def quitGame(self, mentionID):
            f, s = self.getPos(mentionID)
            existingUsers[self.firstUser].randomGameMode = False
            existingUsers[self.firstUser].userMode = True
            existingUsers[self.secondUser].userMode = True
            existingUsers[self.secondUser].randomGameMode = False
            vk.messages.send(
                peer_id=s,
                message=f"Ты был отключен от игры, потому что игрок {vk.users.get(user_ids=f)[0]['first_name']} {vk.users.get(user_ids=f)[0]['last_name'][0]} решил выйти из игры.",
                random_id=random.getrandbits(32),
                keyboard=startGameKeyboard.get_keyboard(),
            )
            vk.messages.send(
                peer_id=f,
                message=f"Ты вышел из игры 'Случайная игра'",
                random_id=random.getrandbits(32),
                keyboard=startGameKeyboard.get_keyboard(),
            )

    class User:
        def __init__(self, mentionID):
            self.mentionID = mentionID
            self.singleGameMode = False
            self.singleGameObject = None
            self.friendGameMode = False
            self.friendGameObject = None
            self.randomGameMode = False
            self.randomGameObject = None
            self.dataCollectionMode = False
            self.searchRandomGameMode = False
            self.userMode = True
            self.code = None
            self.codeDuration = None
            self.availableCommands = {
                "Начать": self.sendIntroductionMessage,
                "Одиночная игра": self.singleGame,
                "Случайная игра": self.randomGame,
                "Сыграть с другом": self.friendGame,
                "Создать игру": self.generateCode,
                "Ввести код": self.enterCode,
                "Вернуться назад": self.backToMain,
                "Выйти из игры": self.quitGame,
                "Отменить поиск": self.cancelSearchRandomGame,
            }

        def callAvailableCommands(self, request, mentionID):
            if self.singleGameMode is True:
                self.singleGameObject.callAvailableCommands(request)
            elif self.friendGameMode is True:
                self.friendGameObject.callAvailableCommands(request, mentionID)
            elif self.randomGameMode is True:
                self.randomGameObject.callAvailableCommands(request, mentionID)
            elif self.dataCollectionMode is True:
                self.checkCode(request)
            elif self.searchRandomGameMode is True and request == "Отменить поиск":
                self.availableCommands[request]()
            elif self.userMode is True:
                if request in self.availableCommands:
                    self.availableCommands[request]()
                else:
                    self.sendFailureMessage()

        def quitGame(self):
            vk.messages.send(
                peer_id=self.mentionID,
                message="Ты вернулся назад, в главное меню.",
                random_id=random.getrandbits(32),
                keyboard=startGameKeyboard.get_keyboard(),
            )

        def sendFailureMessage(self):
            vk.messages.send(
                peer_id=self.mentionID,
                message="Извини, я тебя совсем не понимаю :(",
                random_id=random.getrandbits(32),
                keyboard=startGameKeyboard.get_keyboard(),
            )

        def sendIntroductionMessage(self):
            vk.messages.send(
                peer_id=self.mentionID,
                message="Привет! \n Хочешь начать играть? \n Выбери тип игры, в который ты хочешь сыграть:",
                random_id=random.getrandbits(32),
                keyboard=startGameKeyboard.get_keyboard(),
            )

        def singleGame(self):
            vk.messages.send(
                peer_id=self.mentionID,
                message=f"Ты начал играть в режим 'Одиночная игра', ставь ударение в словах, нажимая на кнопки, в которых указан верный вариант постановки ударения!",
                random_id=random.getrandbits(32),
                keyboard=startGameKeyboard.get_keyboard(),
            )
            self.singleGameMode = True
            self.userMode = False
            self.singleGameObject = singleGame(self.mentionID)
            self.singleGameObject.startGame()

        def randomGame(self):
            self.searchRandomGameMode = True
            self.userMode = False
            vk.messages.send(
                peer_id=self.mentionID,
                message=f"Мы ищем подходящего для тебя соперника. Когда соперник будет найден, ты сразу же подключишься к игре.",
                random_id=random.getrandbits(32),
                keyboard=cancelSearchUserKeyboard.get_keyboard(),
            )
            self.searchRandomGame()

        def cancelSearchRandomGame(self):
            try:
                randomGamesUsers.remove(self.mentionID)
            except ValueError:
                pass
            self.searchRandomGameMode = False
            self.userMode = True
            self.backToMain()

        def searchRandomGame(self):
            if len(randomGamesUsers) != 0:
                if self.mentionID != existingUsers[randomGamesUsers[0]].mentionID:
                    self.randomGameObject = randomGame(
                        self.mentionID, existingUsers[randomGamesUsers[0]].mentionID
                    )
                    existingUsers[
                        randomGamesUsers[0]
                    ].randomGameObject = self.randomGameObject
                    self.randomGameObject.startGame()
                    self.userMode = False
                    self.randomGameMode = True
                    existingUsers[randomGamesUsers[0]].userMode = False
                    existingUsers[randomGamesUsers[0]].randomGameMode = True
                    randomGamesUsers.remove(randomGamesUsers[0])
            else:
                randomGamesUsers.append(self.mentionID)

        def generateCode(self):
            attachments = []
            self.dataCollectionMode = False
            self.code = random.choice(range(1000, 10000))
            while self.code in codes.keys():
                self.code = random.choice(range(1000, 10000))
            self.codeDuration = time.time()
            print(self.codeDuration)
            """imagePath = generateInventationCode(self.mentionID, self.code)
            image = open(imagePath, "rb")
            photo = upload.photo_messages(photos=image.raw)[0]
            attachments.append('photo{}_{}'.format(photo['owner_id'], photo['id']))"""
            vk.messages.send(
                random_id=random.randrange(32),
                peer_id=self.mentionID,
                message=f"Отправь этот код {self.code} своему другу, чтобы он смог присоединиться к игре! Срок действия кода составляет 1 минуту.",
            )

        def getGameIsActiveStatus(self):
            if (
                self.randomGameMode is True
                or self.singleGameMode is True
                or self.friendGameMode is True
            ):
                return True
            else:
                return False

        def checkCode(self, code):
            if code not in self.availableCommands.keys():
                if code.isdigit() is True and len(code) == 4:
                    for user in existingUsers.values():
                        if (
                            user.code == int(code)
                            and user.mentionID != self.mentionID
                            and user.getGameIsActiveStatus() is False
                        ):
                            self.friendGameMode = True
                            self.userMode = False
                            user.friendGameMode = True
                            user.userMode = False
                            self.code = code
                            self.dataCollectionMode = False
                            user.dataCollectionMode = False
                            self.friendGameObject = friendGame(
                                user.mentionID, self.mentionID
                            )
                            user.friendGameObject = self.friendGameObject
                            self.friendGameObject.startGame()
                            return

                        if user.code == int(code) and user.mentionID == self.mentionID:
                            vk.messages.send(
                                peer_id=self.mentionID,
                                message=f"Извини, /ударение не поддерживает игры с самим собой. Для этого есть режим 'Одиночная игра'.",
                                random_id=random.getrandbits(32),
                            )
                            return

                        if (
                            user.code == int(code)
                            and user.getGameIsActiveStatus() is True
                        ):
                            vk.messages.send(
                                peer_id=self.mentionID,
                                message=f"Этот игрок уже с кем-то играет.",
                                random_id=random.getrandbits(32),
                            )
                            return
                    vk.messages.send(
                        peer_id=self.mentionID,
                        message=f"Ой, мы не смогли найти такой код!",
                        random_id=random.getrandbits(32),
                    )
                else:
                    vk.messages.send(
                        peer_id=self.mentionID,
                        message=f"Некорректный код. Код может состоять только из четырех цифр. Нажми на кнопку 'Ввести код', чтобы заново ввести код.",
                        random_id=random.getrandbits(32),
                    )
                    return

        def enterCode(self):
            self.dataCollectionMode = True
            vk.messages.send(
                peer_id=self.mentionID,
                message=f"Введи код, который сообщил тебе друг:",
                random_id=random.getrandbits(32),
            )

        def friendGame(self):
            vk.messages.send(
                peer_id=self.mentionID,
                message=f"Что ты хочешь сделать:",
                random_id=random.getrandbits(32),
                keyboard=selectFriendGameKeyboard.get_keyboard(),
            )

        def backToMain(self):
            self.dataCollectionMode = False
            vk.messages.send(
                peer_id=self.mentionID,
                message=f"Ты вернулся назад.",
                random_id=random.getrandbits(32),
                keyboard=startGameKeyboard.get_keyboard(),
            )

    server = Server()
    server.connectToVKApi()
    vk_session, vk, longpoll = server.vk_session, server.vk, server.longpoll
    upload = VkUpload(vk_session)
    Thread(target=server.checkCodeDuration).start()

    def userIsExisting(mentionID):
        for user in existingUsers.values():
            if user.mentionID == mentionID:
                return user
        user = User(mentionID)
        existingUsers[mentionID] = User(mentionID)
        return user

    def eventHandler(event):
        try:
            if event.type == VkBotEventType.GROUP_LEAVE:
                server.leaveUserEvent(event.obj["user_id"])
            elif event.type == VkBotEventType.MESSAGE_NEW:
                thread = rThread(
                    target=userIsExisting, args=(event.obj.message["from_id"],)
                )
                thread.start()
                user = thread.join()
                Thread(
                    target=user.callAvailableCommands,
                    args=(event.obj.message["text"], event.obj.message["from_id"],),
                ).start()
        except:
            pass

    if longpoll is not None:
        for event in longpoll.listen():
            try:
                Thread(target=eventHandler, args=(event,)).start()
            except:
                pass

except:
    print("Хоба, ошибка!")
