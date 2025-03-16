import os
import smtplib
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Email configuration and other functions here…
# (send_email, check_for_changes, etc.)

def fetch_residences():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Specify the binary location for Chromium
    options.binary_location = "/usr/bin/chromium-browser"

    # Use the system chromedriver installed via apt-get
    driver = webdriver.Chrome(
        service=ChromeService("/usr/bin/chromedriver"),
        options=options
    )

    url = "https://trouverunlogement.lescrous.fr/tools/37/search?bounds=1.4462445_49.241431_3.5592208_48.1201456"
    driver.get(url)

    try:
        # Wait until the container element is present
        wait = WebDriverWait(driver, 10)
        container = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "SearchResults-container")))
        text = container.text.strip()
        driver.quit()
        return text if text else "No available residences"
    except Exception as e:
        print(f"❌ Error extracting data: {e}")
        driver.quit()
        return None

if __name__ == "__main__":
    # Call check_for_changes() or your main routine here.
    check_for_changes()
