# sound.py

import os
import pygame
from .generate_beep import generate_beep
from .get_beep_filename import get_beep_filename
from ..config import BEEP_FREQUENCY, BEEP_DURATION, BEEP_VOLUME

pygame.mixer.init()

def play_sound():
    BEEP_FILENAME = get_beep_filename()
    if not os.path.exists(BEEP_FILENAME):
        generate_beep(BEEP_FREQUENCY, BEEP_DURATION, BEEP_VOLUME, BEEP_FILENAME)
    pygame.mixer.music.load(BEEP_FILENAME)
    pygame.mixer.music.play()
