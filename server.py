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
    token=token,
    groupID=groupID,
)
vk_session, vk, longpoll = server.connectToVKApi()
