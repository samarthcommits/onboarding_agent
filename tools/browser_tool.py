# test_get_started_link(page = Page())
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.chrome.service import Service as ChromeService


def open_link(link: str):
    # options = webdriver.ChromeOptions()
    # options = webdriver.ChromeOptions()
    path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    # options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options = Options()
    # chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9014")
    chrome_options.add_argument('--enable-logging')
    chrome_options.add_argument('--v=1')
    capabilities = {'loggingPrefs': {'browser': 'ALL'}}
    s = ChromeService(log_path="./chromedriver.log")
    # options.add_experimental_option('debuggerAddress', 'localhost:8080')
    # options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=chrome_options, service=s)  # or webdriver.Firefox()
    driver.get(link)
    time.sleep(10)
    driver.quit()
    return f'opened {link} successfully'

from langchain.agents import AgentType
from langchain.tools import Tool

b_tool = Tool(
    name='browser_tool',
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    func=lambda link: open_link(link),
    description='Opens up the link address provided in the browser. Input: an URL as string.'
)