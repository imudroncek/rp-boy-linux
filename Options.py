import json
import os
from core.Menu import Menu, MenuItem

class Options:
    _FILENAME = "options.json"
    _TMP_FILENAME = "options.tmp"
    
    def __init__(self):
        self._json_ignore = ('options_menu')

        self.enable_mask = True
        self.green_background = False

        self.options_menu = Menu([
            OptionsMenuItem("Enable LCD Mask", False, lambda: setattr(self, 'enable_mask', not self.enable_mask)),
            OptionsMenuItem("Use Green Bgr", False, lambda: setattr(self, 'green_background', not self.green_background)),
            OptionsMenuItem("Save & Exit", True, lambda: self.save())
        ])

    def load(self):
        try:
            with open(self._FILENAME, "r") as f:
                data = json.load(f)
                for key, value in data.items():
                    if hasattr(self, key):
                        setattr(self, key, value)
            print("Configuration loaded.")
        except (OSError, ValueError):
            print("Config missing or corrupted. Creating defaults...")
            self.save()

    def save(self):
        """Saves configuration atomically using a temporary file."""
        try:
            # 1. Prepare data
            data = {
                k: v for k, v in self.__dict__.items() 
                if not k.startswith('_') and k not in self._json_ignore
            }
            
            # 2. Write to a temporary file first
            with open(self._TMP_FILENAME, "w") as f:
                json.dump(data, f)
            
            # On some platforms (like Windows/Standard Python), os.rename fails if 
            # the target exists. MicroPython's os.rename typically overwrites it.
            # To be safely cross-platform, we try-catch or remove the destination.
            try:
                os.remove(self._FILENAME)
            except OSError:
                pass # File didn't exist, which is fine
            
            # 3. Rename temp file to the real config file (Atomic operation)
            os.rename(self._TMP_FILENAME, self._FILENAME)
            print("Configuration saved atomically.")
            
        except OSError as e:
            print("Atomic save failed:", e)
            # Clean up the temp file if it was left behind
            try:
                os.remove(self._TMP_FILENAME)
            except OSError:
                pass

class OptionsMenuItem(MenuItem):

    def __init__(self, name, closable, handler):
        super().__init__(name, None, None)
        self.closable = closable
        self.handler = handler