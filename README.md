# 🕵️ LinkedIn Profile Scraper (People + Companies)

This project contains two Python scripts that allow you to scrape LinkedIn profiles and extract both personal and company data using Selenium and undetected ChromeDriver.

---

## 📂 Project Overview

- `linkedin_profile_scraper.py`: Extracts name, headline, location, and associated company link from LinkedIn profiles.
- `linkedin_company_scraper.py`: Navigates to company pages from previously collected profile data and extracts the company name.

---

## ⚙️ Requirements

Install Python dependencies with:

```bash
pip install pandas selenium undetected-chromedriver openpyxl
You must also have Google Chrome installed.

## 🚀 How to Use
🔑 1. First-Time Login
The scraper will prompt you to log in to LinkedIn manually the first time.

Your session cookies will be saved to cookies.pkl for future runs.

The script will automatically use those cookies on the next run.

📥 2. Prepare Your Input File
Use an Excel file (linkedin_links.xlsx) with LinkedIn profile URLs (not company pages):

Link
https://www.linkedin.com/in/sample-user-1/
https://www.linkedin.com/in/sample-user-2/

You may use the included sample_links.xlsx as a template.

🧑 3. Run Profile Scraper
bash
Copy
Edit
python linkedin_profile_scraper.py
This will:

Open each LinkedIn profile link

Extract Name, Headline, Location, and CompanyLink

Save results in linkedin_info.xlsx

🏢 4. Run Company Scraper (Optional)
Once profiles are scraped and CompanyLink fields are collected, run:

bash
Copy
Edit
python linkedin_company_scraper.py
This will:

Visit each unique company link

Extract the official company name from the <h1> tag

Update linkedin_info.xlsx with Company values

💡 Features
✔️ Waits for internet before navigating

⏳ Mimics human behavior with pauses and scrolling

🔁 Avoids scraping already-processed profiles/companies

💾 Saves cookies and resumes session

📊 Automatically updates your output file (linkedin_info.xlsx)
