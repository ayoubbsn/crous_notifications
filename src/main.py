import os
import smtplib
import time
from email.mime.text import MIMEText
from email.header import Header
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Email Configuration (from GitHub Secrets)
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# File path for storing previous results
LAST_RESULT_FILE = "src/last_result.txt"

def send_email(subject, message):
    try:
        # Create a MIMEText object with UTF-8 encoding.
        msg = MIMEText(message, _charset="utf-8")
        # Encode the subject properly using Header:
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        server.quit()
        print("📧 Email sent successfully!")
    except Exception as e:
        print(f"❌ Error sending email: {e}")

def fetch_residences():
    # Set up Chrome options for headless execution.
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    
    # Initialize ChromeDriver using webdriver_manager to handle versioning.
    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=options
    )

    url = "https://trouverunlogement.lescrous.fr/tools/37/search?bounds=1.4462445_49.241431_3.5592208_48.1201456"
    driver.get(url)

    try:
        # Use WebDriverWait to wait for the SearchResults-container element.
        wait = WebDriverWait(driver, 10)
        container = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "SearchResults-container")))
        container_text = container.text.strip()
        driver.quit()

        if container_text:
            return container_text
        else:
            return "No available residences"
    except Exception as e:
        print(f"❌ Error extracting data: {e}")
        driver.quit()
        return None

def check_for_changes():
    # Fetch current residence data.
    current_data = fetch_residences()
    if current_data is None:
        return  # Error fetching data, skip checking

    # Read previous result from file.
    if os.path.exists(LAST_RESULT_FILE):
        with open(LAST_RESULT_FILE, "r", encoding="utf-8") as file:
            last_data = file.read().strip()
    else:
        last_data = ""

    # Compare and send email if there's a change.
    if current_data != last_data:
        print("🔔 Change detected! Sending email...")
        send_email("🏠 CROUS Residence Update!", f"New available residences:\n\n{current_data}")

        # Update the stored result.
        with open(LAST_RESULT_FILE, "w", encoding="utf-8") as file:
            file.write(current_data)
    else:
        print("✅ No changes detected.")

if __name__ == "__main__":
    check_for_changes()
