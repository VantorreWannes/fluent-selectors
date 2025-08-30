import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from fluent_selectors import Selector


@pytest.mark.parametrize(
    "locator, expected",
    [
        ((By.TAG_NAME, "h1"), True),
        ((By.TAG_NAME, "h2"), False),
    ],
)
def test_is_present(driver: WebDriver, locator, expected):
    selector = Selector(driver, locator)
    assert bool(selector.is_present) == expected


@pytest.mark.parametrize(
    "locator, expected",
    [
        ((By.TAG_NAME, "h1"), True),
        ((By.CSS_SELECTOR, "#div-2 p"), False),
    ],
)
def test_is_displayed(driver: WebDriver, locator, expected):
    selector = Selector(driver, locator)
    assert bool(selector.is_displayed) == expected


@pytest.mark.parametrize(
    "locator, expected",
    [
        ((By.ID, "button-1"), True),
        ((By.ID, "button-2"), False),
    ],
)
def test_is_enabled(driver: WebDriver, locator, expected):
    selector = Selector(driver, locator)
    assert bool(selector.is_enabled) == expected


@pytest.mark.parametrize(
    "locator, expected",
    [
        ((By.ID, "checkbox-1"), True),
        ((By.ID, "checkbox-2"), False),
    ],
)
def test_is_selected(driver: WebDriver, locator, expected):
    selector = Selector(driver, locator)
    assert bool(selector.is_selected) == expected


@pytest.mark.parametrize(
    "locator, text, expected",
    [
        ((By.TAG_NAME, "h1"), "Hello", True),
        ((By.TAG_NAME, "h1"), "H2", False),
    ],
)
def test_has_text(driver: WebDriver, locator, text, expected):
    selector = Selector(driver, locator)
    assert bool(selector.has_text(text)) == expected


@pytest.mark.parametrize(
    "locator, text, expected",
    [
        ((By.TAG_NAME, "h1"), "Hello, World!", True),
        ((By.TAG_NAME, "h1"), "An H1", False),
    ],
)
def test_has_exact_text(driver: WebDriver, locator, text, expected):
    selector = Selector(driver, locator)
    assert bool(selector.has_exact_text(text)) == expected


@pytest.mark.parametrize(
    "locator, attribute, expected",
    [
        ((By.ID, "div-1"), "id", True),
        ((By.TAG_NAME, "h1"), "class", False),
    ],
)
def test_has_attribute(driver: WebDriver, locator, attribute, expected):
    selector = Selector(driver, locator)
    assert bool(selector.has_attribute(attribute)) == expected


def test_parent(driver: WebDriver):
    child_selector = Selector(
        driver, (By.TAG_NAME, "body"), (By.ID, "div-1"), (By.TAG_NAME, "h1")
    )
    parent_selector = child_selector.parent
    assert parent_selector is not None
    assert parent_selector.element is not None
    assert parent_selector.element.get_attribute("id") == "div-1"


def test_parents(driver: WebDriver):
    child_selector = Selector(
        driver, (By.TAG_NAME, "body"), (By.ID, "div-1"), (By.TAG_NAME, "h1")
    )
    parents = child_selector.parents
    assert len(parents) == 2
    assert parents[0]._locator == (By.ID, "div-1")
    assert parents[1]._locator == (By.TAG_NAME, "body")


def test_select(driver: WebDriver):
    selector = Selector(driver, (By.ID, "div-1"))
    h1_selector = selector.select((By.TAG_NAME, "h1"))
    assert h1_selector.element is not None
    assert h1_selector.element.text == "Hello, World!"


@pytest.mark.parametrize(
    "child_index, tag_name, text",
    [
        (0, "h1", "Hello, World!"),
        (1, "p", "This is a test page."),
    ],
)
def test_child(driver: WebDriver, child_index, tag_name, text):
    selector = Selector(driver, (By.ID, "div-1"))
    child_selector = selector.child(child_index)
    assert child_selector.element is not None
    assert child_selector.element.tag_name == tag_name
    assert child_selector.text == text


def test_child_out_of_bounds(driver: WebDriver):
    selector = Selector(driver, (By.ID, "div-1"))
    invalid_selector = selector.child(4)
    assert invalid_selector.element is None


def test_children(driver: WebDriver):
    selector = Selector(driver, (By.ID, "div-1"))
    children = selector.children()
    assert len(children) == 4
    expected_tags = ["h1", "p", "button", "button"]
    actual_tags = [child.tag_name for child in children]
    assert actual_tags == expected_tags

