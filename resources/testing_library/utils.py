# Function to log details to the file
import datetime


def log_entry(log_file, form_link, message):
  timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  with open(log_file, 'a') as file:
    file.write(f"{timestamp}\t{form_link}\t{message}\n")
