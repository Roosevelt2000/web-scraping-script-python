from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time

BASE_URL = "https://ph.jobstreet.com/jobs-in-information-communication-technology/in-Philippines"

def scrape_jobstreet(pages=3):

    jobs = []

    options = Options()

    # turn this OFF if site blocks you
    # options.add_argument("--headless")

    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    wait = WebDriverWait(driver, 15)

    for page in range(1, pages + 1):

        url = f"{BASE_URL}?page={page}"
        print("Opening:", url)

        driver.get(url)

        try:
            wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,'[data-automation="normalJob"]')
                )
            )
        except:
            print("Jobs not detected on page")

        time.sleep(2)

        soup = BeautifulSoup(driver.page_source,"html.parser")

        job_cards = soup.select('[data-automation="normalJob"]')

        print("Jobs found:", len(job_cards))

        for job in job_cards:

            title = job.select_one('[data-automation="jobTitle"]')
            company = job.select_one('[data-automation="jobCompany"]')
            location = job.select_one('[data-automation="jobLocation"]')
            link = job.find("a", href=True)

            jobs.append({
                "title": title.text.strip() if title else None,
                "company": company.text.strip() if company else None,
                "location": location.text.strip() if location else None,
                "link": "https://ph.jobstreet.com" + link["href"] if link else None
            })

    driver.quit()

    return jobs


def save_to_csv(data):

    if not data:
        print("No data scraped.")
        return

    df = pd.DataFrame(data)

    df.to_csv(
        "jobstreet_jobs.csv",
        index=False,
        encoding="utf-8"
    )

    print("Saved",len(data),"jobs to jobstreet_jobs.csv")


if __name__ == "__main__":

    results = scrape_jobstreet(pages=3)

    print("Total jobs:", len(results))

    save_to_csv(results)