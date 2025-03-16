import os
import smtplib
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

def fetch_residences():
    # ChromeOptions
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Use webdriver_manager to install matching ChromeDriver
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    url = "https://trouverunlogement.lescrous.fr/tools/37/search?bounds=1.4462445_49.241431_3.5592208_48.1201456"
    driver.get(url)

    time.sleep(5)

    try:
        elements = driver.find_elements(By.CLASS_NAME, "SearchResults-container")
        driver.quit()

        if elements:
            return elements[0].text.strip()
        else:
            return "No available residences"
    except Exception as e:
        print(f"❌ Error extracting data: {e}")
        driver.quit()
        return None

# Email Configuration
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

LAST_RESULT_FILE = "src/last_result.txt"

def send_email(subject, message):
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        email_body = f"Subject: {subject}\n\n{message}"
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, email_body)
        server.quit()
        print("📧 Email sent successfully!")
    except Exception as e:
        print(f"❌ Error sending email: {e}")


def check_for_changes():
    current_data = fetch_residences()
    if current_data is None:
        return  # Error fetching data, skip checking

    if os.path.exists(LAST_RESULT_FILE):
        with open(LAST_RESULT_FILE, "r", encoding="utf-8") as file:
            last_data = file.read().strip()
    else:
        last_data = ""

    if current_data != last_data:
        print("🔔 Change detected! Sending email...")
        send_email("🏠 CROUS Residence Update!", f"New available residences:\n\n{current_data}")

        with open(LAST_RESULT_FILE, "w", encoding="utf-8") as file:
            file.write(current_data)
    else:
        print("✅ No changes detected.")

if __name__ == "__main__":
    check_for_changes()
