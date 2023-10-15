import os
import time

import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from tqdm.contrib import tzip

load_dotenv()

ROOT_URL = "https://search.macaulaylibrary.org/catalog?sort=rating_rank_desc"

latin_names_file = '../shared/latin_names.txt'
bird_names_file = '../shared/botw_names.txt'

already_complete_file = 'already_complete.txt'
not_found_names = 'not-found-names.txt'

ROOT_DIR = 'downloaded_data'

NUM_DATA = 150
LOAD_TIME = 20


def load_names(path):
    with open(path, 'w+') as f:
        return f.read().splitlines()


birds = load_names(bird_names_file)
latin_birds = load_names(latin_names_file)
complete_birds = load_names(already_complete_file)


def login(driver):
    driver.get(ROOT_URL)

    login_button = driver.find_element(By.LINK_TEXT, 'Sign in')
    login_button.click()

    WebDriverWait(driver, 10).until(EC.url_changes(driver.title))

    username = driver.find_element(By.ID, 'input-user-name')
    username.send_keys(os.getenv('BENUTZER'))

    password = driver.find_element(By.ID, 'input-password')
    password.send_keys(os.getenv('PASSWORT'))

    confirm_button = driver.find_element(By.ID, 'form-submit')
    confirm_button.click()

    WebDriverWait(driver, 10).until(EC.url_changes(driver.title))


def download_images(driver, latin_name, bird_folder_path):
    tag_name = 'img'

    elements = driver.find_elements(By.TAG_NAME, tag_name)

    if len(elements) == 0:
        print(f'\nRate-limited - {latin_name}, skipping...')
        return

    while len(elements) < NUM_DATA:
        try:
            rate_limit_placeholders = driver.find_elements(By.CLASS_NAME, 'ResultsGallery-placeholder')
            if len(rate_limit_placeholders) > 0:
                print(f'Rate limited {latin_name}')
                break
        except NoSuchElementException:
            pass

        try:
            more_button = WebDriverWait(driver, LOAD_TIME).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(text(),'More results')]")))
            more_button.click()
        except TimeoutException:
            break

        elements = driver.find_elements(By.TAG_NAME, tag_name)

    time.sleep(4)
    elements = driver.find_elements(By.TAG_NAME, tag_name)

    print(f'Maximum amount of entries found ({latin_name}): {len(elements)}')
    if len(elements) > 0:
        with open(already_complete_file, 'a') as f:
            f.write(latin_name + '\n')

    for idx, element in enumerate(elements[:NUM_DATA]):
        url = element.get_attribute('src')

        response = requests.get(url)
        if response.status_code == 200:
            save_directory = os.path.join(bird_folder_path, str(idx + 1))
            with open(f'{save_directory}.jpg', 'wb') as file:
                file.write(response.content)


def download_audios(driver, latin_name, bird_folder_path):
    tag_name = 'audio'
    element_identifier = 'ResultsGallery-playButton'

    elements = driver.find_elements(By.CLASS_NAME, element_identifier)

    while len(elements) < NUM_DATA:
        try:
            more_button = WebDriverWait(driver, LOAD_TIME).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(text(),'More results')]")))
            more_button.click()
        except TimeoutException:
            break

        elements = driver.find_elements(By.CLASS_NAME, element_identifier)

    time.sleep(3)
    elements = driver.find_elements(By.CLASS_NAME, element_identifier)

    for idx, element in enumerate(elements[:NUM_DATA]):
        element.click()
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, tag_name)))
        time.sleep(0.3)
        try:
            url = element.get_attribute('src')

            response = requests.get(url)
            if response.status_code == 200:
                save_directory = os.path.join(bird_folder_path, str(idx + 1))
                with open(f'{save_directory}.mp3', 'wb') as file:
                    file.write(response.content)
            else:
                print(f'\nRate limited - {latin_name}, skipping...')
                return
        except StaleElementReferenceException:
            print(f'\nElement turned stale {latin_name}')
        close_button = driver.find_element(By.CLASS_NAME, 'Lightbox-close')
        close_button.click()

    print(f'Maximum amount of entries found ({latin_name}): {len(elements)}')
    if len(elements) > 0:
        with open(already_complete_file, 'a') as f:
            f.write(latin_name + '\n')


def scrape_data(bird_names, latin_names, complete_list, media_type='photo'):
    os.makedirs(ROOT_DIR, exist_ok=True)

    chrome_options = Options()
    chrome_options.add_argument("--mute-audio")
    chrome_options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(options=chrome_options)

    login(driver)

    for bird_name, latin_name in tzip(bird_names, latin_names):
        media_folder_path = os.path.join(ROOT_DIR, 'Audios' if media_type == 'audio' else 'Images')
        os.makedirs(media_folder_path, exist_ok=True)

        bird_folder_path = os.path.join(media_folder_path, latin_name)
        os.makedirs(bird_folder_path, exist_ok=True)

        already_downloaded_num = len(os.listdir(bird_folder_path))

        if already_downloaded_num == NUM_DATA or latin_name in complete_list:
            print(f'\nAlready downloaded {media_type} - {latin_name}, skipping...')
            continue

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

        if media_type == 'photo':
            download_images(driver, latin_name, bird_folder_path)
        elif media_type == 'audio':
            download_audios(driver, latin_name, bird_folder_path)


media = input('Please specify the media type (audio or photo): ')

scrape_data(birds, latin_birds, complete_birds, media_type=media)
