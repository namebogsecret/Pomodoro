import os
import pygame
from .generate_beep import generate_beep
from ..config import BEEP_FILENAME, BEEP_FREQUENCY, BEEP_DURATION, BEEP_VOLUME

pygame.mixer.init()

def play_sound():
    if not os.path.exists(BEEP_FILENAME):
        generate_beep(BEEP_FREQUENCY, BEEP_DURATION, BEEP_VOLUME, BEEP_FILENAME)
    pygame.mixer.music.load(BEEP_FILENAME)
    pygame.mixer.music.play()
