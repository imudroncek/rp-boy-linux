import pygame
import sys
from lib.SH1107Emulator import SH1107
import asyncio
import time
from core.ScreensHelper import ScreensHelper
from core.MainScreen import MainScreen
from core.PauseScreen import PauseScreen
from core.CountScreen import CountScreen
from core.InvaderScreen import InvaderScreen
from ExitScreen import ExitScreen
from core.OptionsScreen import OptionsScreen
from ButtonInput import ButtonInput
from core.Menu import Menu, MenuItem
from Options import Options
import framebuf

TARGET_FPS = 25
FRAME_TARGET = 1.0 / TARGET_FPS

async def main():
    width = 128
    height = 128
    options = Options()
    options.load()
    display = SH1107(options, width=1280, height=960, scale=6)
    #display = SH1107(options)
    canvas_buffer = bytearray(width * height // 8)
    canvas = framebuf.FrameBuffer(canvas_buffer, width, height, framebuf.MONO_VLSB)
    
    pygame.init()
  
    screensHelper = ScreensHelper()

    buttonInput = ButtonInput()
    mainScreen = MainScreen(width, height, display, canvas, buttonInput, screensHelper, "Main Menu")
    pauseScreen = PauseScreen(width, height, display, canvas, buttonInput, screensHelper, "Pause", mainScreen)
    optionsScreen = OptionsScreen(width, height, display, canvas, buttonInput, screensHelper, options, "Options", mainScreen)

    mainMenu = Menu([
        MenuItem("Counter", screen_class=CountScreen), 
        MenuItem("Invader", screen_class=InvaderScreen), 
        MenuItem("Options", screen_instance=optionsScreen),
        MenuItem("Exit", screen_class=ExitScreen)
    ])

    mainScreen.set_main_menu(mainMenu)

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