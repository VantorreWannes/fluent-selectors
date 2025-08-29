from pathlib import Path
from typing import Any, Generator

import pytest
from pytest_httpserver import HTTPServer
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.remote.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager


@pytest.fixture
def chrome_driver() -> Generator[WebDriver, Any, None]:
    service = ChromeService(ChromeDriverManager().install())
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=service, options=options)
    yield driver
    driver.quit()


@pytest.fixture
def test_page_url(httpserver: HTTPServer):
    test_html_path = Path(__file__).parent / "test.html"
    with open(test_html_path, "r") as f:
        test_html_content = f.read()
    httpserver.expect_request("/").respond_with_data(
        test_html_content, content_type="text/html"
    )
    return httpserver.url_for("/")
