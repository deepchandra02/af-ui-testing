from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
from openai import OpenAI
from bs4 import BeautifulSoup
import os
from flask_socketio import SocketIO, emit
import speech_recognition as sr
import numpy as np
import torch
from faster_whisper import WhisperModel
from queue import Queue
from threading import Thread
from datetime import datetime, timezone, timedelta
from time import sleep

app = Flask(__name__)
app.secret_key = os.urandom(24)
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)  # This will enable CORS for all routes

# Load the Whisper model once at the start
model_name = "small"
device = "cuda" if torch.cuda.is_available() else "cpu"
audio_model = WhisperModel(
    model_name,
    device=device,
    compute_type="float16" if torch.cuda.is_available() else "int8"
)

# Add these variables
transcribing = False
recognizer = sr.Recognizer()
recognizer.energy_threshold = 1000
recognizer.dynamic_energy_threshold = False
data_queue = Queue()
transcription = ['']
audio_data = b''

record_timeout = 1.5
phrase_timeout = 1.5
phrase_time = None

stop_flag = False
listener_thread = None

# Initialize the OpenAI client
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

# Recognizer and microphone setup
recognizer = sr.Recognizer()
mic = sr.Microphone()

transcribing = False  # Flag to track transcription state


@app.route('/')
def index():
  return render_template('index.html')


@app.route('/chat_to_fill', methods=['POST'])
def chat_to_fill():
  data = request.json
  command = data.get('command')
  html_content = data.get('html')
  # Parse the HTML content
  soup = BeautifulSoup(html_content, 'html.parser')
  # Find all input and button tags
  inputs_and_buttons = soup.find_all(['input', 'button'])

  # Prepare the fixed prompt
  fixed_prompt = """
You are an intelligent assistant that helps users to fill HTML forms on their screen. Based on the user's command and the provided HTML content, generate JavaScript code that will perform the desired action on the form. Do not include any explanations or additional text; only provide the JavaScript code.

Constraints:
- Prioritize selecting elements by their `id`, `class`, or `type` attributes if available.
- Only manipulate form fields (e.g., input, select, textarea) and buttons.
- Use `document.querySelector` or `document.querySelectorAll` to select elements.
- Ensure the code is safe and free from malicious content.
- Do not use any external libraries or make network requests.
- Do not include any comments in the code.
- For date fields, use the format 'YYYY-MM-DD'.

If the command doesn't make sense, reply I don't understand.
"""

  # Construct the user message without repeating the fixed prompt
  user_message = f"User Command: \"{command}\"\nHTML Content:\n{
    inputs_and_buttons}\n. Generate the Javascript code to perform the command, nothing else. Remember the constraints."

  # Call the LLM API
  completion = client.chat.completions.create(
      model="TheBloke/Mistral-7B-Instruct-v0.2-GGUF",
      messages=[
          {"role": "system", "content": fixed_prompt},
          {"role": "user", "content": user_message}
      ],
      temperature=0.0,
      stream=False,
  )

  response_text = completion.choices[0].message.content.strip()

  # Return the JavaScript code to the client
  return jsonify({
      'message': response_text,
      'javascript_code': response_text
  })


@app.route('/test-form', methods=['GET', 'POST'])
def test_form():
  if request.method == 'POST':
      # Save data from Page 1 to the session
    session['firstName'] = request.form['firstName']
    session['lastName'] = request.form['lastName']
    session['dob'] = request.form['dob']
    session['gender'] = request.form['gender']
    session['hobbies'] = request.form.getlist('hobbies')
    session['comments'] = request.form['comments']

    return redirect(url_for('test_form_page2'))
  return render_template('page1.html')


@app.route('/test-form/page2', methods=['GET', 'POST'])
def test_form_page2():
  if request.method == 'POST':
    # Retrieve data from session and Page 2
    firstName = session.get('firstName', '')
    lastName = session.get('lastName', '')
    dob = session.get('dob', '')
    gender = session.get('gender', '')
    hobbies = session.get('hobbies', [])
    comments = session.get('comments', '')

    email = request.form['email']
    phone = request.form['phone']

    # Process the data as needed (e.g., save to a database)

    # Clear session data
    session.clear()

    return render_template('thank_you.html', firstName=firstName, lastName=lastName,
                           dob=dob, gender=gender, hobbies=hobbies, comments=comments,
                           email=email, phone=phone)
  elif request.method == 'GET':
    # Ensure previous data is present
    if 'firstName' not in session:
      return redirect(url_for('test_form'))
  return render_template('page2.html')


@app.route('/test-form/back', methods=['POST'])
def test_form_back():
  # Handle the back action from Page 2 to Page 1
  return redirect(url_for('test_form'))


def record_audio_thread():
  global audio_data, phrase_time, stop_flag, listener_thread, transcription
  source = sr.Microphone(sample_rate=16000)

  with source:
    recognizer.adjust_for_ambient_noise(source)

  def record_callback(_, audio: sr.AudioData) -> None:
    if stop_flag:
      return
    data = audio.get_raw_data()
    data_queue.put(data)

  listener_thread = recognizer.listen_in_background(
      source, record_callback, phrase_time_limit=record_timeout)

  while not stop_flag:
    try:
      now = datetime.now(timezone.utc)
      if not data_queue.empty():
        phrase_complete = False
        if phrase_time and now - phrase_time > timedelta(seconds=phrase_timeout):
          phrase_complete = True
          audio_data = b''
        phrase_time = now
        audio_data += b''.join(data_queue.queue)
        data_queue.queue.clear()

        audio_np = np.frombuffer(
            audio_data, dtype=np.int16).astype(np.float32) / 32768.0

        segments, _ = audio_model.transcribe(
            audio_np, language="en")

        text = ''.join([segment.text for segment in segments]).strip()

        if phrase_complete:
          transcription.append(text)
        else:
          transcription[-1] = text

        socketio.emit('transcription', {'text': "\n".join(transcription)})

      sleep(0.25)

    except Exception as e:
      print(f"Error during transcription: {e}")
      break

  if listener_thread is not None:
    listener_thread(wait_for_stop=False)


@socketio.on('start_transcription')
def start_transcription():
  global stop_flag, transcription, audio_data, phrase_time
  stop_flag = False
  thread = Thread(target=record_audio_thread)
  thread.start()


@socketio.on('stop_transcription')
def stop_transcription():
  global stop_flag, listener_thread, transcription, audio_data, phrase_time
  stop_flag = True
  if listener_thread is not None:
    listener_thread(wait_for_stop=False)
  # Reset variables
  transcription = ['']
  audio_data = b''
  phrase_time = None


if __name__ == '__main__':
  socketio.run(app, debug=False)
