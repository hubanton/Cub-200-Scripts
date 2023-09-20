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

english_names_file = '../shared/en_names.txt'
bird_names_file = '../shared/botw-names.txt'

not_found_names = 'not-found-names.txt'


def load_names(path):
    with open(path, 'r') as f:
        return f.read().splitlines()


bird_names = load_names(bird_names_file)
english_names_file = load_names(english_names_file)

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

for bird_name, english_name in zip(bird_names, english_names_file):
    driver.get("https://birdsoftheworld.org/bow/home")
    WebDriverWait(driver, 10).until(EC.url_changes(driver.title))

    inputField = driver.find_element(By.ID, "hero")
    inputField.send_keys(bird_name)

    try:
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "Suggest-suggestion-0")))
    except TimeoutException:
        print(f'Could not find bird: {bird_name}')
        not_found_birds.append(bird_name)
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
    pyautogui.typewrite(english_name)
    pyautogui.hotkey('enter')
    time.sleep(5)

with open(not_found_names, 'w') as missing_birds:
    missing_list = '\n'.join(not_found_birds)
    missing_birds.write(missing_list)