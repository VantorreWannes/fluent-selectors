import os
from abc import ABC
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Optional, Union

from fluent_checks import Check
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

type Locator = tuple[str, str]

SELF_LOCATOR: Locator = (By.XPATH, ".")
CHILDREN_LOCATOR: Locator = (By.XPATH, "./*")


@dataclass
class Location:
    x: int
    y: int


@dataclass
class Size:
    x: float
    y: float


class Selector(ABC):
    def __init__(self, driver: WebDriver, *locators: Locator) -> None:
        super().__init__()
        self._driver: WebDriver = driver
        self._locators: tuple[Locator, ...] = locators or (SELF_LOCATOR,)
        self._locator: Locator = self._locators[-1]

    @cached_property
    def parent(self) -> Optional["Selector"]:
        if len(self._locators) > 1:
            return Selector(self._driver, *self._locators[:-1])

    @cached_property
    def parents(self) -> list["Selector"]:
        if parent := self.parent:
            return [parent, *parent.parents]
        return []

    @property
    def _context(self) -> Union[WebDriver, WebElement, None]:
        if self.parent:
            return self.parent.element
        return self._driver

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
        return Selector(self._driver, *self._locators, locator)

    def child(self, index: int) -> "Selector":
        locator: Locator = (By.XPATH, f"({CHILDREN_LOCATOR[1]})[{index + 1}]")
        return Selector(self._driver, *self._locators, locator)

    def children(self) -> list["Selector"]:
        num_children = len(self.select(CHILDREN_LOCATOR).elements)
        return [self.child(index) for index in range(num_children)]

    def click(self):
        if element := self.element:
            element.click()

    def type_text(self, text: str):
        if element := self.element:
            element.send_keys(text)

    def clear(self):
        if element := self.element:
            element.clear()

    def set_text(self, text: str):
        self.clear()
        self.type_text(text)

    def upload_file(self, path: Path):
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
            self._driver.execute_script("arguments[0].scrollIntoView(true);", element)

    def attribute(self, name: str) -> Optional[str]:
        if element := self.element:
            return element.get_attribute(name)

    @property
    def is_present(self) -> "IsPresentCheck":
        return IsPresentCheck(self)

    @property
    def is_displayed(self) -> "IsDisplayedCheck":
        return IsDisplayedCheck(self)

    @property
    def is_enabled(self) -> "IsEnabledCheck":
        return IsEnabledCheck(self)

    @property
    def is_selected(self) -> "IsSelectedCheck":
        return IsSelectedCheck(self)

    def has_text(self, text: str) -> "HasTextCheck":
        return HasTextCheck(self, text)

    def has_exact_text(self, text: str) -> "HasExactTextCheck":
        return HasExactTextCheck(self, text)

    def has_attribute(self, name: str) -> "HasAttributeCheck":
        return HasAttributeCheck(self, name)


class IsPresentCheck(Check):
    def __init__(self, selector: Selector) -> None:
        element: WebElement | None = selector.element
        super().__init__(lambda: True if element is not None else False)
        self._selector: Selector = selector


class IsDisplayedCheck(Check):
    def __init__(self, selector: Selector) -> None:
        element: WebElement | None = selector.element
        super().__init__(
            lambda: element.is_displayed() if element is not None else False
        )
        self._selector: Selector = selector


class IsEnabledCheck(Check):
    def __init__(self, selector: Selector) -> None:
        element: WebElement | None = selector.element
        super().__init__(lambda: element.is_enabled() if element is not None else False)
        self._selector: Selector = selector


class IsSelectedCheck(Check):
    def __init__(self, selector: Selector) -> None:
        element: WebElement | None = selector.element
        super().__init__(
            lambda: element.is_selected() if element is not None else False
        )
        self._selector: Selector = selector


class HasTextCheck(Check):
    def __init__(self, selector: Selector, text: str) -> None:
        element: WebElement | None = selector.element
        super().__init__(lambda: text in element.text if element is not None else False)
        self._selector: Selector = selector
        self._text: str = text


class HasExactTextCheck(Check):
    def __init__(self, selector: Selector, text: str) -> None:
        element: WebElement | None = selector.element
        super().__init__(lambda: text == element.text if element is not None else False)
        self._selector: Selector = selector
        self._text: str = text


class HasAttributeCheck(Check):
    def __init__(self, selector: Selector, name: str) -> None:
        element: WebElement | None = selector.element
        super().__init__(
            lambda: bool(element.get_attribute(self._name))
            if element is not None
            else False
        )
        self._selector: Selector = selector
        self._name = name
