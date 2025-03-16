import smtplib
import time
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.by import By
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import os

# Email Configuration
EMAIL_SENDER = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password"
EMAIL_RECEIVER = "your_email@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

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
    last_result_file = "last_result.txt"

    # Fetch current data
    current_data = fetch_residences()

    if current_data is None:
        return  # Error fetching data, skip checking

    # Read previous result
    if os.path.exists(last_result_file):
        with open(last_result_file, "r", encoding="utf-8") as file:
            last_data = file.read().strip()
    else:
        last_data = ""

    # Compare and send email if there's a change
    if current_data != last_data:
        print("🔔 Change detected! Sending email...")
        send_email("🏠 CROUS Residence Update!", f"New available residences:\n\n{current_data}")

        # Update the stored result
        with open(last_result_file, "w", encoding="utf-8") as file:
            file.write(current_data)
    else:
        print("✅ No changes detected.")

# Run the script continuously every hour
while True:
    check_for_changes()
    print("⏳ Waiting for the next check...")
    time.sleep(3600)  # Wait for 1 hour
