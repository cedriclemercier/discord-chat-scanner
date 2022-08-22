from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import json, time

def getConfig():
    configFile = open("config.json", 'r')
    return list(json.load(configFile).values())

def login_password(email, password, driver, args):
    
    email_input = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//input[@name='email']")))
    password_input = driver.find_element(By.XPATH, "//input[@name='password']")
    submit_input = driver.find_element(By.XPATH, "//button[@type='submit']")
    
    print("Found login fields, submitting.")
    email_input.send_keys(email)
    password_input.send_keys(password)
    
    
    if len(args) < 2:
        print("Scan QR by default")
    else:
        if args[1] == 'normal':
            submit_input.click()
    
    print("Logging in...")
    
    # wait for page to load
    textbox = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, "chatContent-3KubbW")))
    
    
def login(driver):
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, "chatContent-3KubbW")))