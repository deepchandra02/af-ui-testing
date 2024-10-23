import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up Chrome options (if needed, for example, to run in headless mode)
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Uncomment to run in headless mode

# Path to your ChromeDriver
service = Service("/path/to/chromedriver")

# Set up the browser
driver = webdriver.Chrome(service=service, options=chrome_options)

# URL to open
url = "https://example.com"  # Replace with the URL you want to open
driver.get(url)

# Wait for user to log in manually
print("Please log in manually...")
WebDriverWait(driver, 300).until(EC.url_changes(url))
print("Logged in successfully!")

# Get all input elements on the page
input_elements = driver.find_elements(By.TAG_NAME, "input")

# Prepare a list to store input details
input_details = []

# Extract and store information for each input element
for input_element in input_elements:
  input_info = {
      "input_snippet": input_element.get_attribute('outerHTML'),
      "type": input_element.get_attribute("type"),
      "aria_attributes": {}
  }

  # Collect all aria-* attributes
  for attribute in input_element.get_property('attributes'):
    if attribute['name'].startswith("aria-"):
      input_info["aria_attributes"][attribute['name']] = attribute['value']

  input_details.append(input_info)

# Save the details to a JSON file
with open("input_details.json", "w") as file:
  json.dump(input_details, file, indent=4)

print("Input details saved to input_details.json")

# Close the browser
driver.quit()
