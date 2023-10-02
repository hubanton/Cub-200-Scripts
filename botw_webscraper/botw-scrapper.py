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

link_text = 'Sounds and Vocal Behavior'

english_names_file = '../shared/en_names.txt'
bird_names_file = '../shared/latin-names.txt'

textfiles = 'textfiles'

if not os.path.exists(textfiles):
    os.mkdir(textfiles)

not_found_names = 'not-found-names.txt'
latin_names_file = 'latin_names.txt'


def load_names(path):
    with open(path, 'r') as f:
        return f.read().splitlines()


birds = load_names(bird_names_file)
en_birds = load_names(english_names_file)


def scrape_botw(bird_names, english_names, download_pdf=True, download_section=True, download_latin_name=False):
    not_found_birds = []

    latin_names = []

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

    for bird_name, english_name in zip(bird_names, english_names):
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

        # for the latin names
        section = driver.find_element(By.CLASS_NAME, 'Heading-sub')
        latin_name = section.text.split('\n')[0]
        latin_name = latin_name.replace(' ', '_')
        print(latin_name)
        latin_names.append(latin_name)

        if download_section or download_pdf:
            category = driver.find_element(By.LINK_TEXT, link_text)
            category.click()
            WebDriverWait(driver, 10).until(EC.url_changes(driver.title))

        if download_section:
            sections = driver.find_elements(By.CLASS_NAME, 'GridFlex-cell')
            with open(textfiles + '/' + latin_name + '.txt', 'w') as bird_info:
                text = sections[3].text
                if not text.startswith(link_text):
                    text = text.split(link_text)[1]
                    text = 'Sounds and Vocal Behavior' + text

                text = text.split('Diet and Foraging')[0]
                if len(text.split('Breeding')) != 1:
                    text = text.split('Breeding')[0]

                bird_info.write(text)

        if download_pdf:
            # Download as pdf
            pyautogui.hotkey('ctrl', 'p')
            time.sleep(5)
            pyautogui.hotkey('enter')
            time.sleep(2)
            pyautogui.typewrite(latin_name)
            pyautogui.hotkey('enter')
            time.sleep(5)

    with open(not_found_names, 'w') as f:
        res = '\n'.join(not_found_birds)
        f.write(res)

    if download_latin_name:
        with open(latin_names_file, 'w') as f:
            res = '\n'.join(latin_names)
            f.write(res)


scrape_botw(birds, en_birds, download_pdf=False, download_section=False, download_latin_name=True)
