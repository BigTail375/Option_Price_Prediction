from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
import os
import time
import shutil

DAILY_TOKEN = 'https://optiondata.org/daily.html?token=3enw7x29'
CHROME_DRIVER_PATH = "./database_management/chromedriver.exe"
DOWNLOAD_DIRECTORY = os.path.expanduser("~\\Downloads")
DATASET_STOCK_DIRECTORY = './dataset/stocks'
DATASET_OPTION_DIRECTORY = './dataset/options'

def latest_date():
    data_path = './dataset/stocks'
    dates = []
    for file_path in os.listdir(data_path):
        dates.append(file_path[:10])
    return dates

def download_latest_data():

    dates = latest_date()
    chrome_options = Options()
    driver = webdriver.Chrome(service=Service(CHROME_DRIVER_PATH), options=chrome_options)
    driver.get(DAILY_TOKEN)
    time.sleep(2)
    downloaded_files = []
    for i in range(1, 131):
        download_button = driver.find_element(By.XPATH, f'//*[@id=\"fileList\"]/li[{i}]/a')
        cur_date = download_button.text[:10]
        downloaded_files.append(download_button.text)
        if cur_date not in dates:
            download_button.click()
            while any(fname.endswith(".crdownload") for fname in os.listdir(DOWNLOAD_DIRECTORY)):
                time.sleep(1)
            time.sleep(2)
    driver.quit()
    return downloaded_files

downloaded_files = download_latest_data()
for file in downloaded_files:
    csv_file = file[:-3] + 'csv'
    os.rename(os.path.join(DOWNLOAD_DIRECTORY, file), os.path.join(DOWNLOAD_DIRECTORY, csv_file))
    if csv_file[10:16] == 'stocks':
        shutil.move(os.path.join(DOWNLOAD_DIRECTORY, csv_file), os.path.join(DATASET_STOCK_DIRECTORY, csv_file))
    else:
        shutil.move(os.path.join(DOWNLOAD_DIRECTORY, csv_file), os.path.join(DATASET_OPTION_DIRECTORY, csv_file))