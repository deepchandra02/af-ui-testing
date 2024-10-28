import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import datetime
from testing_library.type_text import test_text_inputs

# Load the schema from JSON file


def load_schema(file_path):
  with open(file_path, 'r') as file:
    return json.load(file)["components"]

# Function to initialize log file with a timestamp, stored in "ui_test_logs" folder


def initialize_log():
  # Ensure "ui_test_logs" directory exists
  log_dir = "ui_test_logs"
  os.makedirs(log_dir, exist_ok=True)

  # Create a timestamped log file within the directory
  timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
  log_file = os.path.join(log_dir, f"log_{timestamp}.txt")

  with open(log_file, 'w') as file:
    file.write("Date and Time\tForm Link\tLog\n")

  return log_file


# Example usage
schema_path = "components-schema.json"
schema = load_schema(schema_path)

# Set up the browser
driver = webdriver.Chrome()  # Ensure you have the ChromeDriver set up

# URL to open
url = "https://example.com"  # Replace with the URL you want to open
driver.get(url)

# Wait until the URL is the one specified and the page is fully loaded
try:
  WebDriverWait(driver, 300).until(
      # Waits until the browser URL matches the one specified
      EC.url_to_be(url)
  )
  WebDriverWait(driver, 10).until(
      EC.presence_of_all_elements_located(
        (By.TAG_NAME, "input"))  # Ensures inputs are loaded
  )
  print("Page loaded successfully!")
except Exception as e:
  print(f"Error: {e}")
  driver.quit()
  exit()

# Initialize log file and start testing
log_file = initialize_log()
test_text_inputs(driver, schema, log_file, url)

# Quit the browser after testing
driver.quit()

print(f"Testing completed. Log saved to {log_file}")
