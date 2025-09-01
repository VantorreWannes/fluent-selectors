import os
from abc import ABC
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Optional, Union

from fluent_checks import Check, RaisesCheck
from selenium.common import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

type Locator = tuple[str, str]


@dataclass
class Location:
    x: int
    y: int


@dataclass
class Size:
    x: float
    y: float


class Selector(ABC):
    _SELF_LOCATOR: Locator = (By.XPATH, ".")
    _CHILDREN_LOCATOR: Locator = (By.XPATH, "./*")
    _HAS_ATTRIBUTE_SCRIPT = "return arguments[0].hasAttribute(arguments[1]);"
    _SCROLL_INTO_VIEW_SCRIPT = "arguments[0].scrollIntoView(true);"

    def __init__(self, driver: WebDriver, *locators: Locator) -> None:
        super().__init__()
        self.driver: WebDriver = driver
        self._locators: tuple[Locator, ...] = locators or (Selector._SELF_LOCATOR,)
        self._locator: Locator = self._locators[-1]

    @cached_property
    def locators(self) -> tuple[Locator, ...]:
        return self._locators

    @cached_property
    def parent(self) -> Optional["Selector"]:
        if len(self._locators) > 1:
            return Selector(self.driver, *self._locators[:-1])

    @cached_property
    def parents(self) -> list["Selector"]:
        if parent := self.parent:
            return [parent, *parent.parents]
        return []

    @cached_property
    def _context(self) -> Union[WebDriver, WebElement, None]:
        if self.parent:
            return self.parent.element
        return self.driver

    @property
    def element(self) -> Optional[WebElement]:
        try:
            context = self._context
            if context:
                return context.find_element(*self._locator)
            return None
        except NoSuchElementException:
            return None

    @property
    def elements(self) -> list[WebElement]:
        try:
            context = self._context
            if context:
                return context.find_elements(*self._locator)
            return []
        except NoSuchElementException:
            return []

    def select(self, locator: Locator) -> "Selector":
        return Selector(self.driver, *self._locators, locator)

    def child(self, index: int) -> "Selector":
        locator: Locator = (By.XPATH, f"({Selector._CHILDREN_LOCATOR[1]})[{index + 1}]")
        return Selector(self.driver, *self._locators, locator)

    def children(self) -> list["Selector"]:
        num_children = len(self.select(Selector._CHILDREN_LOCATOR).elements)
        return [self.child(index) for index in range(num_children)]

    def click(self) -> None:
        if element := self.element:
            element.click()

    def type_text(self, text: str) -> None:
        if element := self.element:
            element.send_keys(text)

    def clear(self) -> None:
        if element := self.element:
            element.clear()

    def set_text(self, text: str) -> None:
        self.clear()
        self.type_text(text)

    def upload_file(self, path: Path) -> None:
        self.set_text(os.path.abspath(path))

    @property
    def text(self) -> Optional[str]:
        if element := self.element:
            return element.text

    @property
    def tag_name(self) -> Optional[str]:
        if element := self.element:
            return element.tag_name

    @property
    def accessible_name(self) -> Optional[str]:
        if element := self.element:
            return element.accessible_name

    @property
    def aria_role(self) -> Optional[str]:
        if element := self.element:
            return element.aria_role

    @property
    def id(self) -> Optional[str]:
        if element := self.element:
            return element.id

    @property
    def location(self) -> Optional[Location]:
        if element := self.element:
            location = element.location
            return Location(location["x"], location["y"])

    @property
    def size(self) -> Optional[Size]:
        if element := self.element:
            size = element.size
            return Size(size["width"], size["height"])

    def scroll_into_view(self) -> None:
        if element := self.element:
            self.driver.execute_script(Selector._SCROLL_INTO_VIEW_SCRIPT, element)

    def attribute(self, name: str) -> Optional[str]:
        if element := self.element:
            return element.get_attribute(name)

    @property
    def is_present(self) -> "Check":
        return (~self.is_stale) & IsPresentCheck(self)

    @property
    def is_displayed(self) -> "Check":
        return (~self.is_stale) & IsDisplayedCheck(self)

    @property
    def is_enabled(self) -> "Check":
        return (~self.is_stale) & IsEnabledCheck(self)

    @property
    def is_selected(self) -> "Check":
        return (~self.is_stale) & IsSelectedCheck(self)

    @property
    def is_stale(self) -> "Check":
        return IsStaleCheck(self)

    def has_text(self, text: str) -> "Check":
        return (~self.is_stale) & HasTextCheck(self, text)

    def has_exact_text(self, text: str) -> "Check":
        return (~self.is_stale) & HasExactTextCheck(self, text)

    def has_attribute(self, name: str) -> "Check":
        return (~self.is_stale) & HasAttributeCheck(self, name)

    def has_attribute_value(self, name: str, value: str) -> "Check":
        return (~self.is_stale) & HasAttributeValueCheck(self, name, value)


class IsPresentCheck(Check):
    def __init__(self, selector: Selector) -> None:
        super().__init__()
        self._selector: Selector = selector

    def check(self):
        return self._selector.element is not None


class IsDisplayedCheck(Check):
    def __init__(self, selector: Selector) -> None:
        super().__init__()
        self._selector: Selector = selector

    def check(self):
        e = self._selector.element
        return e is not None and e.is_displayed()


class IsEnabledCheck(Check):
    def __init__(self, selector: Selector) -> None:
        super().__init__()
        self._selector: Selector = selector

    def check(self):
        e = self._selector.element
        return e is not None and e.is_enabled()


class IsSelectedCheck(Check):
    def __init__(self, selector: Selector) -> None:
        super().__init__()
        self._selector: Selector = selector

    def check(self) -> bool:
        e = self._selector.element
        return e is not None and e.is_selected()


class HasTextCheck(Check):
    def __init__(self, selector: Selector, text: str) -> None:
        super().__init__()
        self._selector: Selector = selector
        self._text: str = text

    def check(self) -> bool:
        e = self._selector.element
        return e is not None and self._text in e.text


class HasExactTextCheck(Check):
    def __init__(self, selector: Selector, text: str) -> None:
        super().__init__()
        self._selector: Selector = selector
        self._text: str = text

    def check(self) -> bool:
        e = self._selector.element
        return e is not None and self._text == e.text


class HasAttributeCheck(Check):
    def __init__(self, selector: Selector, name: str) -> None:
        super().__init__()
        self._selector: Selector = selector
        self._name = name

    def check(self) -> bool:
        element = self._selector.element
        if element is None:
            return False
        return self._selector.driver.execute_script(
            Selector._HAS_ATTRIBUTE_SCRIPT, element, self._name
        )


class HasAttributeValueCheck(Check):
    def __init__(self, selector: Selector, name: str, value: str) -> None:
        super().__init__()
        self._selector: Selector = selector
        self._name = name
        self._value = value

    def check(self) -> bool:
        e = self._selector.element
        return e is not None and self._value == e.get_attribute(self._name)


class IsStaleCheck(RaisesCheck):
    def __init__(self, selector: Selector) -> None:
        super().__init__(IsDisplayedCheck(selector), StaleElementReferenceException)
