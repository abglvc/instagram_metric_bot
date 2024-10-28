from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
import time
import random
from datetime import datetime
import os


script_dir = os.path.dirname(os.path.abspath(__file__))
METRIC_FILE = ""
METRIC_DIR = os.path.join(script_dir, "metrics")
USER_DATA_DIR = os.path.join(script_dir, "selenium_instagram_session")

def load_previous_data():
    if os.path.exists(METRIC_FILE):
        with open(METRIC_FILE, 'r') as file:
            data = file.readlines()
        if data:
            return set(data[-6].strip().split(','))
    return set()

def save_ff_metric_data(target_username, new_metric_usernames, added_metric_usernames, deleted_metric_usernames, metric):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    current_metric_usernames_count = len(new_metric_usernames)

    print("=========================================================================================================================================================================================\n")
    print(f"------------------------------------------------------------------  {target_username}, {current_metric_usernames_count}, {timestamp}  ------------------------------------------------------------------\n")
    print(f"New {metric}: {', '.join(added_metric_usernames) if added_metric_usernames else 'None'}\n")
    print(f"Deleted {metric}: {', '.join(deleted_metric_usernames) if deleted_metric_usernames else 'None'}\n")
    print("=========================================================================================================================================================================================\n")
    
    with open(METRIC_FILE, 'a') as file:
        file.write("=========================================================================================================================================================================================\n")
        file.write(f"{','.join(new_metric_usernames)}\n")
        file.write("=========================================================================================================================================================================================\n")
        file.write(f"------------------------------------------------------------------  {target_username}, {current_metric_usernames_count}, {timestamp}  ------------------------------------------------------------------\n")
        file.write(f"New {metric}: {', '.join(added_metric_usernames) if added_metric_usernames else 'None'}\n")
        file.write(f"Deleted {metric}: {', '.join(deleted_metric_usernames) if deleted_metric_usernames else 'None'}\n")
        file.write("=========================================================================================================================================================================================\n")

def save_diff_metric_data(target_username, new_followers, new_following):
    user_not_following_them = new_followers - new_following
    them_not_following_user = new_following - new_followers

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    current_diff_count = len(new_followers) - len(new_following)
    print("=========================================================================================================================================================================================\n")
    print(f"------------------------------------------------------------------  {target_username}, {current_diff_count}, {timestamp}  ------------------------------------------------------------------\n")
    print(f"User not following them: {', '.join(user_not_following_them) if user_not_following_them else 'None'}\n")
    print(f"Them not following user: {', '.join(them_not_following_user) if them_not_following_user else 'None'}\n")
    print("=========================================================================================================================================================================================\n")
    
    with open(METRIC_FILE, 'a') as file:
        file.write("=========================================================================================================================================================================================\n")
        file.write(f"------------------------------------------------------------------  {target_username}, {current_diff_count}, {timestamp}  ------------------------------------------------------------------\n")
        file.write(f"User not following them: {', '.join(user_not_following_them) if user_not_following_them else 'None'}\n")
        file.write(f"Them not following user: {', '.join(them_not_following_user) if them_not_following_user else 'None'}\n")
        file.write("=========================================================================================================================================================================================\n")

def init_driver():
    mobile_emulation = {
        "deviceName": "iPhone SE"
    }
    chrome_options = Options()
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    chrome_options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
    chrome_options.add_argument("--profile-directory=Default")
    return webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

def instagram_login(driver):
    username = "your_username"
    print("Your password: ")
    password = input()
    os.system('clear')

    driver.get('https://www.instagram.com/accounts/login/')
    time.sleep(random.uniform(5, 6))
    
    username_input = driver.find_element(By.NAME, 'username')
    password_input = driver.find_element(By.NAME, 'password')
    username_input.send_keys(username)
    password_input.send_keys(password)
    
    login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    login_button.click()
    time.sleep(random.uniform(15, 20))

def get_metric_count(driver, profile, metric):
    driver.get(f"https://www.instagram.com/{profile}/")
    time.sleep(random.uniform(6.5, 7.5))

    if metric == "followers":
        metric_count_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/div[3]/ul/li[2]/div/a/span/span/span"))
        )
    elif metric == "following":
        metric_count_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/div[3]/ul/li[3]/div/a/span/span/span"))
        )
    
    return int(metric_count_element.text.replace(',', ''))

def scrape_metric(driver, profile, metric):
    total_metric = get_metric_count(driver, profile, metric)
    
    driver.get(f"https://www.instagram.com/{profile}/{metric}/")
    metric_modal = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div[1]/section/main/div[2]/div[1]/div'))
    )

    time.sleep(random.uniform(6, 8))
    action_chain = ActionChains(driver)
    metric_usernames = []
    prev_len = 0
    max_scroll_attempts = 5
    scroll_attempts = 0

    while len(metric_usernames) < total_metric and scroll_attempts < max_scroll_attempts:
        action_chain.send_keys(Keys.END).perform()
        time.sleep(random.uniform(5.5, 7.5))

        metric_elements = driver.find_elements(By.XPATH, "//span[@class='_ap3a _aaco _aacw _aacx _aad7 _aade']")
        
        for element in metric_elements:
            username = element.text
            if username not in metric_usernames:
                metric_usernames.append(username)

        if len(metric_usernames) == prev_len:
            scroll_attempts += 1
        else:
            scroll_attempts = 0

        print(str(len(metric_usernames)) + "/" + str(total_metric) + "    " + (int(50*len(metric_usernames)/total_metric))*"#" + (int(50*(1 - len(metric_usernames)/total_metric)))*"_")
        prev_len = len(metric_usernames)

    successful = len(metric_usernames) == total_metric
    return set(metric_usernames), successful

if __name__ == "__main__":
    if len(os.listdir(USER_DATA_DIR)) == 0:
        driver = init_driver()
        instagram_login(driver)
    else:
        driver = init_driver()
        target_usernames = ["username1", 
                            "username2"]
        target_metrics = [["following", "followers", "ffdiff"], 
                        ["following", "followers", "ffdiff"]]

        for i in range(len(target_usernames)):
            target_username = target_usernames[i]
            target_metric = "following"
            if target_metric in target_metrics[i]:
                METRIC_FILE = os.path.join(METRIC_DIR, target_username, (target_username + "_" + target_metric + ".txt"))
                print(METRIC_FILE)
                previous_metric_usernames = load_previous_data()
                new_following, successful_following = scrape_metric(driver, target_username, target_metric)
                if successful_following:
                    added_metric_usernames = new_following - previous_metric_usernames
                    deleted_metric_usernames = previous_metric_usernames - new_following
                    save_ff_metric_data(target_username, new_following, added_metric_usernames, deleted_metric_usernames, target_metric)
            
            target_metric = "followers"
            if target_metric in target_metrics[i]:
                METRIC_FILE = os.path.join(METRIC_DIR, target_username, (target_username + "_" + target_metric + ".txt"))
                print(METRIC_FILE)
                previous_metric_usernames = load_previous_data()
                new_followers, successful_followers = scrape_metric(driver, target_username, target_metric)
                if successful_followers:
                    added_metric_usernames = new_followers - previous_metric_usernames
                    deleted_metric_usernames = previous_metric_usernames - new_followers
                    save_ff_metric_data(target_username, new_followers, added_metric_usernames, deleted_metric_usernames, target_metric)
            
            target_metric = "ffdiff"
            if target_metric in target_metrics[i] and successful_following and successful_followers:
                METRIC_FILE = os.path.join(METRIC_DIR, target_username, (target_username + "_" + target_metric + ".txt"))
                print(METRIC_FILE)
                save_diff_metric_data(target_username, new_followers, new_following)
            
    driver.quit()
