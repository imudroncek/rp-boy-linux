import pygame
import sys
from SH1107Emulator import SH1107
import asyncio
import time
from ..rp_boy.ScreensHelper import ScreensHelper
from ..rp_boy.MainScreen import MainScreen
from ..rp_boy.PauseScreen import PauseScreen
from ..rp_boy.CountScreen import CountScreen
from ..rp_boy.InvaderScreen import InvaderScreen
from ExitScreen import ExitScreen
from ButtonInput import ButtonInput
from ..rp_boy.Menu import Menu, MenuItem

TARGET_FPS = 30
FRAME_TARGET = 1.0 / TARGET_FPS

async def main():
    width = 128
    height = 128
    display = SH1107(enable_mask=True)
    
    pygame.init()
  
    screensHelper = ScreensHelper()

    buttonInput = ButtonInput()
    mainMenu = Menu([MenuItem("Counter", screen_class=CountScreen), MenuItem("Invader", screen_class=InvaderScreen), MenuItem("Exit", screen_class=ExitScreen)])
    mainScreen = MainScreen(width, height, display, buttonInput, screensHelper, mainMenu, "Main Menu")
    pauseScreen = PauseScreen(width, height, display, buttonInput, screensHelper, "Pause", mainScreen)

    screensHelper.set_pause_screen(pauseScreen)

    screensHelper.set_active_screen(mainScreen)
    screensHelper.get_active_screen().init()
    screensHelper.get_active_screen().activate()
    
    while True:
        frame_start = time.perf_counter()
        
        buttonInput.update(pygame.event.get())
        screensHelper.get_active_screen().render()
        
        frame_duration = time.perf_counter() - frame_start
        if frame_duration < FRAME_TARGET:
            sleep_time = max(0.0, FRAME_TARGET - frame_duration)
            await asyncio.sleep(sleep_time)
        else:
            print(f"Warning: Frame dropped! Took {frame_duration}ms")

asyncio.run(main())