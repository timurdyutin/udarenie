from vk_api.keyboard import VkKeyboard, VkKeyboardColor

startGameKeyboard = VkKeyboard(one_time=False)
startGameKeyboard.add_button("Начать игру", color=VkKeyboardColor.PRIMARY)