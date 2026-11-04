import deck
import pygame
import sys
import random
import pygame.freetype
from pygame.sprite import Sprite
from pygame.rect import Rect
from pygame.sprite import RenderUpdates
from enum import Enum

WIDTH, HEIGHT = 600, 600
CENTER = WIDTH/2, HEIGHT/2
RED = (150, 46, 61)
BG_RED = (100, 46, 61)
BLUE = (46, 61, 150) 
BG_BLUE = (46, 61, 100)
GREEN = (46, 150, 61)
BG_GREEN = (46, 100, 61)
YELLOW = (225, 150, 40)
BG_YELLOW = (199, 129, 24)
WHITE = (255, 255, 255)

class GameState(Enum):
    QUIT = -1
    TITLE = 0
    HOWTO = 1
    NEWGAME = 2
    NEXTLEVEL = 3

class AnimState(Enum):
    STATIC = 0
    UP = 1
    UP_LEFT = 2
    UP_RIGHT = 3
    DOWN = 4
    DOWN_LEFT = 5
    DOWN_RIGHT = 6
    LEFT = 7
    RIGHT = 8

def create_surface_with_text(text, font_size, text_rgb, bg_rgb):
    """Returns surface with text written on"""
    font = pygame.freetype.SysFont("Courier", font_size, bold=True)
    surface, _ = font.render(text=text, fgcolor=text_rgb, bgcolor=bg_rgb)
    return surface.convert_alpha()

def create_surface_with_image(file, size, angle):
    """Returns surface with image"""
    image_surface = pygame.image.load(file)
    resized_image = pygame.transform.rotozoom(image_surface, angle, size)
    return resized_image.convert_alpha()

class UIImageElement(Sprite):
    """User Interface element that can be added to a surface as an image"""
    def __init__(self, center_position, file, size, action=None, clickable=False, angle=0, can_animate=False, animation_instructions=None):
        """
        Args:
        center_position - tuple(x, y)
        file - string of the image to load
        size - image size(int)
        action - contains a string or GameState
        clickable - boolean value
        angle - floating type value
        can_animate - boolean value
        animation_instructions - holds an amount of animations(list)
        """
        self.mouse_over = False # Indicates that the mouse is over the element
        self.clickable = clickable # Indicates that the image will change size, when mouse is over the element
        self.x = center_position[0]
        self.y = center_position[1]

        self.size = size
        self.angle = angle

        """
        if front_card is not None:
            self.front_card = front_card
            self.back_side = file
        """

        # Creates the original image
        default_image = create_surface_with_image(file=file, size=size, angle=angle)

        # Creates a copy of the image that shows when mouse is over the element
        highlighted_image = create_surface_with_image(file=file, size=size*1.2, angle=angle)

        self.images = [default_image, highlighted_image] 
        self.rects = [default_image.get_rect(center=(self.x, self.y)), highlighted_image.get_rect(center=(self.x, self.y))]

        super().__init__()
        self.action = action
        self.animation_instructions = animation_instructions
        self.can_animate = can_animate
        self.animating = False

    @property
    def image(self):
        return self.images[1] if (self.mouse_over) and (self.clickable) else self.images[0]

    @property
    def rect(self):
        return self.rects[1] if (self.mouse_over) and (self.clickable) else self.rects[0]

    def update(self, mouse_pos, mouse_up):
        """Updates the element's appearance depending on the mouse position
            and returns the button's action if clicked
        """
        if self.rect.collidepoint(mouse_pos) and self.clickable:
            self.mouse_over = True
            if mouse_up:
                return self.action
        else:
            self.mouse_over = False

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class UITextElement(Sprite):
    """User Interface element that can be added to a surface as text."""
    def __init__(self, center_position, text, font_size, bg_rgb, text_rgb, amount=0, action=None, clickable=True):
        """
        Args:
        center_position - tuple (x, y)
        text - string of text to write
        font_size - int
        bg_rgb (background color) - tuple (r,g,b)
        text_rgb (text color) - tuple (r,g,b)
        """
        self.mouse_over = False # Indicates if the mouse is over the element
        self.clickable = clickable
        self.amount = amount
        self.text = text
        self.font_size = font_size
        self.text_rgb = text_rgb
        self.bg_rgb = bg_rgb

        # Create the default image
        default_image = create_surface_with_text(text=text, font_size=font_size, text_rgb=text_rgb, bg_rgb=bg_rgb)
        
        # Create the image that shows when mouse is over the element
        highlighted_image = create_surface_with_text(text=text, font_size=font_size * 1.2, text_rgb=text_rgb, bg_rgb=bg_rgb)

        # Add both images and their rects to lists
        self.images = [default_image, highlighted_image]
        self.rects = [default_image.get_rect(center=center_position), highlighted_image.get_rect(center=center_position)]
        # calls the init method of the parent sprite class
        super().__init__()
        self.action = action
    
    @property
    def image(self):
            return self.images[1] if self.mouse_over and self.clickable else self.images[0]
    
    @property
    def rect(self):
            return self.rects[1] if self.mouse_over and self.clickable else self.rects[0]
    """
    def update_amount(self, amount_change):
        self.amount = amount_change
        self.text = self.text[:10] + str(self.amount)
    """
    def update_text(self, background_rgb):
        self.images[0] = create_surface_with_text(
            text=self.text, 
            font_size=self.font_size, 
            text_rgb=self.text_rgb, 
            bg_rgb=background_rgb)
        if self.clickable:
            self.images[1] = create_surface_with_text(text=self.text, 
                                                      font_size=self.font_size * 1.2, 
                                                      text_rgb=self.text_rgb, 
                                                      bg_rgb=background_rgb)
        
    def update(self, mouse_pos, mouse_up):
        """Updates the element's appearance depending on the mouse position
            and returns the button's action if clicked
        """
        if self.rect.collidepoint(mouse_pos) and self.clickable:
            self.mouse_over = True
            if mouse_up:
                return self.action
        else:
            self.mouse_over = False

    def draw(self, surface):
        surface.blit(self.image, self.rect)

def game_loop(screen, buttons, game_state):
    running = True

    while running:
        mouse_up = False
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_up = True
            if event.type == pygame.QUIT:
                running = False

        if game_state == GameState.TITLE:
            screen.fill(BLUE)
        if game_state == GameState.NEWGAME:
            screen.fill(GREEN)
        if game_state == GameState.HOWTO:
            screen.fill(RED)

        ui_action = None
        for button in buttons:
            ui_action = button.update(pygame.mouse.get_pos(), mouse_up)

            if ui_action is not None:
                return ui_action
        buttons.draw(screen)
        pygame.display.flip()
    pygame.quit()
    sys.exit()

def title_screen(screen, game_state):
    title = UITextElement(center_position=(300, 100), 
                            font_size=90, 
                            bg_rgb=BLUE, 
                            text_rgb=WHITE, 
                            text="Blackjack",
                            action = None,
                            clickable=False)

    menu_chips = []
    for i in range(1, 6):
        chip = UIImageElement(center_position=(220 + (i * 25), 270 + (i * 15)),
                              file=f"assets/menu_chip_0{i}.png",
                              size=0.8,
                              clickable=False)
        menu_chips.append(chip)

    card_1 = UIImageElement(center_position=(320, 260),
                            file="cards/clubs_10.png",
                            angle=10,
                            size=0.5,
                            clickable=False)
    
    card_2 = UIImageElement(center_position=(370, 265),
                            angle=-25,
                            file="cards/hearts_A.png",
                            size=0.5,
                            clickable=False)

    start_button = UITextElement(center_position=(300, 460), 
                                    font_size=30, 
                                    bg_rgb=BG_BLUE,
                                    text_rgb=WHITE, 
                                    text="START",
                                    action = GameState.NEWGAME)

    howto_button = UITextElement(center_position=(300, 500), 
                                    font_size=30, 
                                    bg_rgb=BG_BLUE,
                                    text_rgb=WHITE, 
                                    text="HOW TO PLAY",
                                    action = GameState.HOWTO)

    quit_button = UITextElement(center_position=(300, 540), 
                                font_size=30, 
                                bg_rgb=BG_BLUE,
                                text_rgb=WHITE, 
                                text="EXIT",
                                action = GameState.QUIT)

    buttons = RenderUpdates(title, card_1, card_2, menu_chips, start_button, howto_button, quit_button)
    return game_loop(screen, buttons, game_state)

def new_game(screen, game_state):
    return_button = UITextElement(center_position=(475, 50), 
                              font_size=30, 
                              bg_rgb=BG_GREEN, 
                              text_rgb=WHITE, 
                              text="GO BACK",
                              action = GameState.TITLE)

    buttons = RenderUpdates(return_button)
    return game_loop(screen, buttons, game_state)

def how_to(screen, game_state):
    return_button = UITextElement(center_position=(475, 50), 
                              font_size=30, 
                              bg_rgb=BG_RED, 
                              text_rgb=WHITE, 
                              text="GO BACK",
                              action = GameState.TITLE)

    buttons = RenderUpdates(return_button)
    return game_loop(screen, buttons, game_state)

def main():
    pygame.init()
    clock = pygame.time.Clock()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    game_state = GameState.TITLE

    running = True
    while running:
        clock.tick(60)
        if game_state == GameState.TITLE:
            game_state = title_screen(screen, game_state)
        if game_state == GameState.NEWGAME:
            game_state = new_game(screen, game_state)
        if game_state == GameState.HOWTO:
            game_state = how_to(screen, game_state)
        if game_state == GameState.QUIT:
            pygame.quit()
            running = False

if __name__ == '__main__':
    main()