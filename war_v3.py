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
    HOW_TO = 1
    NEWGAME = 2
    NEXT_LEVEL = 3
    P1_WINS = 4
    P2_WINS = 5
    TIED = 6

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

P1_ANIMS= [AnimState.UP_RIGHT, AnimState.LEFT]
P2_ANIMS = [AnimState.DOWN_LEFT, AnimState.RIGHT]

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

class UISpriteElement(Sprite):
    """User Interface element that can be added to a surface as image"""
    def __init__(self, center_position, file, size, action=None, clickable=False, angle=0, is_animated=False, animation_instructions=None, front_card=None, rank=None, is_card=False, belongs_to=0):
        """
        Args:
        center_position - tuple(x, y)
        file - string of the image to load
        size - int
        """
        self.mouse_over = False # Indicates that the mouse is over the element
        self.clickable = clickable
        self.x = center_position[0]
        self.y = center_position[1]


        self.size = size
        self.angle = angle
        self.is_card = is_card
        self.belongs_to = belongs_to
        
        if rank is not None:
            self.rank = rank

        if front_card is not None:
            self.front_card = front_card
            self.back_side = file

        # Create the default image
        default_image = create_surface_with_image(file=file, size=size, angle=angle)

        # Create the image that shows when mouse is over the element
        highlighted_image = create_surface_with_image(file=file, size=size*1.2, angle=angle)

        self.images = [default_image, highlighted_image] 
        self.rects = [default_image.get_rect(center=(self.x, self.y)), highlighted_image.get_rect(center=(self.x, self.y))]
        
        super().__init__()

        self.action = action
        self.animation_instructions = animation_instructions
        self.is_animated = is_animated

        self.animating = False
        self.frames = 0
        self.pending_action = None
        self.current_animation = 0
        self.max_frames = 40

        self.pause_until = 0
        self.paused = False

    @property
    def image(self):
        return self.images[1] if self.mouse_over and self.clickable else self.images[0]
        
    @property
    def rect(self):
        return self.rects[1] if (self.mouse_over) and (self.clickable) else self.rects[0]
        
    def toggle_clickable(self, value:bool):
        self.clickable = value
        self.max_frames = 40
        self.mouse_over = False

    def show_clickable(self):
        return self.clickable
    
    def show_animating(self):
        return self.animating

    def set_anim_instructions(self, instructions):
        self.animation_instructions = instructions
    
    def toggle_anim(self):
        self.is_animated = not self.is_animated

    def change_side_card(self, file):
        self.images[0] = create_surface_with_image(file=file, size=self.size, angle=self.angle)
        self.images[1] = create_surface_with_image(file=file, size=self.size * 1.2, angle=self.angle)

    def move(self, dx, dy, delay):
        pause_start = pygame.time.get_ticks()
        pause_duration = delay
        running = True
        while running:
            current_time = pygame.time.get_ticks()
            if current_time - pause_start >= pause_duration:
                self.rects[0].center = (dx, dy)
                running = False
        
        self.rects[1].center = self.rects[0].center
        
    def animation(self, animation_type):
            dx, dy = 0, 0
            if animation_type == AnimState.UP:
                dy = -3
                dx = 0
            if animation_type == AnimState.DOWN:
                dy = 3
                dx = 0
            if animation_type == AnimState.UP_LEFT:
                dy = -3
                dx = -3
            if animation_type == AnimState.UP_RIGHT:
                dy = -3
                dx = 3
            if animation_type == AnimState.DOWN_LEFT:
                dy = 3
                dx = -3
            if animation_type == AnimState.DOWN_RIGHT:
                dy = 3
                dx = 3
            if animation_type == AnimState.LEFT:
                dy = 0
                dx = -3
            if animation_type == AnimState.RIGHT:
                dy = 0
                dx = 3

            self.rects[0].move_ip(dx, dy)
            self.rects[1].center = self.rects[0].center
        
    def update(self, mouse_pos, mouse_up, war_state=False):
        """Updates the element's appearance depending on the mouse position
            and returns the button's action if clicked
        """
        current_time = pygame.time.get_ticks()
        if self.paused:
            if current_time < self.pause_until:
                return None
            
            self.paused = False
            self.frames = 0

            if self.current_animation >= len(self.animation_instructions):
                self.animating = False
                self.toggle_anim()
                self.current_animation = 0
                return self.pending_action

        if self.animating:
            animation = self.animation_instructions[self.current_animation]
            self.animation(animation)
            self.frames += 1

            if self.frames >= self.max_frames:
                self.current_animation += 1
                self.frames = 0

                if self.current_animation >= len(self.animation_instructions):
                    self.animating = False
                    self.toggle_anim()
                    self.current_animation = 0
                    return self.pending_action

                if self.current_animation == len(self.animation_instructions) - 1:
                    self.max_frames = 20
                else:
                    self.max_frames = 40

                self.paused = True
                self.pause_until = current_time + 300
                
        if self.rect.collidepoint(mouse_pos) and self.clickable:
            self.mouse_over = True
            if mouse_up:
                if self.is_animated:
                    if not war_state:
                        self.change_side_card(self.front_card)
                    self.animating = True
                    self.toggle_clickable(False)
                    self.frames = 0
                    self.max_frames = self.max_frames
                    self.pending_action = self.action
                    return None
                else:
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

    def update_amount(self, amount_change):
        self.amount = amount_change
        self.text = self.text[:10] + str(self.amount)

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
        
    def update(self, mouse_pos, mouse_up, war_state=False):
        """Updates the element's appearance depending on the mouse position
            and returns the button's action if clicked
        """
        if self.rect.collidepoint(mouse_pos) and self.clickable:
            self.mouse_over = True
            if mouse_up:
                return self.action
        else:
            self.mouse_over = False

        if war_state:
            background_rgb = BG_YELLOW if self.clickable else YELLOW
        else:
            background_rgb = self.bg_rgb
        self.update_text(background_rgb)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# Helper method for game levels
def game_loop(screen, buttons, game_state, player_holding=None, hands_lst=None):
    """ Handles game loop until an action is return by a button in the
    buttons sprite renderer.
    """
    if player_holding is None:
        player_holding = [[], []]

    current_ranks = []
    current_cards = []

    hold_cards = []
    p1_total, p2_total = 0, 0

    current_turn = 0

    war_state = False
    war_count = 0

    running = True

    while running:

        #Updates the player's totals
        for button in buttons:
            if hasattr(button, "hand"):
                if button.hand == 1:
                    p1_total = len(button.display_hands) + len(player_holding[0])
                elif button.hand == 2:
                    p2_total = len(button.display_hands) + len(player_holding[1])

        mouse_up = False
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_up = True
            if event.type == pygame.QUIT:
                running = False

        # Changes the color of the screen depending of the gamestate
        if game_state == GameState.TITLE or game_state == GameState.TIED:
            screen.fill(GREEN)
        if game_state == GameState.NEWGAME or game_state == GameState.P2_WINS:
            screen.fill(BLUE) if not war_state else screen.fill(YELLOW)
        if game_state == GameState.HOW_TO or game_state == GameState.P1_WINS:
            screen.fill(RED)    

        # Handles user clicks in the screen and the game's logic
        ui_action = None
        for button in buttons:
            ui_action = button.update(pygame.mouse.get_pos(), mouse_up, war_state)

            if hasattr(button, "hand"):
                war_state, war_count, ui_action = handling_cards(ui_action, card=button, 
                                current_ranks=current_ranks,
                                current_turn=current_turn,
                                hold_cards=hold_cards,
                                buttons=buttons,
                                current_cards=current_cards, player_holding=player_holding,
                                war_state=war_state, war_count=war_count, hands_lst=hands_lst, 
                                totals = [p1_total, p2_total])
                
            if ui_action is not None and ui_action not in ["END", "DRAW"]:
                return ui_action

            if ui_action == "END":
                if p1_total > p2_total:
                    ui_action = GameState.P1_WINS
                if p1_total < p2_total:
                    ui_action = GameState.P2_WINS
                if p1_total == p2_total:
                    ui_action = GameState.TIED
                return ui_action

        # Updates the player's amount for the UI
        for button in buttons:
            if hasattr(button, "player"):
                if button.player == 1:
                    button.update_amount(p1_total)
                elif button.player == 2:
                    button.update_amount(p2_total)

        buttons.draw(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

def handling_cards(ui_action, card, current_ranks, current_turn, hold_cards, buttons, current_cards, player_holding, war_state, war_count, hands_lst, totals):
    #Made just to handle card when actions are done
    if ui_action == "DRAW":
        buttons.move_to_front(card)
        player = card.belongs_to - 1
        current_turn = (player + 1) % 2
        player_string = f"Player {player + 1}"
        player_amount = len(card.display_hands) + len(player_holding[player])
        if totals[player] <= 1:
            ui_action = "END"
            return war_state, war_count, ui_action
        current_ranks.append({ 
            player_string:{'rank': card.rank,
            'amount':player_amount}
        })
        current_cards.append(card)
        drawn_card = card.display_hands.pop()
        hold_cards.append(drawn_card)

        if (len(current_ranks) % 2 == 0):
            war_state, war_count = determine_winner(current_ranks=current_ranks, 
                                current_cards=current_cards,
                                hold_cards=hold_cards,
                                player_holding=player_holding,
                                war_state=war_state,
                                war_count=war_count,
                                hands_lst=hands_lst)

        if len(card.display_hands) < 1:               
            for cards in player_holding[player]:
                cards.toggle_anim()
                cards.change_side_card(cards.back_side)
                cards.display_hands = hands_lst[player]
                cards.hand = player + 1
                cards.move(dx=300, dy=450, delay=0) if player == 0 else cards.move(dx=300, dy=150, delay=0)
                buttons.move_to_front(cards)
            card.display_hands.extend(player_holding[player])
            player_holding[player].clear()

        if current_turn == 1:
            # It's now Player's 2 turn
            # Instead of waiting for a click
            trigger_draw(buttons=buttons, player_index = 1, war_state=war_state)
        else:
            enable_current_card(buttons=buttons, current_turn=current_turn, index=-1)

    return war_state, war_count, ui_action

def trigger_draw(buttons, player_index, war_state, index=-1):
    target_hand = None
    for button in buttons:
        if hasattr(button, "hand") and button.hand == player_index + 1:
            target_hand = button.display_hands
    if not target_hand:
        return
    
    card = target_hand[index]

    if card.is_animated:
        if not war_state:
            card.change_side_card(card.front_card)
        card.animating = True
        card.toggle_clickable(False)
        card.frames = 0
        card.pending_action = card.action

def enable_current_card(buttons, current_turn, index):
    target_hand = None
    for button in buttons:
        if hasattr(button, "hand") and button.hand == current_turn + 1:
            if button in button.display_hands:
                button.toggle_clickable(False)
            target_hand = button.display_hands
    if target_hand:
        target_hand[index].toggle_clickable(True)

def determine_winner(current_ranks, current_cards, hold_cards, player_holding, war_state, war_count, hands_lst):
    """Initiates the procedure of the game of war"""
    p1_rank = current_ranks[-2]['Player 1']['rank']
    p2_rank = current_ranks[-1]['Player 2']['rank']

    if not war_state:
        if p1_rank == p2_rank: # WAR
            war_state = True
            war_count += 1
            return war_state, war_count
        
        if p1_rank > p2_rank: # BATTLE (P1 WINS)
            for card in hold_cards:
                card.set_anim_instructions(P1_ANIMS)
                card.belongs_to = 1
                card.move(dx=420, dy=450, delay=200)
                player_holding[0].insert(0, card)
            
            print(f"P1 Wins")

        if p1_rank < p2_rank: # BATTLE (P2 WINS)
            for card in hold_cards:
                card.set_anim_instructions(P2_ANIMS)
                card.belongs_to = 2
                card.move(dx=180, dy=150, delay=200)
                player_holding[1].insert(0, card)

            print(f"P2 Wins")

        war_state = False
        war_count = 0

        current_ranks.clear()
        current_cards.clear()
        hold_cards.clear()

        return war_state, war_count
    else: # WAR STATE
        if war_count < 3:
            war_count += 1
        else:
            war_state = False
            war_count = 0
        return war_state, war_count

def title_screen(screen, game_state):
        title = UITextElement(center_position=(300, 100), 
                            font_size=120, 
                            bg_rgb=GREEN, 
                            text_rgb=WHITE, 
                            text="WAR",
                            action = None,
                            clickable=False)

        start_button = UITextElement(center_position=(300, 460), 
                            font_size=30, 
                            bg_rgb=BG_GREEN, 
                            text_rgb=WHITE, 
                            text="START",
                            action = GameState.NEWGAME)
        
        how_to_button = UITextElement(center_position=(300, 500), 
                            font_size=30, 
                            bg_rgb=BG_GREEN, 
                            text_rgb=WHITE, 
                            text="HOW TO PLAY",
                            action = GameState.HOW_TO)
        
        quit_button = UITextElement(center_position=(300, 540), 
                            font_size=30, 
                            bg_rgb=BG_GREEN,
                            text_rgb=WHITE, 
                            text="EXIT",
                            action = GameState.QUIT)
        
        shield = UISpriteElement(center_position=(300, 300),
                               file="assets/shield.png",
                               size = 0.8,
                               clickable=False,
                               )
        
        card = UISpriteElement(center_position=(300, 300),
                               file="cards/back_dark.png",
                               size = 0.5,
                               clickable=False,
                               angle=-15
                               )
        
        card2 = UISpriteElement(center_position=(320, 300),
                               file="cards/clubs_2.png",
                               size = 0.5,
                               clickable=False,
                               angle=15
                               )
        
        buttons = RenderUpdates(title, start_button, how_to_button, quit_button, shield, card, card2)

        return game_loop(screen, buttons, game_state)

def how_to(screen, game_state):
    instructions = UISpriteElement(center_position=(300, 300),
                               file="assets/instructions_clear.png",
                               size = 0.4,
                               clickable=False
                               )
    return_button = UITextElement(center_position=(475, 50), 
                          font_size=30, 
                          bg_rgb=BG_RED, 
                          text_rgb=WHITE, 
                          text="GO BACK",
                          action = GameState.TITLE)
    
    buttons = RenderUpdates(instructions, return_button)
    return game_loop(screen, buttons, game_state)

def new_game(screen, game_state, players):
    end_game = UITextElement(center_position=(480, 50), 
                          font_size=30, 
                          bg_rgb=BG_BLUE, 
                          text_rgb=WHITE, 
                          text="END GAME",
                          action = "END")

    amount = len(players[0].hand)
    p1_amount = UITextElement(center_position=(120, 450),
                              font_size=15,
                              amount = amount,
                              bg_rgb=BLUE,
                              text_rgb=WHITE,
                              text=f"P1 Amount:{amount}",
                              clickable=False)
    p1_amount.player = 1
    
    p2_amount = UITextElement(center_position=(480, 150),
                                  font_size=15,
                                  amount=amount,
                                  bg_rgb=BLUE,
                                  text_rgb=WHITE,
                                  text=f"P2 Amount:{amount}",
                                  clickable=False)
    p2_amount.player = 2

    p1_hand_display = []
    p2_hand_display = []

    for i in range(len(players[0].hand)): #len(players[0].hand)
        card = UISpriteElement(center_position=(300, 450),
                            file="cards/back_dark.png",
                            size=0.3,
                            angle=random.randint(-3, 3),
                            clickable=True if i >= (len(players[0].hand)) - 1 else False,
                            action="DRAW",
                            is_animated=True,
                            animation_instructions=P1_ANIMS,
                            front_card=players[0].hand[i].return_path(),
                            rank = players[0].hand[i].access_rank(),
                            belongs_to=1
                            )
        card.card_index = i
        card.hand = 1
        card.hand_cards = players[0].hand
        card.card = players[0].hand[i]
        p1_hand_display.append(card)
        card.display_hands = p1_hand_display
    #p1_hand_display.hand = 1
        
    for i in range(len(players[1].hand)): #len(players[1].hand)
        card = UISpriteElement(center_position=(300, 150),
                            file="cards/back_dark.png",
                            size=0.3,
                            angle=random.randint(-3, 3),
                            clickable=False,
                            action="DRAW",
                            is_animated=True,
                            animation_instructions=P2_ANIMS,
                            front_card=players[1].hand[i].return_path(),
                            rank = players[1].hand[i].access_rank(),
                            belongs_to=2
                            )
        card.card_index = i
        card.hand = 2
        card.hand_cards = players[1].hand
        card.card = players[1].hand[i]
        p2_hand_display.append(card)
        card.display_hands = p2_hand_display
        
    #p2_hand_display.hand = 2

    p1_hand_holding = []
    p2_hand_holding = []

    buttons = pygame.sprite.LayeredUpdates()
    buttons.add(end_game, p1_amount, p2_amount)
    buttons.add(*p1_hand_display, layer=1)
    buttons.add(*p2_hand_display, layer=1)
    return game_loop(screen, buttons, game_state, player_holding = [p1_hand_holding, p2_hand_holding], hands_lst = [p1_hand_display, p2_hand_display])

def player_1_wins(screen, game_state):
    back_to_menu = UITextElement(center_position=(450, 50), 
                              font_size=30, 
                              bg_rgb=BG_RED, 
                              text_rgb=WHITE, 
                              text="BACK TO MENU",
                              action = GameState.TITLE)

    win_image = UISpriteElement(center_position=(300, 300),
                                   file="assets/you_won.jpg",
                                   size = 0.6,
                                   clickable=False
                                   )

    buttons = RenderUpdates(back_to_menu, win_image)
    
    return game_loop(screen, buttons, game_state)

def player_2_wins(screen, game_state):
    back_to_menu = UITextElement(center_position=(450, 50), 
                              font_size=30, 
                              bg_rgb=BG_BLUE, 
                              text_rgb=WHITE, 
                              text="BACK TO MENU",
                              action = GameState.TITLE)

    lose_image = UISpriteElement(center_position=(300, 300),
                                       file="assets/you_lost.jpg",
                                       size = 0.6,
                                       clickable=False
                                       )

    buttons = RenderUpdates(back_to_menu, lose_image)
    
    return game_loop(screen, buttons, game_state)

def tied(screen, game_state):
    back_to_menu = UITextElement(center_position=(450, 50), 
                              font_size=30, 
                              bg_rgb=BG_GREEN, 
                              text_rgb=WHITE, 
                              text="BACK TO MENU",
                              action = GameState.TITLE)

    tie_image = UISpriteElement(center_position=(300, 300),
                                       file="assets/tie.jpg",
                                       size = 0.6,
                                       clickable=False
                                       )

    buttons = RenderUpdates(back_to_menu, tie_image)
    
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
        
        if game_state == GameState.HOW_TO:
            game_state = how_to(screen, game_state)
        
        if game_state == GameState.NEWGAME:
            x = deck.Game_Deck()
            x.generateDeck()
            x.shuffle()
            p1 = deck.Player(hand=x.pop_from_deck(26))
            p2 = deck.Player(hand=x.pop_from_deck(26))
            game_state = new_game(screen, game_state, players = [p1, p2])

        if game_state == GameState.P1_WINS:
            game_state = player_1_wins(screen, game_state)

        if game_state == GameState.P2_WINS:
            game_state = player_2_wins(screen, game_state)

        if game_state == GameState.TIED:
            game_state = tied(screen, game_state)

        if game_state == GameState.QUIT:
            pygame.quit()
            running = False

if __name__ == '__main__':
    main()
