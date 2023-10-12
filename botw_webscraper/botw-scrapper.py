import os
import time

import pyautogui
from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

load_dotenv()

LINK_TEXTS = ['Sounds and Vocal Behavior', 'Diet and Foraging', 'Conservation and Management', 'Habitat', 'Systematics']
ROOT_URL = "https://birdsoftheworld.org/bow/home"

english_names_file = '../shared/en_names.txt'
bird_names_file = '../shared/botw_names.txt'

not_found_names = 'not-found-names.txt'
latin_names_file = 'latin_names.txt'


def load_names(path):
    with open(path, 'r') as f:
        return f.read().splitlines()


birds = load_names(bird_names_file)
en_birds = load_names(english_names_file)


def scrape_botw(bird_names, english_names, link_texts):
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(ROOT_URL)

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

    for bird_name, english_name in zip(bird_names, english_names):
        driver.get(ROOT_URL)
        WebDriverWait(driver, 10).until(EC.url_changes(driver.title))

        input_field = driver.find_element(By.ID, "hero")
        input_field.send_keys(bird_name)

        try:
            element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "Suggest-suggestion-0")))
        except TimeoutException:
            print(f'Could not find bird: {bird_name}')
            with open(not_found_names, 'a') as f:
                f.write(bird_name)
            continue

        element.click()

        WebDriverWait(driver, 10).until(EC.url_changes(driver.title))

        section = driver.find_element(By.CLASS_NAME, 'Heading-sub')
        latin_name = section.text.split('\n')[0]
        latin_name = latin_name.replace(' ', '_')
        with open(latin_names_file, 'a') as f:
            f.write(latin_name)

        for link_text in link_texts:
            category = driver.find_element(By.LINK_TEXT, link_text)
            category.click()
            WebDriverWait(driver, 10).until(EC.url_changes(driver.title))

            pyautogui.hotkey('ctrl', 'p')
            time.sleep(5)
            pyautogui.hotkey('enter')
            time.sleep(2)
            pyautogui.typewrite(f"{latin_name}_{link_text}")
            pyautogui.hotkey('enter')
            time.sleep(5)


scrape_botw(birds, en_birds, LINK_TEXTS)
