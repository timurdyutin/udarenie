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
from messages import failureMessages, successMessages
from utils.rthread import rThread
from words import vowels, words


class singleGame:
    def __init__(self, mentionID):
        self.mentionID = mentionID
        self.selectWordKeyboard = VkKeyboard(one_time=False)
        self.words = []
        self.commands = {"Выйти из игры": self.quitGame}

    def commandExecutor(self, request):
        if request in self.commands.keys():
            self.commands[request]()
        else:
            self.checkAnswer(request)

    def generateWord(self):
        self.words = []
        self.selectWordKeyboard = VkKeyboard(one_time=False)
        choosedWord = random.choice(list(words.keys()))
        self.words.append(words[choosedWord])
        choosedWord = list(choosedWord)
        for i in range(len(choosedWord)):
            if choosedWord[i] in vowels:
                choosedWord[i] = choosedWord[i].upper()
                self.selectWordKeyboard.add_button(
                    "".join(choosedWord), color=VkKeyboardColor.DEFAULT
                )
                self.words.append("".join(choosedWord))
                self.selectWordKeyboard.add_line()
                choosedWord[i] = choosedWord[i].lower()
        self.selectWordKeyboard.add_button(
            "Выйти из игры", color=VkKeyboardColor.NEGATIVE
        )

    def checkAnswer(self, word):
        if word == self.words[0]:
            previosRightWord = self.words[0]
            self.generateWord()
            vk.messages.send(
                peer_id=self.mentionID,
                message=f"{random.choice(successMessages)} ударение в слове {previosRightWord} падает на {previosRightWord.index([symbol for symbol in previosRightWord if symbol.isupper() is True][0]) + 1} букву. \n\n Поставь ударение в слове \"{''.join(self.words[0].lower())}\"",
                random_id=random.getrandbits(32),
                keyboard=self.selectWordKeyboard.get_keyboard(),
            )
        else:
            if word in self.words[1::]:
                vk.messages.send(
                    peer_id=self.mentionID,
                    message=f"{random.choice(failureMessages)}",
                    random_id=random.getrandbits(32),
                    keyboard=self.selectWordKeyboard.get_keyboard(),
                )

    def quitGame(self):
        users[self.mentionID].singleGameMode = False
        users[self.mentionID].userMode = True
        vk.messages.send(
            peer_id=self.mentionID,
            message=f'Ты вышел из игры "Одиночная игра"',
            random_id=random.getrandbits(32),
            keyboard=users[self.mentionID].mainKeyboard.get_keyboard(),
        )

    def startGame(self):
        self.generateWord()
        vk.messages.send(
            peer_id=self.mentionID,
            message=f"Ты начал играть в режим \"Одиночная игра\", ставь ударение в словах, нажимая на кнопки, в которых указан верный вариант постановки ударения! \n\n Поставь ударение в слове '{self.words[0].lower()}'",
            random_id=random.getrandbits(32),
            keyboard=self.selectWordKeyboard.get_keyboard(),
        )

class friendGame(singleGame):
    def __init__(self, users):
        self.users = users
        self.firstMessageMode = True
        self.words = []
        self.stat = {}
        self.selectWordKeyboard = VkKeyboard(one_time=False)
        self.commands = {"Выйти из игры": self.quitGame}

    def commandExecutor(self, request, mentionID):
        if request in self.commands.keys():
            self.commands[request](mentionID)
        else:
            self.checkAnswer(request, mentionID)
            
    def generateWord(self):
        self.words = []
        self.selectWordKeyboard = VkKeyboard(one_time=False)
        choosedWord = random.choice(list(words.keys()))
        self.words.append(words[choosedWord])
        self.stat[choosedWord] = {user: [0, 0, 0] for user in self.users}
        choosedWord = list(choosedWord)
        for i in range(len(choosedWord)):
            if choosedWord[i] in vowels:
                choosedWord[i] = choosedWord[i].upper()
                self.selectWordKeyboard.add_button(
                    "".join(choosedWord), color=VkKeyboardColor.DEFAULT
                )
                self.words.append("".join(choosedWord))
                self.selectWordKeyboard.add_line()
                choosedWord[i] = choosedWord[i].lower()
        self.selectWordKeyboard.add_button(
            "Выйти из игры", color=VkKeyboardColor.NEGATIVE
        )

    def checkAnswer(self, word, mentionID):
        q = time.time()
        if word == self.words[0]:
            self.stat[word.lower()][mentionID] = [1, q, 10 * (q / 10)]
        else:
            if word in self.words[1::]:
                self.stat[word.lower()][mentionID] = [0, q, 0]
                
    def sendWordMessage(self): 
        vk.messages.send(
                user_ids=self.users,
                message=f"Поставь ударение в слове \"{''.join(self.words[0].lower())}\"",
                random_id=random.getrandbits(32),
                keyboard=self.selectWordKeyboard.get_keyboard(),
            )

    def startGame(self):
        print(self.users)
        vk.messages.send(
            user_ids=self.users,
            message=f"Ты начал играть в режим \"Игра с другом\", ставь ударение в словах, нажимая на кнопки, в которых указан верный вариант постановки ударения! На каждоё слово даётся по 5 секунд времени. \n\n Чем быстрее ты ответишь, тем больше баллов ты сможешь получить за верно определённое ударение!",
            random_id=random.getrandbits(32),
        )
        Thread(target=self.game).start()
        
    def getIntermediateResult(self):
        rightAnswers, wrongAnswer, wtAnswers = [[], [], []]
        for user, result in self.stat[self.words[0].lower()].items(): 
            if result[2] == 0:
                if result[1] == 0:
                    wtAnswers.append(user)
                else:
                    wrongAnswer.append(user)
            else:
                rightAnswers.append(user)
        self.sendResultsMessage(rightAnswers, wrongAnswer, wtAnswers)
    
    def sendResultsMessage(self, rightAnswers, wrongAnswer, wtAnswers):
        if len(rightAnswers) != 0:
            vk.messages.send(
                user_ids=rightAnswers,
                message=f"Поздравляем! Ты правильно ответил.",
                random_id=random.getrandbits(32),
            )
        elif len(wrongAnswer) != 0:
            vk.messages.send(
                user_ids=wrongAnswer,
                message=f"Нет, неправильно.",
                random_id=random.getrandbits(32),
            )  
        elif len(wtAnswers) != 0:
            vk.messages.send(
            user_ids=wtAnswers,
            message=f"Ты не ответил.",
            random_id=random.getrandbits(32),
            )   
        
    def getFinalResult(self):
        pass

    def game(self):
        for i in range(1, 5):
            self.generateWord()
            self.sendWordMessage()
            time.sleep(5)
            self.getIntermediateResult()
        self.getFinalResult()
        self.quitGameAllUsers()
            
        
    def quitGameAllUsers(self):
        students = []
        teachers = []
        for user in self.users:
            users[user].code = None 
            users[user].userMode = True 
            users[user].friendGameObject = None
            users[user].friendGameMode = False
            if str(users[user]) == "teacher": 
                teachers.append(user)
            else:
                students.append(user)
        if len(users) != 0:
            vk.messages.send(
                peer_id=students,
                message=f"Ты вышел из игры.",
                random_id=random.getrandbits(32),
                keyboard=users[students[0]].mainKeyboard.get_keyboard())
        elif len(teachers) != 0:
            vk.messages.send(peer_id=students, message=f"Ты вышел из игры.", random_id=random.getrandbits(32), keyboard=users[teachers[0]].mainKeyboard.get_keyboard())
            
    def quitGame(self, mentionID):
        users[mentionID].code = None 
        users[mentionID].userMode = True 
        users[mentionID].friendGameObject = None
        users[mentionID].friendGameMode = False
        self.users.remove(mentionID)
        vk.messages.send(
            peer_id=mentionID,
            message=f"Ты вышел из игры \"Игра с другом\"",
            random_id=random.getrandbits(32),
            keyboard=users[mentionID].mainKeyboard.get_keyboard())
        vk.messages.send(
            peer_id=self.users,
            message=f"Игрок {mentionID} решил выйти из игры.",
            random_id=random.getrandbits(32))
    