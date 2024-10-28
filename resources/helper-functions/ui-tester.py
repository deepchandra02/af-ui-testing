import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import os
import datetime

# Load the schema from JSON file


def load_schema(file_path):
  with open(file_path, 'r') as file:
    return json.load(file)["components"]

# Function to determine character limit from placeholder


def get_character_limit(placeholder):
  if placeholder and re.fullmatch(r"X+", placeholder):
    return len(placeholder)
  return None

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

# Function to log details to the file


def log_entry(log_file, form_link, message):
  timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  with open(log_file, 'a') as file:
    file.write(f"{timestamp}\t{form_link}\t{message}\n")

# Function to test text input elements based on the schema


def test_text_inputs(driver, schema, log_file, form_link):
  log_entry(log_file, form_link, "Schema loaded successfully.")
  input_elements = driver.find_elements(By.TAG_NAME, "input")

  for input_element in input_elements:
    input_type = input_element.get_attribute("type")

    # Find matching component in the schema based on "type"
    matching_components = [
        component for component in schema if component["type"] == input_type]
    if not matching_components:
      continue

    # Use the first matching component (assuming unique types per schema)
    component = matching_components[0]
    aria_label = input_element.get_attribute("aria-label") or "None"
    log_entry(log_file, form_link, f"Component '{component['name']}' found with type '{
              input_type}', aria-label '{aria_label}', and testing started.")

    # Set up dynamic variables for testing
    placeholder = input_element.get_attribute("placeholder")
    char_limit = get_character_limit(placeholder) if component["variations"].get(
      "character_limit", {}).get("exists") else None

    # Determine if the component should have character limit and numeric only checks
    has_char_limit = char_limit is not None and component["variations"].get(
      "character_limit", {}).get("triggered_by") == "placeholder contains only X's"
    is_numeric_only = aria_label == "Numeric Box" and component["variations"].get(
      "numeric_only", {}).get("triggered_by") == "aria-label='Numeric Box'"

    specific_test_run = False

    # Dynamic combination of scenarios
    if has_char_limit and is_numeric_only:
      # Combined scenario: Numeric input only with character limit
      log_entry(log_file, form_link,
                "Running combined scenario: 'Numeric input only with character limit'")
      # Generate numeric input that matches the character limit
      numeric_input = "1" * char_limit
      input_element.clear()
      input_element.send_keys(numeric_input)
      actual_value = input_element.get_attribute("value")
      assert len(actual_value) <= char_limit, f"Error: Text '{
          actual_value}' exceeds character limit of {char_limit}."
      assert re.fullmatch(r"\d*", actual_value), f"Error: Non-numeric characters found in '{
          actual_value}' for numeric-only input."
      log_entry(log_file, form_link, f"Combined scenario passed: Input '{
                numeric_input}' accepted within character limit.")
      specific_test_run = True
    else:
      # Run individual scenarios based on preconditions
      for scenario in component["testing_scenarios"]:
        scenario_name = scenario["scenario"]
        preconditions = scenario["preconditions"]

        # Evaluate preconditions dynamically
        if "variations.character_limit.exists == true" in preconditions and not has_char_limit:
          continue
        if "variations.numeric_only.exists == true" in preconditions and not is_numeric_only:
          continue

        log_entry(log_file, form_link, f"Running scenario: '{scenario_name}'")

        for step in scenario["steps"]:
          action = step["action"]
          parameters = step["parameters"]
          expected_result = step["expected_result"]

          # Perform actions based on the step details
          if action == "enter_text":
            # Adapt input based on variations
            if is_numeric_only:
              # Ensure only numeric values are used
              text_value = re.sub(r'\D', '', parameters["value"])
            else:
              text_value = parameters["value"]

            if "_char_limit_" in text_value:
              text_value = text_value.replace("_char_limit_", str(char_limit))

            input_element.clear()
            input_element.send_keys(text_value)

            # Verify expected result based on component constraints
            actual_value = input_element.get_attribute("value")
            if "truncated" in expected_result:
              assert len(actual_value) <= char_limit, f"Error: Text '{
                  actual_value}' exceeds character limit of {char_limit}."
            elif "input rejected" in expected_result:
              assert re.fullmatch(r"\d*", actual_value), f"Error: Non-numeric characters found in '{
                  actual_value}' for numeric-only input."
            elif "accepted without error" in expected_result:
              log_entry(log_file, form_link, f"Input '{
                        text_value}' accepted without issues.")

            log_entry(log_file, form_link, f"Step result: {expected_result}")

        log_entry(log_file, form_link, f"Scenario '{
                  scenario_name}' completed.\n")
        specific_test_run = True

    # Generic condition for text inputs without specific variations
    if not specific_test_run:
      log_entry(log_file, form_link, f"Running generic test for component '{
                component['name']}' with type '{input_type}'")
      input_element.clear()
      input_element.send_keys("TestInput")
      actual_value = input_element.get_attribute("value")
      if actual_value == "TestInput":
        log_entry(log_file, form_link,
                  f"Generic test passed: Input 'TestInput' accepted without issues.")
      else:
        log_entry(log_file, form_link,
                  f"Generic test failed: Input 'TestInput' was not accepted as expected.")


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
