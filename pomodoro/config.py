
import os
import hashlib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORK_TIME_MIN = 25
BREAK_TIME_MIN = 5
BEEP_FREQUENCY = 440
BEEP_DURATION = 0.5
BEEP_VOLUME = 0.5

def get_beep_filename():
    if not os.path.exists(os.path.join(BASE_DIR, 'assets')):
        os.makedirs(os.path.join(BASE_DIR, 'assets'))
    params = f"{BEEP_FREQUENCY}_{BEEP_DURATION}_{BEEP_VOLUME}"
    params_hash = hashlib.md5(params.encode()).hexdigest()
    return os.path.join(BASE_DIR, 'assets', f'beep_{params_hash}.wav')

BEEP_FILENAME = get_beep_filename()