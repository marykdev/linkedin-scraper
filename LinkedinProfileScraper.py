# ---------------------- Import required libraries ----------------------
import undetected_chromedriver as uc  # Bypasses bot detection on Chrome
from selenium.webdriver.common.by import By  # For locating elements by type (e.g., CSS selector)
from selenium.webdriver.support.ui import WebDriverWait  # To wait for elements to load
from selenium.webdriver.support import expected_conditions as EC  # Expected conditions for waiting
import pandas as pd  # For data manipulation
import time
import random
from selenium.webdriver.common.action_chains import ActionChains  # For simulating human mouse actions
import pickle  # For saving/loading cookies
import os
import re  # Regular expressions for cleaning URLs
import socket  # To check internet connectivity
import sys

# ---------------------- Functions to wait for internet connection ----------------------
def net_check_run(func, *args, **kwargs):
    """
    Waits until internet connection is available,
    then runs the given function.
    If function raises an exception (e.g. network error),
    waits and retries.
    """
    while True:
        try:
            # Check internet connectivity
            socket.create_connection(("8.8.8.8", 53), timeout=5)
            print("📶 Internet connection established.")
            # Run the function with args
            return func(*args, **kwargs)
        except OSError:
            print("📡 No internet connection. Waiting to reconnect...")
            time.sleep(5)
        except Exception as e:
            print(f"Error during function execution: {e}. Retrying in 5 seconds...")
            time.sleep(5)
# ---------------------- Human-like interaction functions ----------------------

def human_scroll(driver):
    # Scrolls down the page in small random steps to simulate human behavior
    scroll_pause_time = random.uniform(0.8, 1.5)
    scroll_height = driver.execute_script("return document.body.scrollHeight")
    scroll_pos = 0
    while scroll_pos < scroll_height:
        scroll_pos += random.randint(100, 300)
        driver.execute_script(f"window.scrollTo(0, {scroll_pos});")
        time.sleep(scroll_pause_time)
        scroll_height = driver.execute_script("return document.body.scrollHeight")

def human_pause(min_sec=3, max_sec=7):
    # Adds a random delay to mimic human pause
    time.sleep(random.uniform(min_sec, max_sec))

# ---------------------- Load and clean input data ----------------------

df_links = pd.read_excel("linkedin_links.xlsx")

# Keep only LinkedIn profile links (those containing '/in/')
df_links = df_links[df_links['Link'].str.contains("/in/")].copy()

# Normalize all profile links to a consistent format
def normalize_link(link):
    match = re.search(r'/in/([^/?#,]+)', link)
    if match:
        username = match.group(1)
        return f"https://www.linkedin.com/in/{username}?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app"
    return ""

df_links['Link'] = df_links['Link'].apply(normalize_link)
df_links = df_links[df_links['Link'] != ""].copy()
df_links.reset_index(drop=True, inplace=True)

# ---------------------- Prepare DataFrame to store results ----------------------

columns = ['Link', 'Name', 'Headline', 'Location', 'Company']
df_data = pd.DataFrame(columns=columns)

# ---------------------- Initialize undetected Chrome driver ----------------------

options = uc.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")  # Helps avoid detection
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
options.add_argument(f"user-agent={user_agent}")
driver = uc.Chrome(options=options)

# ---------------------- Load login cookies or wait for manual login ----------------------

cookie_file = "cookies.pkl"
print("🔐 Opening LinkedIn login page...")
net_check_run(driver.get, "https://www.linkedin.com/login")

if os.path.exists(cookie_file):
    print("♻️ Loading cookies from file...")
    cookies = pickle.load(open(cookie_file, "rb"))
    for cookie in cookies:
        cookie.pop('sameSite', None)
        driver.add_cookie(cookie)
    driver.refresh()
else:
    print("⚠️ No cookies found, please log in manually.")

# ---------------------- Wait for login to complete ----------------------

while True:
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.search-global-typeahead__input"))
        )
        print("✅ Login detected, starting profile scraping...")
        break
    except:
        print("⏳ Waiting for successful login...")
        time.sleep(5)

# Save cookies for next time
print("💾 Saving cookies for future sessions...")
pickle.dump(driver.get_cookies(), open(cookie_file, "wb"))

# Prepare for mouse actions
actions = ActionChains(driver)

# ---------------------- Load already collected data if any ----------------------

output_file = "linkedin_info.xlsx"
if os.path.exists(output_file):
    df_data = pd.read_excel(output_file)
    done_links = set(df_data['Link'])
else:
    done_links = set()

# ---------------------- Function to retry loading profile ----------------------

def load_linkedin_profile(url):
    """
    Tries to load a LinkedIn profile URL, waits for profile name element.
    Retries every 15 seconds on failure.
    """
    while True:
        try:
            net_check_run(driver.get, url)
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.ph5 h1'))
            )
            return True
        except Exception as e:
            print(f"🔁 Failed to load profile. Retrying in 15 seconds... Error: {e}")
            time.sleep(15)

# ---------------------- Scraping loop ----------------------

batch_count = 0
for idx, row in df_links.iterrows():
    url = row['Link']

    name = ''
    headline = ''
    location = ''
    company_name = ''
    company_link = ''

    if url in done_links:
        continue  # Skip previously processed links

    print(f"🔍 Processing ({idx + 1}/{len(df_links)}): {url}")

    success = load_linkedin_profile(url)
    if not success:
        continue

    human_pause(4, 6)
    human_scroll(driver)
    human_pause(2, 4)

    # Extract profile details
    try:
        name = driver.find_element(By.CSS_SELECTOR, 'div.ph5 h1').text.strip()
    except:
        name = ""

    try:
        headline = driver.find_element(By.CSS_SELECTOR, 'div.text-body-medium.break-words').text.strip()
    except:
        headline = ""

    try:
        location = driver.find_element(By.CSS_SELECTOR, 'span.text-body-small.inline.t-black--light.break-words').text.strip()
    except:
        location = ""

    try:
       
        company_link_element = driver.find_element(By.CSS_SELECTOR, "a[data-field='experience_company_logo']")
        company_link = company_link_element.get_attribute("href")
        print(f"✅ Company link found: {company_link}")

        # If company link exists, navigate and extract the company name
        if company_link:
            print("🌐 Navigating to the company page...")
            try:
                net_check_run(driver.get, company_link)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "h1"))
                )
                h1_text = driver.find_element(By.TAG_NAME, "h1").text.strip()

                # Check if h1_text starts with "Search results for"
                if h1_text.startswith("Search results for"):
                    match = re.search(r"Search results for (.+?)\.", h1_text)
                    if match:
                        company_name = match.group(1).strip()
                        print(f"🔍 Extracted company name from search results format: {company_name}")
                    else:
                        company_name = "Unknown from Search Results"
                        print("⚠️ Couldn't extract company name from search results format.")
                else:
                    company_name = h1_text
                    print(f"🏢 Company name extracted: {company_name}")

            except Exception as e:
                print(f"⚠️ Could not load the company page or extract the name. Error: {e}")
        else:
            company_name = "Unknown / No Link"
            print("📭 No company link available, setting name as 'Unknown / No Link'.")

    except Exception as e:
        print(f"❌ Failed to process the experience section. Error: {e}")
        company_link = ""
        company_name = ""
  
    except Exception as e:
        print(f"⚠️ Error: {e}")

    # Log extracted data
    if name:
        print(f"✅ Retrieved: {name} - {headline} - {location} - {company_name}- {company_link}")
    else:
        print("⚠️ No valid data found.")

    # Save new row to DataFrame
    new_row = pd.DataFrame([{
        'Link': url,
        'Name': name,
        'Headline': headline,
        'Location': location,
        'Company': company_name,
        'CompanyLink': company_link
    }])
    df_data = pd.concat([df_data, new_row], ignore_index=True)
    df_data.to_excel(output_file, index=False)

    done_links.add(url)
    batch_count += 1

    # # Ask user if they want to continue every 10 profiles
    # if batch_count % 10 == 0:
    #     cont = input("🔄 Do you want to continue? (y/n): ").strip().lower()
    #     if cont != 'y':
    #         print("🛑 Stopped by user.")
    #         break

    # Pause between profiles
    human_pause(10, 20)

# ---------------------- Done ----------------------

driver.quit()
print("🎉 All available profiles processed and saved.")
