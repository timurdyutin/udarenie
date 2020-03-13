# -*- coding: utf-8 -*-
import random
import time
import tracemalloc
from threading import Thread
from requests import *
import vk_api
from vk_api import VkUpload
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import os
import schedule
from keyboards import (
    userMainKeyboard,
    teacherMainKeyboard,
    selectFriendGameKeyboard,
    cancelSearchUserKeyboard,
    selectRoleKeyboard,
    friendGameCreatorKeyboard,
    friendGameUserKeyboard,
)
from games import friendGame, singleGame
from messages import failureMessages, successMessages
from utils.rthread import rThread
from words import vowels, words

users = {}
codes = {}
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
            for user in users.values():
                if user.codeDuration != 0 and user.code is not None:
                    if time.time() - user.codeDuration > 60:
                        self.sendCodeIsExpiredMessage(user)

    def checkSearchDuration(self):
        while True:
            for user in users.values():
                if user.searchDuration != 0:
                    if time.time() - user.searchDuration > 10:
                        self.sendUserIsNotFoundMessage(user)

    def sendCodeIsExpiredMessage(self, user):
        vk.messages.send(
            peer_id=user.mentionID,
            message=f"Срок действия твоего кода: {user.code} истёк.",
            random_id=random.getrandbits(32),
        )
        user.codeDuration = None
        user.code = None

    def sendUserIsNotFoundMessage(self, user):
        vk.messages.send(
            peer_id=user.mentionID,
            message=f"Извини, мы не смогли никого найти для случайной игры с тобой.",
            random_id=random.getrandbits(32),
            keyboard=user.mainKeyboard.get_keyboard(),
        )
        user.searchDuration = 0
        user.searchRandomGameMode = False
        user.userMode = True

    def newUserEvent(self, mentionID):
        attachments = []
        image = open(r"udarenie/pictures/greeting_after_leaving.png", "rb")
        photo = upload.photo_messages(photos=image.raw)[0]
        attachments.append("photo{}_{}".format(photo["owner_id"], photo["id"]))
        vk.messages.send(
            random_id=random.randrange(32),
            peer_id=mentionID,
            message=f"{vk.users.get(user_ids=event.obj['user_id'])[0]['first_name']}, мы рады, что ты вернулся.",
            attachment=",".join(attachments),
        )

    def leaveUserEvent(self, mentionID):
        attachments = []
        image = open(
            r"udarenie/pictures/farewell_{}.PNG".format(random.choice(range(1, 3))),
            "rb",
        )
        photo = upload.photo_messages(photos=image.raw)[0]
        attachments.append("photo{}_{}".format(photo["owner_id"], photo["id"]))
        vk.messages.send(
            random_id=random.randrange(32),
            peer_id=mentionID,
            message=f"Пока, {vk.users.get(user_ids=event.obj['user_id'])[0]['first_name']}. \n /ударение будет скучать по тебе!",
            attachment=",".join(attachments),
        )

class friendGameAwaitRoom:
    def __init__(self):
        self.users = []
        self.creatorCommands = {
            "Удалить игру": self.removeGame,
            "Начать игру": self.startGame,
        }
        self.userCommands = {"Выйти из ожидания": self.quitAwaitRoom}
        self.friendGameCreatorKeyboard = friendGameCreatorKeyboard
        self.friendGameUserKeyboard = friendGameUserKeyboard

    def commandExecutor(self, request, mentionID):
        if request in self.creatorCommands.keys() or request in self.userCommands:
            if mentionID == self.users[0]:
                self.creatorCommands[request]()
            else:
                self.userCommands[request](mentionID)
        else:
            pass

    def sendFriendWasFoundMessage(self, mentionID):
        vk.messages.send(
            peer_id=self.users[0],
            message=f"{vk.users.get(user_ids=mentionID)[0]['first_name']} подключился к комнате ожидания! Ты уже можешь начать игру.",
            random_id=random.getrandbits(32),
            keyboard=self.friendGameCreatorKeyboard.get_keyboard(),
        )

        vk.messages.send(
            peer_id=mentionID,
            message=f"Ты подключился к комнате игрока {vk.users.get(user_ids=self.users[0])[0]['first_name']}.",
            random_id=random.getrandbits(32),
            keyboard=self.friendGameUserKeyboard.get_keyboard(),
        )

    def sendGameIsNotReadyMessage(self):
        vk.messages.send(
            peer_id=self.users[0],
            message=f"Недостаточно игроков для начала игры.",
            random_id=random.getrandbits(32),
            keyboard=self.friendGameCreatorKeyboard.get_keyboard(),
        )

    def sendGameWasRemovedMessage(self):
        for user in self.users[1::]:
            vk.messages.send(
                peer_id=users[user].mentionID,
                message=f"Ты был отключен от комнаты ожидания, потому что создатель комнаты решил удалить её.",
                random_id=random.getrandbits(32),
                keyboard=users[user].mainKeyboard.get_keyboard(),
            )

    def startGame(self):
        if len(self.users) >= 2:
            friendGameObject = friendGame(self.users)
            friendGameObject.startGame()
            for user in self.users:
                users[user].friendGameObject = friendGameObject
                users[user].friendGameAwaitRoomMode = False
                users[user].friendGameMode = True
                users[user].code = None
        else:
            self.sendGameIsNotReadyMessage()

    def removeGame(self):
        for user in self.users:
            users[user].code = None
            users[user].friendGameAwaitRoomMode = False
            users[user].friendGameAwaitRoomObject = None
            users[user].userMode = True
        vk.messages.send(
            peer_id=self.users[0],
            message=f"Ты удалил комнату ожидания игры.",
            random_id=random.getrandbits(32),
            keyboard=users[self.users[0]].mainKeyboard.get_keyboard(),
        )
        self.sendGameWasRemovedMessage()

    def quitAwaitRoom(self, mentionID):
        users[mentionID].friendGameAwaitRoomMode = False
        users[mentionID].userMode = True
        self.users.remove(mentionID)
        vk.messages.send(
            peer_id=mentionID,
            message=f"Ты вышел из комнаты ожидания.",
            random_id=random.getrandbits(32),
            keyboard=users[mentionID].mainKeyboard.get_keyboard(),
        )
        vk.messages.send(
            peer_id=self.users[0],
            message=f"Игрок {vk.users.get(user_ids=mentionID)[0]['first_name']} вышел из комнаты ожидания.",
            random_id=random.getrandbits(32),
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
        self.selectRoleMode = True
        self.friendGameAwaitRoomMode = False
        self.friendGameAwaitRoomObject = None
        self.userMode = True
        self.code = None
        self.mainKeyboard = None
        self.codeDuration = 0
        self.searchDuration = 0
        self.commands = {
            "Одиночная игра": self.singleGame,
            "Случайная игра": self.randomGame,
            "Сыграть с другом": self.friendGame,
            "Создать игру": self.generateCode,
            "Ввести код": self.enterCode,
            "Вернуться назад": self.backToMain,
            "Выйти из игры": self.quitGame,
            "Отменить поиск": self.cancelSearchRandomGame,
        }

    def commandExecutor(self, request, mentionID):
        if self.singleGameMode is True:
            self.singleGameObject.commandExecutor(request)
        elif self.friendGameMode is True:
            self.friendGameObject.commandExecutor(request, mentionID)
        elif self.randomGameMode is True:
            self.randomGameObject.commandExecutor(request, mentionID)
        elif self.friendGameAwaitRoomMode is True:
            self.friendGameAwaitRoomObject.commandExecutor(request, mentionID)
        elif self.dataCollectionMode is True:
            if request == "Вернуться назад" or request == "Создать игру":
                self.commands[request]()
            else:
                self.checkCode(request)
        elif self.searchRandomGameMode is True and request == "Отменить поиск":
            self.commands[request]()
        elif self.userMode is True:
            if request in self.commands:
                self.commands[request]()
            else:
                self.sendFailureMessage()

    def quitGame(self):
        vk.messages.send(
            peer_id=self.mentionID,
            message="Ты вернулся назад, в главное меню.",
            random_id=random.getrandbits(32),
            keyboard=self.mainKeyboard.get_keyboard(),
        )

    def sendFailureMessage(self):
        vk.messages.send(
            peer_id=self.mentionID,
            message="Извини, я тебя совсем не понимаю :(",
            random_id=random.getrandbits(32),
            keyboard=self.mainKeyboard.get_keyboard(),
        )

    def singleGame(self):
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
        self.searchDuration = time.time()
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
            if self.mentionID != users[randomGamesUsers[0]].mentionID:
                self.randomGameObject = randomGame(
                    self.mentionID, users[randomGamesUsers[0]].mentionID
                )
                users[randomGamesUsers[0]].randomGameObject = self.randomGameObject
                self.randomGameObject.startGame()
                self.userMode = False
                self.randomGameMode = True
                users[randomGamesUsers[0]].userMode = False
                users[randomGamesUsers[0]].randomGameMode = True
                randomGamesUsers.remove(randomGamesUsers[0])
        else:
            randomGamesUsers.append(self.mentionID)

    def generateCode(self):
        self.dataCollectionMode = False
        self.code = random.choice(range(1000, 10000))
        while self.code in codes.keys():
            self.code = random.choice(range(1000, 10000))
        self.codeDuration = time.time()
        self.friendGameAwaitRoomMode = True
        self.friendGameAwaitRoomObject = friendGameAwaitRoom()
        self.friendGameAwaitRoomObject.users.append(self.mentionID)
        vk.messages.send(
            random_id=random.randrange(32),
            peer_id=self.mentionID,
            message=f'Отправь этот код "{self.code}" своему другу, чтобы он смог присоединиться к комнате ожидания! \n\n Срок действия кода: 1 минута.',
            keyboard=friendGameCreatorKeyboard.get_keyboard(),
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
        if code not in self.commands.keys():
            if code.isdigit() is True and len(code) == 4:
                for user in users.values():
                    if (
                        user.code == int(code)
                        and user.mentionID != self.mentionID
                        and user.getGameIsActiveStatus() is False
                    ):
                        self.friendGameAwaitRoomMode = True
                        self.userMode = False
                        self.dataCollectionMode = False
                        self.friendGameAwaitRoomObject = user.friendGameAwaitRoomObject
                        user.friendGameAwaitRoomObject.users.append(self.mentionID)
                        user.friendGameAwaitRoomObject.sendFriendWasFoundMessage(
                            self.mentionID
                        )
                        return 

                    if user.code == int(code) and user.mentionID == self.mentionID:
                        vk.messages.send(
                            peer_id=self.mentionID,
                            message=f"Извини, /ударение не поддерживает игры с самим собой. Для этого есть режим 'Одиночная игра'.",
                            random_id=random.getrandbits(32),
                        )
                        return

                    if user.code == int(code) and user.getGameIsActiveStatus() is True:
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
                    message=f"Некорректный код. Код может состоять только из четырех цифр.",
                    random_id=random.getrandbits(32),
                )

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
            keyboard=self.mainKeyboard.get_keyboard(),
        )

    def __str__(self):
        return "user"


class Teacher(User):
    def __str__(self):
        return "teacher"


class undefinedRole:
    def __init__(self, mentionID):
        self.mentionID = mentionID
        self.commands = {
            "Я ученик": self.selectStudentRole,
            "Я учитель": self.selectTeacherRole,
            "Начать": self.start,
        }

    def commandExecutor(self, request, mentionID):
        if request in self.commands:
            self.commands[request]()
        else:
            self.sendRoleIsNotSelectedMessage()

    def start(self):
        vk.messages.send(
            peer_id=self.mentionID,
            message="Привет! \n\n Мы поможем тебе определить, в каких словах ты неправильно ставишь ударение. \n\n Чтобы начать играть, выбери свою роль:",
            random_id=random.getrandbits(32),
            keyboard=selectRoleKeyboard.get_keyboard(),
        )

    def selectTeacherRole(self):
        users[self.mentionID] = Teacher(self.mentionID)
        users[self.mentionID].mainKeyboard = teacherMainKeyboard
        users[self.mentionID].selectRoleMode = False
        vk.messages.send(
            peer_id=self.mentionID,
            message="Ты выбрал роль учителя. Учитель может создавать тесты для учеников, получать статистику прохождения тестов. \n\n Чтобы изменить свою роль, перейди в раздел 'Настройки' и нажми на кнопку 'Изменить роль'.",
            random_id=random.getrandbits(32),
            keyboard=users[self.mentionID].mainKeyboard.get_keyboard(),
        )

    def selectStudentRole(self):
        users[self.mentionID] = User(self.mentionID)
        users[self.mentionID].mainKeyboard = userMainKeyboard
        users[self.mentionID].selectRoleMode = False
        vk.messages.send(
            peer_id=self.mentionID,
            message="Ты выбрал роль ученика. \n\n Чтобы изменить свою роль, перейди в раздел 'Настройки' и нажми на кнопку 'Изменить роль'.",
            random_id=random.getrandbits(32),
            keyboard=users[self.mentionID].mainKeyboard.get_keyboard(),
        )

    def sendRoleIsNotSelectedMessage(self):
        vk.messages.send(
            peer_id=self.mentionID,
            message="Ой, ты не выбрал свою роль. Выбери прямо сейчас: ",
            random_id=random.getrandbits(32),
            keyboard=selectRoleKeyboard.get_keyboard(),
        )

    def __str__(self):
        return "undefinedRole"


server = Server()
server.connectToVKApi()
vk_session, vk, longpoll = server.vk_session, server.vk, server.longpoll
upload = VkUpload(vk_session)
Thread(target=server.checkCodeDuration).start()
Thread(target=server.checkSearchDuration).start()


def userIsExisting(mentionID):
    for user in users.values():
        if user.mentionID == mentionID:
            return user
    users[mentionID] = undefinedRole(mentionID)
    return users[mentionID]


def eventHandler(event):
    try:
        if event.type == VkBotEventType.GROUP_LEAVE:
            server.leaveUserEvent(event.obj["user_id"])
        elif event.type == VkBotEventType.GROUP_JOIN:
            server.newUserEvent(event.obj["user_id"])
        elif event.type == VkBotEventType.MESSAGE_NEW:
            thread = rThread(
                target=userIsExisting, args=(event.obj.message["from_id"],)
            )
            thread.start()
            user = thread.join()
            Thread(
                target=user.commandExecutor,
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
