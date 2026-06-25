import pygame

class MockPhysicalButton:
    """Simulates a physical hardware button register with assignable callbacks."""
    def __init__(self):
        # This will hold the callback method assigned by Screen.init()
        self.when_pressed = None 

class InputButton:
    """Matches your original structural wrapper wrapper."""
    def __init__(self, name):
        self.name = name
        self.physical_button = MockPhysicalButton()

class ButtonInput:
    def __init__(self):
        # Replicate your exact attribute assignments
        self.a = InputButton("Button A")
        self.b = InputButton("Button B")
        self.start = InputButton("Start")
        self.select = InputButton("Select")
        self.up = InputButton("D-Pad Up")
        self.down = InputButton("D-Pad Down")
        self.left = InputButton("D-Pad Left")
        self.right = InputButton("D-Pad Right")
        self.zl = InputButton("Button ZL")
        self.zr = InputButton("Button ZR")

        # Define your local PC keyboard layout mappings
        self._key_map = {
            pygame.K_a: self.a,
            pygame.K_b: self.b,
            pygame.K_RETURN: self.start,
            pygame.K_SPACE: self.select,
            pygame.K_UP: self.up,
            pygame.K_DOWN: self.down,
            pygame.K_LEFT: self.left,
            pygame.K_RIGHT: self.right,
            pygame.K_q: self.zl,
            pygame.K_e: self.zr,
        }

    def update(self, events):
        """
        Pumps the Pygame event stream buffer. If a registered key is pressed,
        it automatically fires the assigned callback function.
        """
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in self._key_map:
                    target_button = self._key_map[event.key]
                    # If the active screen has bound a callback function, execute it!
                    if target_button.physical_button.when_pressed:
                        target_button.physical_button.when_pressed()