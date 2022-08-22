import os, time, sys, argparse

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
CHAT_URL_TEST = os.environ.get('CHAT_URL_TEST', config('CHAT_URL_TEST'))
TOKEN = os.environ.get('TOKEN', config('TOKEN'))


urls= ["https://opensea.io/","https://twitter.com/","https://etherscan.io/"]


def setup(driver):
    # driver.get(CHAT_URL) #turts
    script = """
    function login(token) {
        setInterval(() => {
        document.body.appendChild(document.createElement `iframe`).contentWindow.localStorage.token = `"${token}"`
        }, 50);
        setTimeout(() => {
        location.reload();
        }, 2500);
    }

    login('TOKEN');
    """.replace("TOKEN", TOKEN)
    driver.get(CHAT_URL_TEST) # test
    driver.execute_script(script)


def scan(driver):
    webhook = Webhook.from_url(WEBHOOK_URL, adapter=RequestsWebhookAdapter())
    
    all_links = []
    buy_link =  ''
    
    try:
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
                    
    except Exception as error:
        print(error)
        webhook.send(error)
            
def main():
    # Create the parser
    parser = argparse.ArgumentParser(description='Args parse')
    # Add the arguments
    parser.add_argument('--type', action='store', type=str, required=True)
    parser.add_argument('--headless', action='store', type=str, required=True)
    
    args = parser.parse_args()
    
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    
    if args.headless == 'yes':
        options.add_argument("--headless")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
    
    
    if args.type == 'prod':
        print("Production settings with binaries...")
        options.binary_location = os.environ.get('GOOGLE_CHROME_BIN', config('GOOGLE_CHROME_BIN'))
    
    driver = webdriver.Chrome(ChromeDriverManager(chrome_type=ChromeType.BRAVE).install(), options=options)
    print("Assertion - successfully found chrome driver")
        
    print("--------- python main.y (optional arg: normal - to login via password) -----------")
    setup(driver)
    login(driver)
    print("Logged in!")
    scan(driver)
    
    
main()