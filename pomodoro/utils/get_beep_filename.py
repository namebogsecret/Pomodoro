# utils/get_beep_filename.py

import os
import hashlib
from ..config import BEEP_FREQUENCY, BEEP_DURATION, BEEP_VOLUME

def get_beep_filename():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    if not os.path.exists(os.path.join(BASE_DIR, '..', 'assets')):
        os.makedirs(os.path.join(BASE_DIR, '..', 'assets'))
    params = f"{BEEP_FREQUENCY}_{BEEP_DURATION}_{BEEP_VOLUME}"
    params_hash = hashlib.md5(params.encode()).hexdigest()
    return os.path.join(BASE_DIR, '..', 'assets', f'beep_{params_hash}.wav')
