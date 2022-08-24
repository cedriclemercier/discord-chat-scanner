import os, time, sys, argparse, aiohttp, asyncio, json

from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.opera import OperaDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from selenium.webdriver.chrome.options import Options
from discord import Webhook

from utils import login

from decouple import config
from datetime import datetime

USERNAME = os.environ.get('DISCORD_EMAIL', config('DISCORD_EMAIL'))
PASSWORD = os.environ.get('DISCORD_PASSWORD', config('DISCORD_PASSWORD'))
WEBHOOK_URL = os.environ.get('WEBHOOK_URL', config('WEBHOOK_URL'))
CHAT_URL = os.environ.get('CHAT_URL', config('CHAT_URL'))
CHAT_URL_TEST = os.environ.get('CHAT_URL_TEST', config('CHAT_URL_TEST'))
TOKEN = os.environ.get('TOKEN', config('TOKEN'))

def getConfig():
    configFile = open("config.json", 'r')
    return list(json.load(configFile).values())

#gets config
#json file containing  { urls: ["url1", "url2"..] }
urls = getConfig()[0]

def getLinks(driver):
    links = driver.find_elements(By.XPATH, f"//*[contains(., '{urls[0]}') or contains(., '{urls[1]}') or contains(., '{urls[2]}')]")[-2:]
    return links
    

class DiscordListener:
    
    def __init__(self, driver):
        self.driver = driver
        self.reset()
        
        links = getLinks(self.driver)
        
        for link in links:
            self.blacklist.append(link.text)
            
    def reset(self):
        
        self.blacklist = []
        self.newLink = None
        
    def newLinks(self):
        links = getLinks(self.driver)
        NT = 0
        
        for link in links:
            if not link.text in self.blacklist:
                self.blacklist.append(link.text)
                self.newLink = links
                NT = 1
            else:
                pass
        return NT


def setup(driver):
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
    driver.get(CHAT_URL_TEST) # test with CHAT_URL_TEST
    # driver.get(CHAT_URL_TEST) # test with CHAT_URL_TEST
    driver.execute_script(script)


async def scan(driver):
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(WEBHOOK_URL, session=session)
    
        last_link = ''
        
        links = []
        
        try:
            
            Listener = DiscordListener(driver)
            
            print("Scanning...")
            while True:
                if Listener.newLinks():
                    links = Listener.newLink
                
                if len(links) != 0:
                    if last_link != links[-1].text:
                        last_link = links[-1].text
                        dt = datetime.now()
                        print(f"{dt} : {last_link}")
                        await webhook.send(f"@here {last_link} \nLink to chat: {CHAT_URL}", wait=True)
        except StaleElementReferenceException:
            err = "State element issue, rescanning..."
            await webhook.send(err)
            print(err)
            await scan(driver)
        except Exception as error:
            print(error)
            await webhook.send(str(error) + "\nRestarting...")
            print("Error, restarting...")
            await scan(driver)
            
async def main():
    # Create the parser
    parser = argparse.ArgumentParser(description='Args parse')
    # Add the arguments
    parser.add_argument('--type', action='store', type=str, choices=["dev","prod"], default="dev")
    parser.add_argument('--headless', action='store', type=str, choices=["yes", "no"],default="yes")
    
    args = parser.parse_args()
    
    options = Options()
    # options.add_argument("--disable-gpu")
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
    await scan(driver)
    
asyncio.run(main())