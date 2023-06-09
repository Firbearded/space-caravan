import pygame

from geometry.point import Point, tuple_to_point


class ControllerStrategy:
    """
    Базовый класс стратегии контроллера по обработке события.
    """

    def execute(self, controller, event):
        """
        Исполнить стратегию.

        :param controller: исполняющий контроллер
        :param event: событие
        """
        pass


class StrategyQuit(ControllerStrategy):
    """
    Обработка закрытия окна игры.
    """

    def execute(self, controller, event):
        print('Пользователь нажал крестик')
        controller.game.end()


class StrategyMouseMotion(ControllerStrategy):
    """
    Обработка движения мыши.
    """

    def execute(self, controller, event):
        controller.mouse_pos = tuple_to_point(event.pos)


class StrategyMouseDown(ControllerStrategy):
    """
    Обработка щелчка мышью.
    """

    def execute(self, controller, event):
        controller.click_pos = tuple_to_point(event.pos)
        controller.click_button = event.button


class StrategyKeyDown(ControllerStrategy):
    """
    Обработка нажатия клавиши.
    """

    def execute(self, controller, event):
        if event.key not in controller.pressed_keys:
            controller.pressed_keys.add(event.key)
        controller.bumped_key = event.key


class StrategyKeyUp(ControllerStrategy):
    """
    Обработка отпускания клавиши.
    """

    def execute(self, controller, event):
        if event.key in controller.pressed_keys:
            controller.pressed_keys.remove(event.key)


class StrategyWindowResize(ControllerStrategy):
    """
    При изменении размера окна меняется game.width и game.height,
    при этом размер спрайтов остается тем же (за исключением меню).
    """

    def execute(self, controller, event):
        controller.game.size = event.size


class Controller:
    """
    Контроллер, обрабатывающий ввод со стороны пользователя: нажатия и отпускания клавиш, движение мыши, нажатия ее
    кнопок, а также закрытие окна игры.

    :param game: игра, которой создается контроллер
    """
    STRATEGIES = {
        pygame.QUIT: StrategyQuit(),
        pygame.MOUSEMOTION: StrategyMouseMotion(),
        pygame.MOUSEBUTTONDOWN: StrategyMouseDown(),
        pygame.KEYDOWN: StrategyKeyDown(),
        pygame.KEYUP: StrategyKeyUp(),
        pygame.VIDEORESIZE: StrategyWindowResize()
    }

    def __init__(self, game):
        self.game = game

        self.mouse_pos = Point()
        self.click_pos = None
        self.click_button = None
        self.pressed_keys = set()
        self.bumped_key = None

    def iteration(self):
        """
        Итерация работы контроллера.
        """
        self.click_pos = self.click_button = self.bumped_key = None
        event_list = pygame.event.get()
        for event in event_list:
            if event.type in Controller.STRATEGIES:
                Controller.STRATEGIES[event.type].execute(self, event)

    def get_mouse_pos(self):
        """
        :return: текущее положение мыши
        """
        return self.mouse_pos

    def get_click_pos(self):
        """
        :return: точка щелчка мыши (None, если на текущей итерации щелчка не было)
        """
        return self.click_pos

    def get_click_button(self):
        """
        :return: кнопка, которая была нажата на мыши (None, если на текущей итерации щелчка не было)
        """
        return self.click_button

    def is_key_pressed(self, key):
        """
        Нажата ли клавиша.

        :param key: код клавиши
        :return: логическое значение
        """
        return key in self.pressed_keys

    def is_mouse_pressed(self, button_id):
        """
        Нажата ли заданная кнопка мыши.

        :param button_id: ID кнопки в pygame
        :return: логическое значение
        """
        pressed = pygame.mouse.get_pressed()
        return bool(pressed[button_id - 1])

    def is_one_of_keys_pressed(self, keys):
        """
        Нажата ли хотя бы одна из клавиш.

        :param keys: массив кодов клавиш
        :return: логическое значение
        """
        b = 0
        for key in keys:
            b += self.is_key_pressed(key)
        return bool(b)

    def get_bumped_key(self):
        """
        :return: код клавиши, ставшей нажатой на текущей итерации (None, если ее нет)
        """
        return self.bumped_key
