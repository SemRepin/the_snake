import random as rnd
from typing import Optional

import pygame as pg

# Константы типов
RGB = tuple[int, int, int]
COORDINATES = tuple[int, int]

# Константы для размеров поля и сетки:
SCREEN_WIDTH: int = 640
SCREEN_HEIGHT: int = 480
GRID_SIZE: int = 20
GRID_WIDTH: int = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT: int = SCREEN_HEIGHT // GRID_SIZE
CENTRE_PONIT: COORDINATES = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))

# Направления движения:
UP: COORDINATES = (0, -1)
DOWN: COORDINATES = (0, 1)
LEFT: COORDINATES = (-1, 0)
RIGHT: COORDINATES = (1, 0)

# Константы цветов
BASE_COLOR: RGB = (1, 2, 3)
BOARD_BACKGROUND_COLOR: RGB = (0, 0, 0)
BORDER_COLOR: RGB = (93, 216, 228)
APPLE_COLOR: RGB = (255, 0, 0)
SNAKE_COLOR: RGB = (0, 255, 0)

# Скорость движения змейки:
SPEED = 10

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Настройка времени:
clock = pg.time.Clock()


# Тут опишите все классы игры.
class GameObject:
    """Базовый класс для игровых объектов."""

    position: COORDINATES
    body_color: RGB

    def __init__(self, position: COORDINATES = CENTRE_PONIT,
                 body_color: RGB = BASE_COLOR) -> None:
        """Инициализирует базовые атрибуты объекта позицию и цвет."""
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Заготовка для метода draw."""
        raise NotImplementedError("Метод должен использоваться наследниками.")


class Apple(GameObject):
    """Класс, описывающий яблоко и действия с ним."""

    def __init__(self, occupied_positions: Optional[list[COORDINATES]] = None,
                 position: COORDINATES = CENTRE_PONIT,
                 body_color: RGB = BASE_COLOR) -> None:
        """Задает цвет яблока и устанавливает позицию на экране."""
        occupied_positions = occupied_positions or [CENTRE_PONIT]
        super().__init__(position=CENTRE_PONIT, body_color=APPLE_COLOR)
        self.randomize_position(occupied_positions)
        # При использовании оператора | в init ругается pytest

    def randomize_position(self,
                           occupied_positions: list[COORDINATES]) -> None:
        """Рандомизирует позицию яблока на экране."""
        while True:
            new_position: COORDINATES = (
                rnd.randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                rnd.randint(0, GRID_HEIGHT - 1) * GRID_SIZE)

            # Проверяем, чтобы яблоко не заспавнилось в теле змейки
            if new_position not in occupied_positions:
                self.position = new_position
                break

    def draw(self) -> None:
        """Отрисовывает яблоко на экране."""
        rect = pg.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс, описывающий змейку и её поведение."""

    length: int
    positions: list[COORDINATES]
    direction: COORDINATES
    next_direction: Optional[COORDINATES]

    def __init__(self, position: COORDINATES = CENTRE_PONIT,
                 body_color: RGB = BASE_COLOR) -> None:
        """Инициализирует начальное состояние змейки."""
        super().__init__(position=CENTRE_PONIT, body_color=SNAKE_COLOR)
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None

    def update_direction(self) -> None:
        """Обновляет направление движения змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self) -> None:
        """Обновляет позицию змейки."""
        x, y = self.get_head_position()
        dx, dy = self.direction
        new_head = ((x + dx * GRID_SIZE) % SCREEN_WIDTH,
                    (y + dy * GRID_SIZE) % SCREEN_HEIGHT)

        # Вставляем новую голову в начало списка
        self.positions.insert(0, new_head)

        # Если змея не увеличилась, убираем последний сегмент
        if len(self.positions) > self.length:
            self.positions.pop()

    def draw(self) -> None:
        """Рисует змейку на экране."""
        for position in self.positions:
            rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, self.body_color, rect)
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def get_head_position(self) -> COORDINATES:
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def reset(self) -> None:
        """Сбрасывает змейку в начальное состояние."""
        self.length = 1
        self.positions = [self.position]
        self.direction = rnd.choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None


def handle_keys(snake: Snake) -> None:
    """Функция обработки действий пользователя."""
    key_directions: dict[int, COORDINATES] = {
        pg.K_UP: UP,
        pg.K_DOWN: DOWN,
        pg.K_LEFT: LEFT,
        pg.K_RIGHT: RIGHT,
    }

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            new_direction = key_directions.get(event.key)
            # Проверяем, чтобы змейка не реверсировала движение
            if new_direction and (
                new_direction[0] != -snake.direction[0]
                    or new_direction[1] != -snake.direction[1]):
                snake.next_direction = new_direction


def main() -> None:
    """Основной цикл игры."""
    # Инициализация PyGame:
    pg.init()
    snake: Snake = Snake()
    apple: Apple = Apple(snake.positions)
    max_length: int = 1

    while True:
        screen.fill(BOARD_BACKGROUND_COLOR)
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        # Проверяем съела ли змейка яблоко
        if snake.get_head_position() == apple.position:
            snake.length += 1
            max_length = max(max_length, snake.length)
            apple.randomize_position(snake.positions)

        # Проверяем врезалась ли змейка в себя
        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()

        # Заголовок окна игрового поля:
        pg.display.set_caption(f'Змейка - Скорость: {SPEED} '
                               f'| Рекорд: {max_length} '
                               '| Для выхода закройте окно курсором мыши')

        # Рисуем змейку и яблоко
        snake.draw()
        apple.draw()
        pg.display.update()
        clock.tick(SPEED)


if __name__ == '__main__':
    main()
