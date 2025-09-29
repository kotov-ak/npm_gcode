from dataclasses import dataclass
from typing import Optional, Union
from enum import Enum


class CommandType(Enum):
    """Типы команд G-кода"""
    LINEAR_MOVE = "G01"  # Линейное движение
    M_CODE = "M"        # M-код (например M110)
    PAUSE = "G04"       # Пауза


@dataclass
class MotionCommand:
    """
    Структурированная команда движения для станка

    Attributes:
        command_type (CommandType): Тип команды
        x (Optional[float]): Позиция по оси X в мм
        y (Optional[float]): Позиция по оси Y в мм
        z (Optional[float]): Позиция по оси Z в мм
        a (Optional[float]): Угол поворота по оси A в градусах
        feed_rate (Optional[float]): Скорость подачи в мм/мин
        m_code (Optional[int]): Номер M-кода (например, 110 для M110)
        pause_time (Optional[float]): Время паузы в секундах для G04
        comment (Optional[str]): Комментарий к команде
    """
    command_type: CommandType
    x: Optional[float] = None
    y: Optional[float] = None
    z: Optional[float] = None
    a: Optional[float] = None
    feed_rate: Optional[float] = None
    m_code: Optional[int] = None
    pause_time: Optional[float] = None
    comment: Optional[str] = None

    def __post_init__(self):
        """Валидация параметров команды"""
        if self.command_type == CommandType.LINEAR_MOVE:
            pass
            # if self.feed_rate is None:
            #     raise ValueError("Команда G01 требует указания скорости feed_rate")

        elif self.command_type == CommandType.M_CODE:
            if self.m_code is None:
                raise ValueError("M-команда требует указания номера m_code")

        elif self.command_type == CommandType.PAUSE:
            if self.pause_time is None:
                raise ValueError("Команда паузы G04 требует указания времени pause_time")

    @classmethod
    def linear_move(cls, x: Optional[float] = None, y: Optional[float] = None,
                   z: Optional[float] = None, a: Optional[float] = None,
                   feed_rate: float = 1000, comment: Optional[str] = None) -> 'MotionCommand':
        """
        Создать команду линейного движения G01

        Args:
            x, y, z: Координаты в мм
            a: Угол поворота в градусах
            feed_rate: Скорость подачи в мм/мин
            comment: Комментарий

        Returns:
            MotionCommand: Команда линейного движения
        """
        return cls(
            command_type=CommandType.LINEAR_MOVE,
            x=x, y=y, z=z, a=a,
            feed_rate=feed_rate,
            comment=comment
        )

    @classmethod
    def m_code(cls, m_code: int, comment: Optional[str] = None) -> 'MotionCommand':
        """
        Создать M-команду

        Args:
            m_code: Номер M-кода
            comment: Комментарий

        Returns:
            MotionCommand: M-команда
        """
        return cls(
            command_type=CommandType.M_CODE,
            m_code=m_code,
            comment=comment
        )

    @classmethod
    def pause(cls, pause_time: float, comment: Optional[str] = None) -> 'MotionCommand':
        """
        Создать команду паузы G04

        Args:
            pause_time: Время паузы в секундах
            comment: Комментарий

        Returns:
            MotionCommand: Команда паузы
        """
        return cls(
            command_type=CommandType.PAUSE,
            pause_time=pause_time,
            comment=comment
        )

    def to_gcode_string(self) -> str:
        """
        Преобразовать команду в строку G-кода

        Returns:
            str: Строка G-кода
        """
        if self.command_type == CommandType.LINEAR_MOVE:
            parts = [self.command_type.value]

            if self.x is not None:
                parts.append(f"X{round(self.x, 3)}")
            if self.y is not None:
                parts.append(f"Y{round(self.y, 3)}")
            if self.z is not None:
                parts.append(f"Z{round(self.z, 3)}")
            if self.a is not None:
                parts.append(f"A{round(self.a, 3)}")
            if self.feed_rate is not None:
                parts.append(f"F{int(self.feed_rate)}")

            result = " ".join(parts)

        elif self.command_type == CommandType.M_CODE:
            result = f"M{self.m_code}"

        elif self.command_type == CommandType.PAUSE:
            result = f"G04 P{round(self.pause_time, 3)}"

        else:
            raise ValueError(f"Неизвестный тип команды: {self.command_type}")

        # Добавляем комментарий если есть
        # if self.comment:
        #     result += f" ; {self.comment}"

        return result

    def __str__(self) -> str:
        """Строковое представление команды"""
        return self.to_gcode_string()


# Специальные типы команд для удобства
class PunchCommands:
    """Фабричные методы для создания команд пробития"""

    @staticmethod
    def approach(x: float, y: float, z: float, feed_rate: float) -> MotionCommand:
        """Команда подхода к точке пробития"""
        return MotionCommand.linear_move(
            x=x, y=y, z=z, feed_rate=feed_rate,
            comment="Подход к точке пробития"
        )

    @staticmethod
    def punch(x: float, y: float, z: float, feed_rate: float) -> MotionCommand:
        """Команда пробития"""
        return MotionCommand.linear_move(
            x=x, y=y, z=z, feed_rate=feed_rate,
            # comment="Внедрение игл"
        )

    @staticmethod
    def retract(x: float, y: float, z: float, feed_rate: float) -> MotionCommand:
        """Команда Извлечение игла после пробития"""
        return MotionCommand.linear_move(
            x=x, y=y, z=z, feed_rate=feed_rate,
            # comment="Извлечение игл"
        )

    @staticmethod
    def rotate(angle: float, feed_rate: float) -> MotionCommand:
        """Команда поворота"""
        return MotionCommand.linear_move(
            a=angle, feed_rate=feed_rate,
            # comment="Поворот"
        )

    @staticmethod
    def waiting() -> MotionCommand:
        """Команда паузы для резки"""
        return MotionCommand.m_code(110, "Пауза для резки")