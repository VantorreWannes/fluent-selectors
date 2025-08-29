from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from fluent_selectors import Selector


def test_is_present(chrome_driver: WebDriver, test_page_url: str):
    chrome_driver.get(test_page_url)
    selector = Selector(chrome_driver, (By.TAG_NAME, "h1"))
    assert selector.is_present


def test_is_not_present(chrome_driver: WebDriver, test_page_url: str):
    chrome_driver.get(test_page_url)
    selector = Selector(chrome_driver, (By.TAG_NAME, "h2"))
    assert not selector.is_present


def test_is_displayed(chrome_driver: WebDriver, test_page_url: str):
    chrome_driver.get(test_page_url)
    selector = Selector(chrome_driver, (By.TAG_NAME, "h1"))
    assert selector.is_displayed


def test_is_not_displayed(chrome_driver: WebDriver, test_page_url: str):
    chrome_driver.get(test_page_url)
    selector = Selector(chrome_driver, (By.CSS_SELECTOR, "#div-2 p"))
    assert not selector.is_displayed


def test_is_enabled(chrome_driver: WebDriver, test_page_url: str):
    chrome_driver.get(test_page_url)
    selector = Selector(chrome_driver, (By.ID, "button-1"))
    assert selector.is_enabled


def test_is_not_enabled(chrome_driver: WebDriver, test_page_url: str):
    chrome_driver.get(test_page_url)
    selector = Selector(chrome_driver, (By.ID, "button-2"))
    assert not selector.is_enabled


def test_is_selected(chrome_driver: WebDriver, test_page_url: str):
    chrome_driver.get(test_page_url)
    selector = Selector(chrome_driver, (By.ID, "checkbox-1"))
    assert selector.is_selected


def test_is_not_selected(chrome_driver: WebDriver, test_page_url: str):
    chrome_driver.get(test_page_url)
    selector = Selector(chrome_driver, (By.ID, "checkbox-2"))
    assert not selector.is_selected


def test_has_text(chrome_driver: WebDriver, test_page_url: str):
    chrome_driver.get(test_page_url)
    selector = Selector(chrome_driver, (By.TAG_NAME, "h1"))
    assert selector.has_text("Hello")


def test_does_not_have_text(chrome_driver: WebDriver, test_page_url: str):
    chrome_driver.get(test_page_url)
    selector = Selector(chrome_driver, (By.TAG_NAME, "h1"))
    assert not selector.has_text("H2")


def test_does_have_exact_text(chrome_driver: WebDriver, test_page_url: str):
    chrome_driver.get(test_page_url)
    selector = Selector(chrome_driver, (By.TAG_NAME, "h1"))
    assert selector.has_exact_text("Hello, World!")


def test_does_not_have_exact_text(chrome_driver: WebDriver, test_page_url: str):
    chrome_driver.get(test_page_url)
    selector = Selector(chrome_driver, (By.TAG_NAME, "h1"))
    assert not selector.has_exact_text("An H1")


def test_has_attribute(chrome_driver: WebDriver, test_page_url: str):
    chrome_driver.get(test_page_url)
    selector = Selector(chrome_driver, (By.ID, "div-1"))
    assert selector.has_attribute("id")


def test_does_not_have_attribute(chrome_driver: WebDriver, test_page_url: str):
    chrome_driver.get(test_page_url)
    selector = Selector(chrome_driver, (By.TAG_NAME, "h1"))
    assert not selector.has_attribute("class")


def test_parent(chrome_driver: WebDriver, test_page_url: str):
    chrome_driver.get(test_page_url)
    child_selector = Selector(
        chrome_driver, (By.TAG_NAME, "body"), (By.ID, "div-1"), (By.TAG_NAME, "h1")
    )
    parent_selector = child_selector.parent
    assert parent_selector is not None
    assert parent_selector.element is not None
    assert parent_selector.element.get_attribute("id") == "div-1"


def test_parents(chrome_driver: WebDriver, test_page_url: str):
    chrome_driver.get(test_page_url)
    child_selector = Selector(
        chrome_driver, (By.TAG_NAME, "body"), (By.ID, "div-1"), (By.TAG_NAME, "h1")
    )
    parents = child_selector.parents
    assert len(parents) == 2
    assert parents[0]._locator == (By.ID, "div-1")
    assert parents[1]._locator == (By.TAG_NAME, "body")


def test_select(chrome_driver: WebDriver, test_page_url: str):
    chrome_driver.get(test_page_url)
    selector = Selector(chrome_driver, (By.ID, "div-1"))
    h1_selector = selector.select((By.TAG_NAME, "h1"))
    assert h1_selector.element is not None
    assert h1_selector.element.text == "Hello, World!"


def test_child(chrome_driver: WebDriver, test_page_url: str):
    chrome_driver.get(test_page_url)
    selector = Selector(chrome_driver, (By.ID, "div-1"))

    # Test first child
    h1_selector = selector.child(0)
    assert h1_selector.element is not None
    assert h1_selector.element.tag_name == "h1"
    assert h1_selector.text == "Hello, World!"

    # Test second child
    p_selector = selector.child(1)
    assert p_selector.element is not None
    assert p_selector.element.tag_name == "p"
    assert p_selector.text == "This is a test page."

    # Test out of bounds
    invalid_selector = selector.child(4)
    assert invalid_selector.element is None


def test_children(chrome_driver: WebDriver, test_page_url: str):
    chrome_driver.get(test_page_url)
    selector = Selector(chrome_driver, (By.ID, "div-1"))

    child_selectors = selector.children()
    assert len(child_selectors) == 4

    assert child_selectors[0].tag_name == "h1"
    assert child_selectors[1].tag_name == "p"
    assert child_selectors[2].tag_name == "button"
    assert child_selectors[3].tag_name == "button"
