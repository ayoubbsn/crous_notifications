import os
import smtplib
import time
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.by import By
from webdriver_manager.microsoft import EdgeChromiumDriverManager

# Email Configuration (from GitHub Secrets)
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# File path for storing previous results
LAST_RESULT_FILE = "src/last_result.txt"

# Function to send an email
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

# Function to get residence listings
def fetch_residences():
    options = webdriver.EdgeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")

    driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=options)

    url = "https://trouverunlogement.lescrous.fr/tools/37/search?bounds=1.4462445_49.241431_3.5592208_48.1201456"
    driver.get(url)

    time.sleep(5)  # Wait for the page to load

    try:
        residence_elements = driver.find_elements(By.CLASS_NAME, "SearchResults-container")
        driver.quit()

        if residence_elements:
            container_text = residence_elements[0].text.strip()
            return container_text
        else:
            return "No available residences"
    except Exception as e:
        print(f"❌ Error extracting data: {e}")
        driver.quit()
        return None

# Function to check for changes
def check_for_changes():
    # Fetch current data
    current_data = fetch_residences()

    if current_data is None:
        return  # Error fetching data, skip checking

    # Read previous result
    if os.path.exists(LAST_RESULT_FILE):
        with open(LAST_RESULT_FILE, "r", encoding="utf-8") as file:
            last_data = file.read().strip()
    else:
        last_data = ""

    # Compare and send email if there's a change
    if current_data != last_data:
        print("🔔 Change detected! Sending email...")
        send_email("🏠 CROUS Residence Update!", f"New available residences:\n\n{current_data}")

        # Update the stored result
        with open(LAST_RESULT_FILE, "w", encoding="utf-8") as file:
            file.write(current_data)
    else:
        print("✅ No changes detected.")

# Run the check
check_for_changes()
