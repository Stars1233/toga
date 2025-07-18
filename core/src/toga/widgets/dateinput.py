from __future__ import annotations

import datetime
from typing import Any, Protocol

import toga
from toga.handlers import wrapped_handler

from .base import StyleT, Widget

# This accommodates the ranges of all existing implementations:
#  * datetime.date: 1 - 9999
#  * Android: approx 5,800,000 BC - 5,800,000
#  * Windows: 1753 - 9998
MIN_DATE = datetime.date(1800, 1, 1)
MAX_DATE = datetime.date(8999, 12, 31)


class OnChangeHandler(Protocol):
    def __call__(self, widget: DateInput, **kwargs: Any) -> None:
        """A handler that will be invoked when a change occurs.

        :param widget: The DateInput that was changed.
        :param kwargs: Ensures compatibility with arguments added in future versions.
        """


class DateInput(Widget):
    _MIN_WIDTH = 200

    def __init__(
        self,
        id: str | None = None,
        style: StyleT | None = None,
        value: datetime.date | None = None,
        min: datetime.date | None = None,
        max: datetime.date | None = None,
        on_change: toga.widgets.dateinput.OnChangeHandler | None = None,
        **kwargs,
    ):
        """Create a new DateInput widget.

        :param id: The ID for the widget.
        :param style: A style object. If no style is provided, a default style
            will be applied to the widget.
        :param value: The initial date to display. If not specified, the current date
            will be used.
        :param min: The earliest date (inclusive) that can be selected.
        :param max: The latest date (inclusive) that can be selected.
        :param on_change: A handler that will be invoked when the value changes.
        :param kwargs: Initial style properties.
        """
        super().__init__(id, style, **kwargs)

        self.on_change = None
        self.min = min
        self.max = max

        self.value = value
        self.on_change = on_change

    def _create(self) -> Any:
        return self.factory.DateInput(interface=self)

    @property
    def value(self) -> datetime.date:
        """The currently selected date. A value of ``None`` will be converted into
        today's date.

        If this property is set to a value outside of the min/max range, it will be
        clipped.
        """
        return self._impl.get_value()

    @value.setter
    def value(self, value: object) -> None:
        value = self._convert_date(value, check_range=False)

        if value < self.min:
            value = self.min
        elif value > self.max:
            value = self.max

        self._impl.set_value(value)

    def _convert_date(self, value: object, *, check_range: bool) -> datetime.date:
        if value is None:
            value = datetime.date.today()
        elif isinstance(value, datetime.datetime):
            value = value.date()
        elif isinstance(value, datetime.date):
            pass
        elif isinstance(value, str):
            value = datetime.date.fromisoformat(value)
        else:
            raise TypeError("Not a valid date value")

        if check_range:
            if value < MIN_DATE:
                raise ValueError(f"The lowest supported date is {MIN_DATE.isoformat()}")
            if value > MAX_DATE:
                raise ValueError(
                    f"The highest supported date is {MAX_DATE.isoformat()}"
                )

        return value

    @property
    def min(self) -> datetime.date:
        """The minimum allowable date (inclusive). A value of ``None`` will be converted
        into the lowest supported date of 1800-01-01.

        When setting this property, the current :attr:`value` and :attr:`max` will be
        clipped against the new minimum value.

        :raises ValueError: If set to a date outside of the supported range.
        """
        return self._impl.get_min_date()

    @min.setter
    def min(self, value: object) -> None:
        if value is None:
            min = MIN_DATE
        else:
            min = self._convert_date(value, check_range=True)

        if self.max < min:
            self._impl.set_max_date(min)
        self._impl.set_min_date(min)
        if self.value < min:
            self.value = min

    @property
    def max(self) -> datetime.date:
        """The maximum allowable date (inclusive). A value of ``None`` will be converted
        into the highest supported date of 8999-12-31.

        When setting this property, the current :attr:`value` and :attr:`min` will be
        clipped against the new maximum value.

        :raises ValueError: If set to a date outside of the supported range.
        """
        return self._impl.get_max_date()

    @max.setter
    def max(self, value: object) -> None:
        if value is None:
            max = MAX_DATE
        else:
            max = self._convert_date(value, check_range=True)

        if self.min > max:
            self._impl.set_min_date(max)
        self._impl.set_max_date(max)
        if self.value > max:
            self.value = max

    @property
    def on_change(self) -> OnChangeHandler:
        """The handler to invoke when the date value changes."""
        return self._on_change

    @on_change.setter
    def on_change(self, handler: toga.widgets.dateinput.OnChangeHandler) -> None:
        self._on_change = wrapped_handler(self, handler)
