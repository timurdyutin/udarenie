import vk_api
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from vk_api.keyboard import VkKeyboard, VkKeyboardColor


class Server:
    def __init__(self, token, groupID):
        self.token = token
        self.groupID = groupID

    def connectToVKApi(self):
        vk_session = vk_api.VkApi(token=self.token)
        vk = vk_session.get_api()
        longpoll = VkBotLongPoll(vk_session, self.groupID)
        return vk_session, vk, longpoll
    
server = Server(
    token="70cb1f8026e1adf42d7e9534edab8c8ca8e6c0796f23fa71ab338f196b7f2d853182b179d13c97f179acf",
    groupID="186661962",
)
vk_session, vk, longpoll = server.connectToVKApi()

