import os, time, sys

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.opera import OperaDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from selenium.webdriver.chrome.options import Options
from discord import Webhook, RequestsWebhookAdapter

from utils import login, getConfig

from decouple import config
from datetime import datetime

USERNAME = os.environ.get('DISCORD_EMAIL', config('DISCORD_EMAIL'))
PASSWORD = os.environ.get('DISCORD_PASSWORD', config('DISCORD_PASSWORD'))
WEBHOOK_URL = os.environ.get('WEBHOOK_URL', config('WEBHOOK_URL'))
CHAT_URL = os.environ.get('CHAT_URL', config('CHAT_URL'))


args = sys.argv
urls= ["https://opensea.io/","https://twitter.com/","https://etherscan.io/"]

options = Options()
options.add_argument("--disable-gpu")
# to keep window open after mint uncomment option below, side effect, will open alot of chrome windows
#options.add_experimental_option("detach", True)
# prefs = {"profile.managed_default_content_settings.images": 2}
# options.add_experimental_option("prefs", prefs)
options.add_experimental_option("excludeSwitches", ["enable-logging"])
# driver = webdriver.Chrome(
#         executable_path=ChromeDriverManager().install(), options=options)
driver = webdriver.Chrome(ChromeDriverManager(chrome_type=ChromeType.BRAVE).install(), options=options)
print("Assertion - successfully found chrome driver")
load_dotenv()
# config = getConfig()
# driver.get(config[0])
# driver.maximize_window()

 
# driver.get(CHAT_URL) #turts
driver.get('CHAT_URL_TEST') # test


def scan(driver):
    webhook = Webhook.from_url(WEBHOOK_URL, adapter=RequestsWebhookAdapter())
    
    all_links = []
    buy_link =  ''
    
    # links = driver.find_elements(By.XPATH, "//a[contains(text(),'opensea')]")
    links = driver.find_elements(By.XPATH, f"//*[contains(., '{urls[0]}') or contains(., '{urls[1]}') or contains(., '{urls[2]}')]")
    
    print("Scanning...")
    
    if len(links) != 0:
        print(f"Length: {len(links)}")
        print(links[-1].text)
        
        last_link = links[-1].text
    
    while True:
        
        # links = driver.find_elements(By.XPATH, "//a[contains(text(),'opensea')]")
        
        links = driver.find_elements(By.XPATH, f"//*[contains(., '{urls[0]}') or contains(., '{urls[1]}') or contains(., '{urls[2]}')]")
        
        if len(links) != 0:
            if last_link != links[-1].text:
                last_link = links[-1].text
                dt = datetime.now()
                print(f"{dt} : {last_link}")
                webhook.send(f"@here {last_link}")
            

print("--------- python main.y (optional arg: normal - to login via password) -----------")
login(USERNAME, PASSWORD, driver, args)
scan(driver)