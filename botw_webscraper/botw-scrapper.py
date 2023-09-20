from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import pyautogui
import os
from dotenv import load_dotenv

load_dotenv()

filepath = 'birds_of_the_world_files'
search_names = 'botw-missing.txt'
not_found_names = 'world_not_found.txt'
en_names = 'en_names.txt'

with open(search_names, 'r') as birds:
    search_bird_names = birds.read().splitlines()

with open(en_names, 'r') as en_birds:
    en_bird_names = en_birds.read().splitlines()

not_found_birds = []

chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=chrome_options)

driver.get("https://birdsoftheworld.org/bow/home")

login = driver.find_element(By.LINK_TEXT, 'Sign In')

login.click()
WebDriverWait(driver, 10).until(EC.url_changes(driver.title))

username = driver.find_element(By.ID, 'input-user-name')
username.send_keys(os.getenv('BENUTZER'))
password = driver.find_element(By.ID, 'input-password')
password.send_keys(os.getenv('PASSWORT'))

confirm_button = driver.find_element(By.ID, 'form-submit')
confirm_button.click()

WebDriverWait(driver, 10).until(EC.url_changes(driver.title))

offset = len(en_bird_names) - len(search_bird_names)

assert len(en_bird_names[offset:]) == len(search_bird_names)

for search, savefile in zip(search_bird_names, en_bird_names[offset:]):
    driver.get("https://birdsoftheworld.org/bow/home")
    WebDriverWait(driver, 10).until(EC.url_changes(driver.title))

    inputField = driver.find_element(By.ID, "hero")
    inputField.send_keys(search)

    try:
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "Suggest-suggestion-0")))
    except TimeoutException:
        print(f'Could not find bird: {search}')
        not_found_birds.append(search)
        continue

    element.click()

    WebDriverWait(driver, 10).until(EC.url_changes(driver.title))

    category = driver.find_element(By.LINK_TEXT, 'Sounds and Vocal Behavior')
    category.click()
    WebDriverWait(driver, 10).until(EC.url_changes(driver.title))

    # sections = driver.find_elements(By.TAG_NAME, 'p')
    # introduction = sections[0].text

    # Download as pdf
    pyautogui.hotkey('ctrl', 'p')
    time.sleep(5)
    pyautogui.hotkey('enter')
    time.sleep(2)
    pyautogui.typewrite(savefile)
    pyautogui.hotkey('enter')
    time.sleep(5)

with open(not_found_names, 'w') as missing_birds:
    missing_list = '\n'.join(not_found_birds)
    missing_birds.write(missing_list)
