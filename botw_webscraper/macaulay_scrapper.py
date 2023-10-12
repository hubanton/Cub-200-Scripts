import os
import time

import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

load_dotenv()

ROOT_URL = "https://search.macaulaylibrary.org/catalog?sort=rating_rank_desc"

latin_names_file = '../shared/latin_names.txt'
bird_names_file = '../shared/botw_names.txt'

not_found_names = 'not-found-names.txt'

ROOT_DIR = 'downloaded_data'

NUM_DATA = 100


def load_names(path):
    with open(path, 'r') as f:
        return f.read().splitlines()


birds = load_names(bird_names_file)
latin_birds = load_names(latin_names_file)


def scrape_data(bird_names, latin_names, media_types=None):
    if media_types is None:
        media_types = ['photo']

    os.makedirs(ROOT_DIR, exist_ok=True)

    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(ROOT_URL)

    login = driver.find_element(By.LINK_TEXT, 'Sign in')
    login.click()

    WebDriverWait(driver, 10).until(EC.url_changes(driver.title))

    username = driver.find_element(By.ID, 'input-user-name')
    username.send_keys(os.getenv('BENUTZER'))

    password = driver.find_element(By.ID, 'input-password')
    password.send_keys(os.getenv('PASSWORT'))

    confirm_button = driver.find_element(By.ID, 'form-submit')
    confirm_button.click()

    WebDriverWait(driver, 10).until(EC.url_changes(driver.title))

    for bird_name, latin_name in zip(bird_names, latin_names):
        bird_folder_path = os.path.join(ROOT_DIR, latin_name)
        os.makedirs(bird_folder_path, exist_ok=True)

        for media_type in media_types:
            media_folder_path = os.path.join(bird_folder_path, media_type)
            os.makedirs(media_folder_path, exist_ok=True)

            driver.get(ROOT_URL + '&mediaType=' + media_type)
            WebDriverWait(driver, 10).until(EC.url_changes(driver.title))

            input_field = driver.find_element(By.ID, "taxonFinder")
            input_field.send_keys(bird_name)

            try:
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "Suggest-suggestion-0")))
            except TimeoutException:
                print(f'Could not find bird: {bird_name}')
                with open(not_found_names, 'a') as f:
                    f.write(bird_name)
                continue

            element.click()

            WebDriverWait(driver, 10).until(EC.url_changes(driver.title))

            tag_name = ''

            if media_type == 'photo':
                tag_name = 'img'

            elements = driver.find_elements(By.TAG_NAME, tag_name)

            while len(elements) < NUM_DATA:
                try:
                    more_button = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.XPATH, "//button[contains(text(),'More results')]")))
                    more_button.click()

                except TimeoutException:
                    print('Cant find more data ' + bird_name)
                    break

                elements = driver.find_elements(By.TAG_NAME, tag_name)

            time.sleep(3)
            elements = driver.find_elements(By.TAG_NAME, tag_name)

            for idx, element in enumerate(elements[:NUM_DATA]):
                url = element.get_attribute('src')

                response = requests.get(url)
                if response.status_code == 200:
                    save_directory = os.path.join(media_folder_path, f'{idx}_{element.get_attribute("alt")}')
                    with open(f'{save_directory}.jpg', 'wb') as file:
                        file.write(response.content)


scrape_data(birds, latin_birds)
