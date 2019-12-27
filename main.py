# -*- coding: utf-8 -*-

import random
import time
from threading import Thread

import vk_api
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

existingUsers = []

words = {'алкоголь': 'алкогОль', 'алфавит': 'алфавИт', 'аристократия': 'аристокрАтия', 'балованный': 'балОванный', 'баловать': 'баловАть', 'бензопровод': 'бензопровОд', 'бряцание': 'бряцАние', 'буксировать': 'буксИровать', 'буржуазия': 'буржуазИя', 'вечеря': 'вЕчеря', 'втридорога': 'втрИдорога', 'газопровод': 'газопровОд', 'гусеничный': 'гУсеничный', 'дефис': 'дефИс', 'диспансер': 'диспансЕр', 'добела': 'добелА', 'добыча': 'добЫча', 'договор': 'договОр', 'документ': 'докумЕнт', 'донельзя': 'донЕльзя', 'донизу': 'дОнизу', 'доска': 'доскА', 'дремота': 'дремОта', 'единовременный': 'единоврЕменный', 'жаловать': 'жАловать', 'жалюзи': 'жалюзИ', 'жаровенный': 'жарОвенный', 'завидно': 'завИдно', 'загнутый': 'зАгнутый', 'заговор': 'зАговор', 'загодя': 'зАгодя', 'закупорить': 'закУпорить', 'запломбировать': 'запломбировАть', 'знамение': 'знАмение', 'зубчатый': 'зубчАтый', 'избалованный': 'избалОванный', 'иконопись': 'Иконопись', 'индустрия': 'индустрИя', 'исповедание': 'исповЕдание', 'исчерпать': 'исчЕрпать', 'камбала': 'кАмбала', 'кардиган': 'кардигАн', 'каталог': 'каталОг', 'квартал': 'квартАл', 'кедровый': 'кедрОвый', 'километр': 'киломЕтр', 'кожух': 'кожУх', 'коклюш': 'коклЮш', 'корысть': 'корЫсть', 'костюмированный': 
'костюмирОванный', 'красивее': 'красИвее', 'кровоточить': 'кровоточИть', 'кухонный': 'кУхонный', 'ламинировать': 'ламинИровать', 'лацкан': 'лАцкан', 'ломота': 'ломОта', 'мантра': 'мАнтра', 'мастерски': 'мастерскИ', 'метрополитен': 'метрополитЕн', 'мозаичный': 'мозаИчный', 'мусоропровод': 'мусоропровОд', 'набок': 'нАбок', 'надолго': 'надОлго', 'намерение': 'намЕрение', 'нарочито': 'нарочИто', 'начатый': 'нАчатый', 'нефтепровод': 'нефтепровОд', 'облегчить': 'облегчИть', 'оксюморон': 'оксЮморон', 'опошлить': 'опОшлить', 'оптовый': 'оптОвый', 'осведомить': 'освЕдомить', 'откупорить': 'откУпорить', 'отрочество': 'Отрочество', 'партер': 'партЕр', 'переходник': 'переходнИк', 'плодоносить': 'плодоносИть', 'пломбировать': 'пломбировАть', 'пломбировщик': 'пломбирОвщик', 'понявший': 'понЯвший', 'понятый': 'пОнятый', 'портфель': 'портфЕль', 'премировать': 'премировАть', 'принудить': 'принУдить', 'гербы': 'гербЫ', 'путепровод': 'путепровОд', 'равно': 
'равнО', 'разоружить': 'разоружИть', 'рубчатый': 'рУбчатый', 'сакура': 'сАкура', 'силос': 'сИлос', 'сливовый': 'слИвовый', 'сосредоточение': 'сосредотОчение', 'столяр': 'столЯр', 'телепатия': 'телепАтия', 'трансфер': 'трансфЕр', 'убыть': 'убЫть', 'углубить': 'углубИть', 'удобрить': 'удОбрить', 'украинский': 'украИнский', 'феномен': 'фенОмен', 'фетиш': 'фетИш', 'хвоя': 'хвОя', 'ходатайство': 'ходАтайство', 'ходатайствовать': 'ходАтайствовать', 'хребет': 'хребЕт', 'христианин': 'христианИн', 'цемент': 'цемЕнт', 'центнер': 'цЕнтнер', 'цепочка': 'цепОчка', 'черпать': 'чЕрпать', 'шаровой': 'шаровОй', 'щавель': 'щавЕль', 'экскурс': 'Экскурс', 'эпиграф': 'эпИграф', 'торты': 'тОрты', 'банты': 'бАнты', 'аниме': 'анимЕ', 'воры': 'вОры', 'взята': 'взятА', 'договоры': 'договОры', 'занята': 'занятА', 'кремы': 'крЕмы', 'кремов': 'крЕмов', 'латте': 'лАтте', 'начался': 'началсЯ', 'обняли': 'Обняли', 'средства': 'срЕдства', 'подняли': 'пОдняли', 'шарфы': 
'шАрфы', 'снята': 'снятА', 'ногтя': 'нОгтя', 'черпая': 'чЕрпая', 'снабжена': 'снабженА', 'лгала': 'лгалА', 'сверлит': 'сверлИт', 'включим': 'включИм', 'прибыла': 'прибылА', 'начавшись': 'начАвшись', 'бомжи': 'бОмжи', 'лекторов': 'лЕкторов', 'продал': 'прОдал', 'вручат': 'вручАт', 'маршмеллоу': 'маршмЕллоу', 'рандомный': 'рандОмный', 'стригу': 'стригУ', 'средствами': 'срЕдствами', 'грунтовы': 'грунтОвы'} 
vowels = "яёыуаеиоэю"
successMessages = ["Так точно,", "Да,", "Правильно,", "Всё верно,", "Так держать,"]
failureMessages = ["Неаю", "Нет, не так.", "Неверно", "Не огорчай меня.", "Неправильно.", "Ой, неправильно."]


availableCommands = ["Начать", "Начать игру", "Выйти из игры"]

startGameKeyboard = VkKeyboard(one_time=False)
startGameKeyboard.add_button("Начать игру", color=VkKeyboardColor.PRIMARY)

class ThreadWithReturnValue(Thread):
    def __init__(
        self, group=None, target=None, name=None, args=(), kwargs={}, Verbose=None
    ):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, *args):
        Thread.join(self, *args)
        return self._return

class Server:
    def __init__(self, token, groupID, databaseName):
        self.token = token
        self.groupID = groupID

    def connectToVKApi(self):
        vk_session = vk_api.VkApi(token=self.token)
        vk = vk_session.get_api()
        longpoll = VkBotLongPoll(vk_session, self.groupID)
        return vk_session, vk, longpoll
    

class User:
    def __init__(self, mentionID):
        self.mentionID = mentionID
        self.gameIsActive = False
        self.selectWordKeyboard = VkKeyboard(one_time=False)
        self.word = None
        self.rightWord = None
        self.wrongWords = []
        
    def callAvailableCommands(self, request):
        availableCommands = {
            "Начать": self.sendIntroductionMessage,
            "Начать игру": self.startGame,
            "Выйти из игры": self.quitGame}
        if (self.gameIsActive is True or self.gameIsActive is False) and request in availableCommands:
            availableCommands[request]()
        if self.gameIsActive is True and request not in availableCommands:
            self.checkAnswer(request)
        if self.gameIsActive is False and request not in availableCommands:
            vk.messages.send(
                        peer_id=self.mentionID,
                        message="Ой, я тебе не понимаю :(",
                        random_id=random.getrandbits(32),
                        keyboard = startGameKeyboard.get_keyboard()
                    )
            return
        
    def sendIntroductionMessage(self):
        vk.messages.send(
                        peer_id=self.mentionID,
                        message="О, привет! \n Хочешь начать играть? Нажми на кнопку 'Начать игру'!",
                        random_id=random.getrandbits(32),
                        keyboard = startGameKeyboard.get_keyboard()
                    )
        
    def startGame(self):
        if self.gameIsActive is True:
            vk.messages.send(
                        peer_id=self.mentionID,
                        message="Ты уже начал играть со мной. \n Хочешь выйти? Нажми на кнопку 'Выйти из игры'",
                        random_id=random.getrandbits(32),
                        keyboard = startGameKeyboard.get_keyboard()
                    )
        else:
            self.gameIsActive = True
            self.generateWord()
            vk.messages.send(
                        peer_id=self.mentionID,
                        message=f"Поставьте ударение в слове '{''.join(self.word)}''",
                        random_id=random.getrandbits(32),
                        keyboard=self.selectWordKeyboard.get_keyboard()
                    )
    
            
    def quitGame(self):
        if self.gameIsActive is False:
            vk.messages.send(
                        peer_id=self.mentionID,
                        message=f"Нельзя выйти оттуда, где ты никогда не был. \n (C) Физика",
                        random_id=random.getrandbits(32),
                        keyboard=startGameKeyboard.get_keyboard()
                    )
        else:
            self.gameIsActive = False
            vk.messages.send(
                            peer_id=self.mentionID,
                            message=f"Ты вышел из игры. Надеемся, что ты вернёшься!",
                            random_id=random.getrandbits(32),
                            keyboard=startGameKeyboard.get_keyboard()
                        )
        
            
    def generateWord(self):
        self.selectWordKeyboard = VkKeyboard(one_time=False)    
        self.word = random.choice(list(words.keys()))
        self.rightWord = words[self.word]
        self.word = list(self.word)
        for i in range(len(self.word)):
            if self.word[i] in vowels:
                self.word[i] = self.word[i].upper()
                print("".join(self.word))
                self.wrongWords.append("".join(self.word))
                self.selectWordKeyboard.add_button("".join(self.word), color=VkKeyboardColor.PRIMARY)
                self.selectWordKeyboard.add_line()
                self.word[i] = self.word[i].lower()
        self.selectWordKeyboard.add_button("Выйти из игры", color=VkKeyboardColor.NEGATIVE)
        
    def checkAnswer(self, word):
        if word == self.rightWord:
            vk.messages.send(
                        peer_id=self.mentionID,
                        message=f"{random.choice(successMessages)} ударение в слове {self.rightWord} падает на {self.rightWord.index([symbol for symbol in self.rightWord if symbol.isupper() is True][0]) + 1} букву",
                        random_id=random.getrandbits(32),
                        keyboard = self.selectWordKeyboard.get_keyboard()
                            )    
            self.gameIsActive = False
            self.startGame()
        else:
            vk.messages.send(
                        peer_id=self.mentionID,
                        message=f"{random.choice(failureMessages)}",
                        random_id=random.getrandbits(32),
                        keyboard = self.selectWordKeyboard.get_keyboard()
                            )    
            
            
        
        
server = Server(
    token="70cb1f8026e1adf42d7e9534edab8c8ca8e6c0796f23fa71ab338f196b7f2d853182b179d13c97f179acf",
    groupID="186661962",
    databaseName="usersDB.db",
)
vk_session, vk, longpoll = server.connectToVKApi()

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
            print(event.obj.message["text"])
            thread = ThreadWithReturnValue(
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
        Thread(target=eventHandler, args=(event,)).start()
    except:
        pass