from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import time 
userMainKeyboard = VkKeyboard(one_time=False)
userMainKeyboard.add_button("Одиночная игра", color=VkKeyboardColor.PRIMARY)
userMainKeyboard.add_line()
userMainKeyboard.add_button("Случайная игра", color=VkKeyboardColor.PRIMARY)
userMainKeyboard.add_line()
userMainKeyboard.add_button("Сыграть с другом", color=VkKeyboardColor.POSITIVE)

teacherMainKeyboard = VkKeyboard(one_time=False)
teacherMainKeyboard.add_button("Одиночная игра", color=VkKeyboardColor.PRIMARY)
teacherMainKeyboard.add_line()
teacherMainKeyboard.add_button("Случайная игра", color=VkKeyboardColor.PRIMARY)
teacherMainKeyboard.add_line()
teacherMainKeyboard.add_button("Сыграть с другом", color=VkKeyboardColor.POSITIVE)
teacherMainKeyboard.add_line()
teacherMainKeyboard.add_button("Создать тест", color=VkKeyboardColor.DEFAULT)

selectFriendGameKeyboard = VkKeyboard(one_time=False)
selectFriendGameKeyboard.add_button("Ввести код", color=VkKeyboardColor.PRIMARY)
selectFriendGameKeyboard.add_button("Создать игру", color=VkKeyboardColor.PRIMARY)
selectFriendGameKeyboard.add_line()
selectFriendGameKeyboard.add_button("Вернуться назад", color=VkKeyboardColor.NEGATIVE)

friendGameCreatorKeyboard = VkKeyboard(one_time=False)
friendGameCreatorKeyboard.add_button("Начать игру", color=VkKeyboardColor.POSITIVE)
friendGameCreatorKeyboard.add_button("Удалить игру", color=VkKeyboardColor.NEGATIVE)

friendGameUserKeyboard = VkKeyboard(one_time=False)
friendGameUserKeyboard.add_button("Выйти из ожидания", color=VkKeyboardColor.NEGATIVE)

selectRoleKeyboard = VkKeyboard(one_time=False)
selectRoleKeyboard.add_button("Я ученик", color=VkKeyboardColor.PRIMARY)
selectRoleKeyboard.add_button("Я учитель", color=VkKeyboardColor.PRIMARY)

cancelSearchUserKeyboard = VkKeyboard(one_time=False)
cancelSearchUserKeyboard.add_button("Отменить поиск", color=VkKeyboardColor.NEGATIVE)

a = 1


