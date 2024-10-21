import pygame
import time

pygame.mixer.init()


def alarm_sound(alarm_path):
    pygame.mixer.music.load(alarm_path)
    try:
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.5)  # Keep looping while music is playing
    except KeyboardInterrupt:
        pygame.mixer.music.stop()


# alarm_sound(r"Burglar Alarm Going off with Sirens.mp3")
