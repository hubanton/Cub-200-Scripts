from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pyautogui
import os
from dotenv import load_dotenv


load_dotenv()

filepath = 'birds_of_the_world_files'

birdnames = ['Black-footed Albatross']

chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=chrome_options)

for bird in birdnames:
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

    inputField = driver.find_element(By.ID, "hero")
    inputField.send_keys(bird)

    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "Suggest-suggestion-0")))

    element.click()

    WebDriverWait(driver, 10).until(EC.url_changes(driver.title))

    category = driver.find_element(By.LINK_TEXT, 'Sounds and Vocal Behavior')
    category.click()
    WebDriverWait(driver, 10).until(EC.url_changes(driver.title))

    sections = driver.find_elements(By.TAG_NAME, 'p')
    introduction = sections[0].text

    # Download as pdf
    pyautogui.hotkey('ctrl', 'p')
    time.sleep(5)
    pyautogui.hotkey('enter')
    time.sleep(2)
    pyautogui.typewrite(bird)
    pyautogui.hotkey('enter')
    time.sleep(5)