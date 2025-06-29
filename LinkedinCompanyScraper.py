# ---------------------- Import required libraries ----------------------
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import random
import pickle
import os
import socket
import re

# ---------------------- Utility: Check for internet connection ----------------------
def net_check_run(func, *args, **kwargs):
    while True:
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=5)
            print("📶 Internet connected.")
            return func(*args, **kwargs)
        except OSError:
            print("📡 No internet. Retrying in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            print(f"⚠️ Error: {e}. Retrying in 5 seconds...")
            time.sleep(5)

# ---------------------- Utility: Human-like delays ----------------------
def human_pause(min_sec=3, max_sec=7):
    time.sleep(random.uniform(min_sec, max_sec))

# ---------------------- Load Excel and filter company links ----------------------
input_file = "linkedin_links.xlsx"
df = pd.read_excel(input_file)

# Keep only rows with company links
df = df[df['Link'].str.contains("/company/")].copy()
df.reset_index(drop=True, inplace=True)

# ---------------------- Setup Chrome options ----------------------
options = uc.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.0.0 Safari/537.36")
driver = uc.Chrome(options=options)

# ---------------------- Load cookies if available ----------------------
cookie_file = "cookies.pkl"
net_check_run(driver.get, "https://www.linkedin.com/login")

if os.path.exists(cookie_file):
    print("♻️ Loading saved cookies...")
    cookies = pickle.load(open(cookie_file, "rb"))
    for cookie in cookies:
        cookie.pop('sameSite', None)
        driver.add_cookie(cookie)
    driver.refresh()
else:
    print("🔓 Please log in to LinkedIn manually.")

# Wait for login confirmation
while True:
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.search-global-typeahead__input"))
        )
        print("✅ Login successful.")
        break
    except:
        print("⏳ Waiting for login to complete...")
        time.sleep(5)

# Save cookies for future use
pickle.dump(driver.get_cookies(), open(cookie_file, "wb"))

# ---------------------- Load existing output Excel ----------------------
output_file = "linkedin_info.xlsx"
if os.path.exists(output_file):
    df_out = pd.read_excel(output_file)
else:
    print("⚠️ Output file 'linkedin_info.xlsx' not found.")
    exit()

# Ensure required columns exist
if not {'CompanyLink', 'Company'}.issubset(df_out.columns):
    print("❌ 'linkedin_info.xlsx' must contain 'CompanyLink' and 'Company' columns.")
    exit()

# ---------------------- Loop through company links ----------------------
for idx, row in df.iterrows():
    url = row['Link']

    # Skip if link already exists in output file
    if url in df_out['CompanyLink'].values:
        print(f"⏭️ Skipping already processed link: {url}")
        continue

    print(f"🌐 Visiting: {url}")

    try:
        net_check_run(driver.get, url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        human_pause(2, 4)

        # Extract company name from <h1>
        company_name = driver.find_element(By.TAG_NAME, "h1").text.strip()
        print(f"🏢 Company name extracted: {company_name}")

        # Append new row to DataFrame
        new_row = {"CompanyLink": url, "Company": company_name}
        df_out = pd.concat([df_out, pd.DataFrame([new_row])], ignore_index=True)
        df_out.to_excel(output_file, index=False)

    except Exception as e:
        print(f"❌ Error while processing {url}: {e}")
        continue

    human_pause(8, 15)

# ---------------------- Done ----------------------
driver.quit()
print("🎉 Done! All new companies added to 'linkedin_info.xlsx'.")
