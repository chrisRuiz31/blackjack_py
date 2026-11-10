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
LG_GREEN = (46, 170, 61)
YELLOW = (225, 150, 40)
BG_YELLOW = (199, 129, 24)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

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

def create_surface_with_drawing(shape_type, color, width, height, line_width=0):
    """Returns surface with a drawing shape type"""
    drawing_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    if shape_type == "RECT":
        pygame.draw.rect(drawing_surface, color, drawing_surface.get_rect(), line_width)
    elif shape_type == "CIRCLE":
        radius = width/2 + height^2/(8*width)
        pygame.draw.circle(drawing_surface, color, (width // 2, height // 2), radius, line_width)
    elif shape_type == "LINE":
        pygame.draw.line(drawing_surface, color, (0, height // 2), (width, height // 2), max(line_width, 1))
    else:
        raise ValueError(f"Not desired drawing type: {type}")
    return drawing_surface.convert_alpha()

class UIDrawingElement(Sprite):
    """User Interface element that can be added to a surface as a drawing"""
    def __init__(self, center_position, shape_type, color, width, height, line_width=0, action=None, clickable=True):
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
        self.shape_type = shape_type
        self.color = color
        self.width = width
        self.height = height
        self.line_width = line_width
        self.x = center_position[0]
        self.y = center_position[1]

        # Create the default image
        default_drawing = create_surface_with_drawing(shape_type=shape_type, color=color, width=width, height=height, line_width=line_width)
        
        # Create the image that shows when mouse is over the element
        highlighted_drawing = create_surface_with_drawing(shape_type=shape_type, color=color, width=int(width * 1.2), height=int(height * 1.2), line_width=line_width)

        # Add both images and their rects to lists
        self.images = [default_drawing, highlighted_drawing]
        self.rects = [default_drawing.get_rect(center=center_position), highlighted_drawing.get_rect(center=center_position)]
        # calls the init method of the parent sprite class
        super().__init__()
        self.action = action
        self.visible = True
        
    @property
    def image(self):
        return self.images[1] if self.mouse_over and self.clickable else self.images[0]
    
    @property
    def rect(self):
        return self.rects[1] if self.mouse_over and self.clickable else self.rects[0]
        
    def update(self, mouse_pos, mouse_up):
        """Updates the element's appearance depending on the mouse position
            and returns the button's action if clicked
        """
        if not self.visible:
            return None
        if self.rects[0].collidepoint(mouse_pos) and self.clickable:
            self.mouse_over = True
            if mouse_up:
                return self.action
        else:
            self.mouse_over = False

    def draw(self, surface):
        """Self explanatory, but to remind myself, THIS function
        draws the object and can be manipulated to allow to draw
        the object or not. Hence visibility being toggled."""
        if self.visible:
            surface.blit(self.image, self.rect)

class UIImageElement(Sprite):
    """User Interface element that can be added to a surface as an image"""
    def __init__(self, center_position, file, size, action=None, clickable=False, angle=0, can_animate=False, animation_instructions=None, clickable_size=1.3):
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
        self.clickable_size = clickable_size
        self.angle = angle

        """
        if front_card is not None:
            self.front_card = front_card
            self.back_side = file
        """

        # Creates the original image
        default_image = create_surface_with_image(file=file, size=size, angle=angle)

        # Creates a copy of the image that shows when mouse is over the element
        highlighted_image = create_surface_with_image(file=file, size=size*clickable_size, angle=angle)

        self.images = [default_image, highlighted_image] 
        self.rects = [default_image.get_rect(center=(self.x, self.y)), highlighted_image.get_rect(center=(self.x, self.y))]

        super().__init__()
        self.action = action
        self.animation_instructions = animation_instructions
        self.can_animate = can_animate
        self.animating = False
        self.visible = True

    @property
    def image(self):
        return self.images[1] if (self.mouse_over) and (self.clickable) else self.images[0]

    @property
    def rect(self):
        return self.rects[1] if (self.mouse_over) and (self.clickable) else self.rects[0]

    def set_image(self, file):
        """Swap this element's picture in place (keeps position, size, and angle)"""
        default_image = create_surface_with_image(file=file, size=self.size, angle=self.angle)
        highlighted_image = create_surface_with_image(file=file, size=self.size * self.clickable_size, angle=self.angle)
        self.images = [default_image, highlighted_image]
        self.rects = [default_image.get_rect(center=(self.x, self.y)), 
                      highlighted_image.get_rect(center=(self.x, self.y))]

    def update(self, mouse_pos, mouse_up):
        """Updates the element's appearance depending on the mouse position
            and returns the button's action if clicked
        """
        if not self.visible:
            return None
        if self.rects[0].collidepoint(mouse_pos) and self.clickable:
            self.mouse_over = True
            if mouse_up:
                return self.action
        else:
            self.mouse_over = False

    def draw(self, surface):
        """Self explanatory, but to remind myself, THIS function
        draws the object and can be manipulated to allow to draw
        the object or not. Hence visibility being toggled."""
        if self.visible:
            surface.blit(self.image, self.rect)

class UITextElement(Sprite):
    """User Interface element that can be added to a surface as text."""
    def __init__(self, center_position, text, font_size, bg_rgb, text_rgb, amount=0, action=None, clickable=True, clickable_size=1.3):
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
        self.clickable_size = clickable_size
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
        self.visible = True
    
    @property
    def image(self):
            return self.images[1] if self.mouse_over and self.clickable else self.images[0]
    
    @property
    def rect(self):
            return self.rects[1] if self.mouse_over and self.clickable else self.rects[0]
    
    def update_amount(self, text):
        self.text = text
        self.images[0] = create_surface_with_text(text, self.font_size, self.text_rgb, self.bg_rgb)
        self.images[1] = create_surface_with_text(text, self.font_size * 1.2, self.text_rgb, self.bg_rgb)

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
        if not self.visible:
            return None
        if self.rects[0].collidepoint(mouse_pos) and self.clickable:
            self.mouse_over = True
            if mouse_up:
                return self.action
        else:
            self.mouse_over = False

    def draw(self, surface):
        """Self explanatory, but to remind myself, THIS function
        draws the object and can be manipulated to allow to draw
        the object or not. Hence visibility being toggled."""
        if self.visible:
            surface.blit(self.image, self.rect)

# Helper function to make sure that the elements are refreshing per frame
def refresh_bank_ui(buttons, bank):
    """Updates the bank text and hides ADD chips worth more than the bank."""
    for element in buttons:
        if hasattr(element, "bank"):
            element.update_amount(f"Bank:{bank}")
        if hasattr(element, "value_string"):
            element.visible = int(element.value_string) <= bank

def game_loop(screen, buttons, game_state, betting_chips=None):
    running = True
    bank = 900
    refresh_bank_ui(buttons, bank)
    while running:
        mouse_up = False
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_up = True
            if event.type == pygame.QUIT:
                running = False

        if game_state == GameState.TITLE:
            screen.fill(RED)
        if game_state == GameState.NEWGAME:
            screen.fill(GREEN)
        if game_state == GameState.HOWTO:
            screen.fill(YELLOW)

        ui_action = None
        for button in buttons:
            ui_action = button.update(pygame.mouse.get_pos(), mouse_up)
            if ui_action == "NEXT":
                for element in buttons:
                    if hasattr(element, "image_files"):
                        element.image_index = (element.image_index + 1)
                        element.set_image(element.image_files[element.image_index])
                        if element.image_index == len(element.image_files) - 1:
                            button.visible = False
            elif ui_action == "ADD":
                #print(f"pressed the {button.value_string}")
                value = int(button.value_string)
                if value <= bank:
                    new_chip = UIImageElement(center_position=(460, 470),
                                file=f"assets/chip_{button.value_string}.png",
                                size=0.8,
                                clickable=True,
                                action="REMOVE",
                                clickable_size=1.2)
                    new_chip.value = value
                    bank -= value
                    buttons.add(new_chip, layer=2)
                    betting_chips.append(new_chip)
                    refresh_bank_ui(buttons, bank)
              
            elif ui_action == "REMOVE":
                mouse_pos = pygame.mouse.get_pos()
                for chip in reversed(betting_chips):
                    if chip.rects[0].collidepoint(mouse_pos):
                        chip.kill()
                        betting_chips.remove(chip)
                        bank += chip.value
                        refresh_bank_ui(buttons, bank)
                        break
                break
            elif ui_action == "DEAL":
                buttons.remove(betting_chips)
                betting_chips.clear()
            elif ui_action is not None:
                return ui_action

        for button in buttons:       
            button.draw(screen)
        pygame.display.flip()
    pygame.quit()
    sys.exit()

def title_screen(screen, game_state):
    title = UITextElement(center_position=(300, 100), 
                            font_size=90, 
                            bg_rgb=RED, 
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
                                    bg_rgb=BG_RED,
                                    text_rgb=WHITE, 
                                    text="START",
                                    action = GameState.NEWGAME)

    howto_button = UITextElement(center_position=(300, 500), 
                                    font_size=30, 
                                    bg_rgb=BG_RED,
                                    text_rgb=WHITE, 
                                    text="HOW TO PLAY",
                                    action = GameState.HOWTO)

    quit_button = UITextElement(center_position=(300, 540), 
                                font_size=30, 
                                bg_rgb=BG_RED,
                                text_rgb=WHITE, 
                                text="EXIT",
                                action = GameState.QUIT)

    buttons = RenderUpdates(title, card_1, card_2, menu_chips, start_button, howto_button, quit_button)
    return game_loop(screen, buttons, game_state)

def new_game(screen, game_state):
    return_button = UITextElement(center_position=(500, 50), 
                              font_size=30, 
                              bg_rgb=BG_GREEN, 
                              text_rgb=WHITE, 
                              text="GO BACK",
                              action = GameState.TITLE)

    player_amount = 900
    bank_text = UITextElement(center_position=(100, 50),
                                font_size=30,
                                bg_rgb=GREEN, 
                                text_rgb=WHITE, 
                                text=F"Bank:{player_amount}",
                                clickable=False)
    bank_text.bank = 1
    
    chip_values = ["01", "05", "25", "50", "100", "500"]
    game_chips = []
    chip_x_position = 60
    # Adding chips
    for i in range(6):
        chip = UIImageElement(center_position=(chip_x_position, 425) if i < 3 else (chip_x_position, 525),
                            file=f"assets/chip_{chip_values[i]}.png",
                            size = 0.4,
                            clickable=True,
                            clickable_size=1.02,
                            action="ADD"
                            )
        chip_x_position += 110
        if chip_x_position > 280:
            chip_x_position = 60
        game_chips.append(chip)
        chip.value_string = chip_values[i]

    rectangle = UIDrawingElement(center_position=(150, 480),
                                 shape_type="RECT",
                                 color=LG_GREEN,
                                 width=370,
                                 height=320,
                                 action=None,
                                 clickable=False)
    
    rectangle2 = UIDrawingElement(center_position=(150, 480),
                                     shape_type="RECT",
                                     color=BLACK,
                                     width=380,
                                     height=330,
                                     action=None,
                                     clickable=False)

    all_in = UITextElement(center_position=(80, 350),
                                    font_size=30,
                                    bg_rgb=GREEN, 
                                    text_rgb=WHITE, 
                                    text="ALL IN",
                                    clickable=True)

    deal = UITextElement(center_position=(460, 330),
                                    font_size=60,
                                    bg_rgb=BG_GREEN, 
                                    text_rgb=WHITE, 
                                    text="DEAL",
                                    clickable=True)

    starting_chip = UIImageElement(center_position=(460, 470),
                                    file=f"assets/chip_100.png",
                                    size=0.8,
                                    clickable=True,
                                    action="REMOVE",
                                    clickable_size=1.2)
    starting_chip.value = 100

    betting_phase = [rectangle2, rectangle, all_in, game_chips, deal, starting_chip]
    betting_chips = [starting_chip]
    buttons = pygame.sprite.LayeredUpdates(return_button, bank_text, betting_phase)
    return game_loop(screen, buttons, game_state, betting_chips)

def how_to(screen, game_state):
    return_button = UITextElement(center_position=(475, 50), 
                              font_size=30, 
                              bg_rgb=BG_YELLOW, 
                              text_rgb=WHITE, 
                              text="MENU",
                              action = GameState.TITLE)
    next_button = UITextElement(center_position=(475, 100), 
                                  font_size=30, 
                                  bg_rgb=BG_YELLOW, 
                                  text_rgb=WHITE, 
                                  text="NEXT",
                                  action = "NEXT")

    how_to_images = ["assets/how_to_play_part1.jpeg",
                     "assets/how_to_play_part2.jpeg",
                     "assets/how_to_play_part3.jpeg"]
    
    how_to = UIImageElement(center_position=(300, 350),
                               file=how_to_images[0],
                               size = 1,
                               clickable=False
                               )
    how_to.image_index = 0
    how_to.image_files = how_to_images

    buttons = RenderUpdates(return_button, next_button, how_to)
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