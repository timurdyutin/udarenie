from vk_api.keyboard import VkKeyboard, VkKeyboardColor

startGameKeyboard = VkKeyboard(one_time=False)
startGameKeyboard.add_button("Одиночная игра", color=VkKeyboardColor.PRIMARY)
startGameKeyboard.add_line()
startGameKeyboard.add_button("Случайная игра", color=VkKeyboardColor.PRIMARY)
startGameKeyboard.add_line()
startGameKeyboard.add_button("Сыграть с другом", color=VkKeyboardColor.POSITIVE)

selectFriendGameKeyboard = VkKeyboard(one_time=False)
selectFriendGameKeyboard.add_button("Ввести код", color=VkKeyboardColor.PRIMARY)
selectFriendGameKeyboard.add_button("Создать игру", color=VkKeyboardColor.PRIMARY)
selectFriendGameKeyboard.add_line()
selectFriendGameKeyboard.add_button("Вернуться назад", color=VkKeyboardColor.NEGATIVE)

cancelSearchUserKeyboard = VkKeyboard(one_time=False)
cancelSearchUserKeyboard.add_button("Отменить поиск", color=VkKeyboardColor.NEGATIVE)

