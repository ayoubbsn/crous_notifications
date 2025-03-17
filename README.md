# CROUS Notifications

CROUS Notifications is an automated tool that checks for available residences in Île de France on the LesCrous website and sends email notifications when a change is detected. This project leverages Selenium with headless Chrome and GitHub Actions to run the script every 15 minutes.

## Features

- **Automated Search:** Checks for residence listings in Île de France.
- **Email Alerts:** Sends notifications when new listings appear.
- **Configurable:** Easily update the search URL and email addresses via GitHub Secrets.
- **CI/CD Integration:** Runs automatically every 15 minutes using GitHub Actions.

## Repository Structure

```
.
├── .github
│   └── workflows
│       └── crous-checker.yml   # GitHub Actions workflow file
├── src
│   ├── main.py                 # Python script to fetch listings & send notifications
│   └── last_result.txt         # Stores the previous search result
└── README.md                   # This file
```

## Setup

### GitHub Secrets

To configure the email notifications and (optionally) allow the workflow to push updates, add the following secrets to your repository:

- `EMAIL_SENDER`: The email address that will send the notifications.
- `EMAIL_PASSWORD`: The email account’s app password (e.g., a Gmail App Password).
- `EMAIL_RECEIVER`: The email address where notifications will be sent.
- `GH_PAT`: (Optional) A GitHub Personal Access Token with repo permissions (needed if you want the workflow to push changes).

### Customizing the Search URL

The search URL is currently set for Île de France. You can adjust this URL in `src/main.py`:

```python
url = "https://trouverunlogement.lescrous.fr/tools/37/search?bounds=1.4462445_49.241431_3.5592208_48.1201456"
```

Change the URL as needed to target different regions or search parameters.

## GitHub Actions Workflow

The workflow is defined in `.github/workflows/crous-checker.yml` and is set to run every 15 minutes using the following cron schedule:

```yaml
on:
  schedule:
    - cron: "*/15 * * * *"  # Runs every 15 minutes
  workflow_dispatch:        # Allows manual triggering
```

This ensures your script checks for changes frequently without any cost if your repository is public (or within GitHub’s free tier for private repos).

## Dependencies

- **Python 3.x**
- **Selenium** – for browser automation.
- **webdriver-manager** – for managing the ChromeDriver version.
- **Headless Chrome/Chromium** – installed on GitHub Actions runners.
- **SMTP** – used for sending email notifications.

Install dependencies locally with:

```bash
pip install selenium webdriver-manager
```

## Running Locally

To test the script locally, ensure you have set the required environment variables (`EMAIL_SENDER`, `EMAIL_PASSWORD`, and `EMAIL_RECEIVER`), then run:

```bash
python src/main.py
```

## Troubleshooting

- **Email Encoding:** The script uses UTF-8 encoding (via MIMEText) to handle non-ASCII characters such as emojis.
- **Selenium Issues:** If you experience connection issues with Selenium, make sure you’re running headless mode with options like `--no-sandbox` and `--disable-dev-shm-usage`.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

### `.github/workflows/crous-checker.yml`

```yaml
name: CROUS Checker

on:
  schedule:
    - cron: "*/15 * * * *"  # Runs every 15 minutes
  workflow_dispatch:

jobs:
  check_crous:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
        with:
          persist-credentials: false

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.x"

      - name: Install Chromium and Chromedriver
        run: |
          sudo apt-get update
          sudo apt-get install -y chromium-browser chromium-chromedriver

      - name: Install Python Dependencies
        run: |
          pip install selenium webdriver-manager

      - name: Run the script
        env:
          EMAIL_SENDER: ${{ secrets.EMAIL_SENDER }}
          EMAIL_PASSWORD: ${{ secrets.EMAIL_PASSWORD }}
          EMAIL_RECEIVER: ${{ secrets.EMAIL_RECEIVER }}
        run: python src/main.py

      - name: Commit and push changes if detected
        if: always()
        env:
          GH_PAT: ${{ secrets.GH_PAT }}
        run: |
          git config --global user.name "github-actions"
          git config --global user.email "github-actions@github.com"
          git add src/last_result.txt
          git commit -m "Update last_result.txt" || echo "No changes to commit"
          git push https://x-access-token:${GH_PAT}@github.com/${{ github.repository }}.git master
```

---

### `src/main.py`

```python
import os
import smtplib
import time
from email.mime.text import MIMEText
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Email Configuration
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

LAST_RESULT_FILE = "src/last_result.txt"

def send_email(subject, message):
    try:
        msg = MIMEText(message, _charset="utf-8")
        msg['Subject'] = subject
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

# Fetch data, check for changes, and run main process
if __name__ == "__main__":
    check_for_changes()

