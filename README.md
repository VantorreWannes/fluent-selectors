# Fluent Selectors

A Python library for creating a readable, fluent API for Selenium browser automation.

## Installation

Install the package using pip:

```bash
pip install fluent-selectors
```

## Usage

Here's a simple example of how to use `fluent-selectors`:

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from fluent_selectors import Selector

# Initialize the WebDriver
driver = webdriver.Chrome()
driver.get("http://www.python.org")

# Create a Selector instance
s = Selector(driver)

# Select an element and interact with it
search_bar = s.select((By.NAME, "q"))
search_bar.set_text("pycon")

go_button = s.select((By.ID, "submit"))
go_button.click()

# Perform checks
s.select((By.CLASS_NAME, "list-recent-events")).is_displayed.is_true()

driver.quit()
```

## API

### `Selector(driver: WebDriver, *locators: Locator)`

The main class for selecting and interacting with elements.

-   `select(locator: Locator) -> Selector`: Select a descendant of the current element.
-   `child(index: int) -> Selector`: Select a child by its index.
-   `children() -> list[Selector]`: Get a list of all children.
-   `parent() -> Selector | None`: Get the parent selector.
-   `parents() -> list[Selector]`: Get a list of all parent selectors.

### Element Actions

-   `click()`: Clicks the element.
-   `type_text(text: str)`: Types text into the element.
-   `clear()`: Clears the text from the element.
-   `set_text(text: str)`: Clears the element and then types text into it.
-   `upload_file(path: Path)`: Uploads a file to a file input element.
-   `scroll_into_view()`: Scrolls the element into view.

### Element Properties

-   `element() -> WebElement | None`: The Selenium WebElement.
-   `elements() -> list[WebElement]`: A list of Selenium WebElements.
-   `text() -> str | None`: The text of the element.
-   `tag_name() -> str | None`: The tag name of the element.
-   `accessible_name() -> str | None`: The accessible name of the element.
-   `aria_role() -> str | None`: The ARIA role of the element.
-   `id() -> str | None`: The ID of the element.
-   `location() -> Location | None`: The location of the element.
-   `size() -> Size | None`: The size of the element.
-   `attribute(name: str) -> str | None`: The value of an attribute.

### Checks

You can perform checks on selectors using the following properties. These checks are based on the [fluent-checks](https://github.com/VantorreWannes/fluent-checks) library.

-   `is_present()`: Checks if the element is present in the DOM.
-   `is_displayed()`: Checks if the element is visible.
-   `is_enabled()`: Checks if the element is enabled.
-   `is_selected()`: Checks if the element is selected.
-   `has_text(text: str)`: Checks if the element's text contains the given text.
-   `has_exact_text(text: str)`: Checks if the element's text exactly matches the given text.
-   `has_attribute(name: str)`: Checks if the element has the given attribute.

Example of a check:

```python
s.select((By.ID, "my-element")).is_displayed.is_true()
s.select((By.ID, "my-element")).has_text("Hello").is_true()
```

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
