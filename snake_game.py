import pygame
import sys
import random
import time
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any
from enum import Enum

# set up pygame stuff
pygame.init()

# color definitions
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 120, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
ENEMY_COLOR = (255, 0, 128)  # Pink color for enemies

# no sounds yet

# different food types
class FoodType(Enum):
    REGULAR = 1
    BONUS = 2
    SUPER = 3  # Super food can remove one enemy

@dataclass
class Position:
    x: int
    y: int
    
    def __eq__(self, other):
        if not isinstance(other, Position):
            return False
        return self.x == other.x and self.y == other.y
        
    def distance_to(self, other):
        return abs(self.x - other.x) + abs(self.y - other.y)  # rough distance measure

class Enemy:
    def __init__(self, pos: Position, grid_width: int, grid_height: int, walls: List):
        self.position = pos
        self.color = ENEMY_COLOR
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.walls = walls
        self.move_cooldown = 0
        self.move_delay = 2  # Moves every N game ticks (higher = slower)
        
    def get_valid_moves(self, snake_body):
        # check possible directions
        possible_moves = [
            Position(self.position.x, self.position.y - 1),  # Up
            Position(self.position.x, self.position.y + 1),  # Down
            Position(self.position.x - 1, self.position.y),  # Left
            Position(self.position.x + 1, self.position.y)   # Right
        ]
        
        # remove bad options
        valid_moves = []
        for move in possible_moves:
            # Check if move is within grid boundaries
            if move.x < 0 or move.x >= self.grid_width or move.y < 0 or move.y >= self.grid_height:
                continue
                
            # Check if move collides with walls
            if any(w[0] == move.x and w[1] == move.y for w in self.walls):
                continue
                
            # Check if move collides with snake body (except head which we want to chase)
            if any(b.x == move.x and b.y == move.y for b in snake_body[1:]):
                continue
                
            # Check if move collides with other enemies (not implemented yet)
            # todo: handle other enemies
                
            valid_moves.append(move)
            
        return valid_moves
    
    def move_towards_snake(self, snake_head: Position, snake_body: List[Position]):
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
            return
            
        valid_moves = self.get_valid_moves(snake_body)
        if not valid_moves:
            # No valid moves, stay in place
            self.move_cooldown = self.move_delay
            return
            
        # find distance to snake
        dx = snake_head.x - self.position.x
        dy = snake_head.y - self.position.y
        
        # Prioritize the direction with larger distance
        horizontal_priority = abs(dx) > abs(dy)
        
        # Sort moves based on getting closer to snake with directional priority
        def move_score(move):
            move_dx = move.x - self.position.x
            move_dy = move.y - self.position.y
            
            # check if moving closer
            helps_horizontal = (dx > 0 and move_dx > 0) or (dx < 0 and move_dx < 0)
            helps_vertical = (dy > 0 and move_dy > 0) or (dy < 0 and move_dy < 0)
            
            # Score the move based on priority
            if horizontal_priority:
                return (-2 if helps_horizontal else 2) + (-1 if helps_vertical else 1)
            else:
                return (-2 if helps_vertical else 2) + (-1 if helps_horizontal else 1)
        
        # Choose the best move based on our scoring system
        best_move = min(valid_moves, key=move_score)
        self.position = best_move
        self.move_cooldown = self.move_delay

class Snake:
    def __init__(self, start_pos: Position):
        # Start with two segments - head and one body segment
        self.body = [start_pos, Position(start_pos.x - 1, start_pos.y)]
        self.direction = 'RIGHT'
        self.growth_pending = False
        self.head_color = WHITE  # Head is white
        self.body_color = BLACK  # Body is black

    def move(self):
        head = self.body[0]
        new_head = Position(head.x, head.y)

        if self.direction == 'UP':
            new_head.y -= 1
        elif self.direction == 'DOWN':
            new_head.y += 1
        elif self.direction == 'LEFT':
            new_head.x -= 1
        elif self.direction == 'RIGHT':
            new_head.x += 1

        self.body.insert(0, new_head)
        if not self.growth_pending:
            self.body.pop()
        else:
            self.growth_pending = False

    def grow(self):
        self.growth_pending = True

class Game:
    DIFFICULTY_SPEEDS = {
        'EASY': 7,  # easier mode speed
        'MEDIUM': 15,
        'HARD': 20
    }

    MAP_LAYOUTS = {
        'BASIC': [],
        'MAZE': [
            # border walls
            *[(i, 5) for i in range(5, 35)],  # top barrier
            *[(i, 25) for i in range(5, 35)],  # bottom barrier
            *[(5, i) for i in range(5, 26)],  # left side
            *[(35, i) for i in range(5, 26)],  # right side
            
            # maze guts
            *[(10, i) for i in range(5, 20)],  # Vertical wall 1
            *[(15, i) for i in range(10, 26)],  # Vertical wall 2
            *[(20, i) for i in range(5, 20)],  # Vertical wall 3
            *[(25, i) for i in range(10, 26)],  # Vertical wall 4
            *[(30, i) for i in range(5, 20)],  # Vertical wall 5
            
            # Horizontal connectors
            *[(i, 10) for i in range(5, 35, 5)],  # Horizontal wall 1
            *[(i, 15) for i in range(5, 35, 5)],  # Horizontal wall 2
            *[(i, 20) for i in range(5, 35, 5)]   # Horizontal wall 3
        ]
    }

    def __init__(self, width=800, height=600):
        # screen setup
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Snake Game')
        
        # game config
        self.cell_size = 20
        self.grid_width = width // self.cell_size
        self.grid_height = height // self.cell_size
        self.score = 0
        self.high_score = self.load_high_score()
        self.difficulty = 'EASY'
        self.map_style = 'BASIC'
        self.walls = self.MAP_LAYOUTS[self.map_style]
        
        # enemy setup
        self.enemies = []
        self.enemy_count = 0
        self.spawn_enemies = False
        
        self.snake = Snake(Position(self.grid_width // 2, self.grid_height // 2))
        self.food = self.generate_food()
        self.game_over = False
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 25)
        self.last_update_time = pygame.time.get_ticks()
        self.food_flash_interval = 500  # milliseconds between food flashing for special foods

    def load_high_score(self) -> int:
        try:
            with open('snake_highscore.txt', 'r') as f:
                return int(f.read())
        except:
            return 0

    def save_high_score(self):
        with open('snake_highscore.txt', 'w') as f:
            f.write(str(self.high_score))

    def generate_food(self) -> Dict[str, Any]:
        while True:
            food_pos = Position(
                random.randint(0, self.grid_width - 1),
                random.randint(0, self.grid_height - 1)
            )
            # Make sure food doesn't spawn on snake, walls, or enemies
            if not any(b.x == food_pos.x and b.y == food_pos.y for b in self.snake.body) and \
               not any(w[0] == food_pos.x and w[1] == food_pos.y for w in self.walls) and \
               not any(e.position.x == food_pos.x and e.position.y == food_pos.y for e in self.enemies):
                # Determine food type based on probability
                food_type_roll = random.random()
                if food_type_roll < 0.05:  # 5% chance for super food
                    food_type = FoodType.SUPER
                    food_color = PURPLE
                    food_value = 30
                elif food_type_roll < 0.20:  # 15% chance for bonus food
                    food_type = FoodType.BONUS
                    food_color = ORANGE
                    food_value = 20
                else:  # 80% chance for regular food
                    food_type = FoodType.REGULAR
                    food_color = GREEN
                    food_value = 10
                    
                return {
                    "position": food_pos,
                    "type": food_type,
                    "color": food_color,
                    "value": food_value,
                    "spawn_time": pygame.time.get_ticks(),
                    "flash_state": False
                }

    def check_collision(self) -> bool:
        head = self.snake.body[0]
        
        # Wall collision - fixed to use grid dimensions
        if head.x < 0 or head.x >= self.grid_width or head.y < 0 or head.y >= self.grid_height:
            return True
            
        # Self collision - only check body parts after the head
        if len(self.snake.body) > 1 and any(b.x == head.x and b.y == head.y for b in self.snake.body[1:]):
            return True
            
        # Map obstacles collision
        if any(w[0] == head.x and w[1] == head.y for w in self.walls):
            return True
            
        return False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and self.snake.direction != 'DOWN':
                    self.snake.direction = 'UP'
                elif event.key == pygame.K_DOWN and self.snake.direction != 'UP':
                    self.snake.direction = 'DOWN'
                elif event.key == pygame.K_LEFT and self.snake.direction != 'RIGHT':
                    self.snake.direction = 'LEFT'
                elif event.key == pygame.K_RIGHT and self.snake.direction != 'LEFT':
                    self.snake.direction = 'RIGHT'

    def update(self):
        self.snake.move()

        if self.check_collision():
            self.game_over = True
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
            return

        # Check for food collision
        head = self.snake.body[0]
        food_pos = self.food["position"]
        if head.x == food_pos.x and head.y == food_pos.y:
            # Add score based on food type
            self.score += self.food["value"]
            
            # Grow the snake
            self.snake.grow()
            
            # Generate new food
            self.food = self.generate_food()
        
        # Update food flashing for special foods
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update_time > self.food_flash_interval:
            if self.food["type"] != FoodType.REGULAR:
                self.food["flash_state"] = not self.food["flash_state"]
            self.last_update_time = current_time
            
        # Update enemies if they are spawned
        if self.spawn_enemies:
            for enemy in self.enemies:
                enemy.move_towards_snake(self.snake.body[0], self.snake.body)
                
            # Check if snake collides with any enemy
            for enemy in self.enemies:
                if head.x == enemy.position.x and head.y == enemy.position.y:
                    self.game_over = True
                    if self.score > self.high_score:
                        self.high_score = self.score
                        self.save_high_score()
                    return

    def draw(self):
        # Clear screen
        self.screen.fill(BLUE)
        
        # Draw score
        score_text = self.font.render(f'Score: {self.score} | High Score: {self.high_score}', True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Draw walls
        for wall in self.walls:
            pygame.draw.rect(self.screen, WHITE, 
                            (wall[0] * self.cell_size, wall[1] * self.cell_size, 
                             self.cell_size, self.cell_size))
        
        # Draw enemies if they are spawned
        if self.spawn_enemies:
            for enemy in self.enemies:
                pygame.draw.rect(self.screen, enemy.color,
                               (enemy.position.x * self.cell_size, enemy.position.y * self.cell_size,
                                self.cell_size, self.cell_size))
        
        # Draw snake body segments
        for segment in self.snake.body[1:]:
            pygame.draw.rect(self.screen, self.snake.body_color,
                            (segment.x * self.cell_size, segment.y * self.cell_size,
                             self.cell_size, self.cell_size))
        
        # Draw snake head (white)
        head = self.snake.body[0]
        pygame.draw.rect(self.screen, self.snake.head_color,
                        (head.x * self.cell_size, head.y * self.cell_size,
                         self.cell_size, self.cell_size))
        
        # Draw eyes on the snake head to make it more appealing
        eye_size = self.cell_size // 5
        eye_offset = self.cell_size // 4
        
        # eye placement
        if self.snake.direction == 'RIGHT':
            left_eye = (head.x * self.cell_size + self.cell_size - eye_offset, head.y * self.cell_size + eye_offset)
            right_eye = (head.x * self.cell_size + self.cell_size - eye_offset, head.y * self.cell_size + self.cell_size - eye_offset)
        elif self.snake.direction == 'LEFT':
            left_eye = (head.x * self.cell_size + eye_offset, head.y * self.cell_size + eye_offset)
            right_eye = (head.x * self.cell_size + eye_offset, head.y * self.cell_size + self.cell_size - eye_offset)
        elif self.snake.direction == 'UP':
            left_eye = (head.x * self.cell_size + eye_offset, head.y * self.cell_size + eye_offset)
            right_eye = (head.x * self.cell_size + self.cell_size - eye_offset, head.y * self.cell_size + eye_offset)
        else:  # DOWN
            left_eye = (head.x * self.cell_size + eye_offset, head.y * self.cell_size + self.cell_size - eye_offset)
            right_eye = (head.x * self.cell_size + self.cell_size - eye_offset, head.y * self.cell_size + self.cell_size - eye_offset)
        
        pygame.draw.circle(self.screen, BLACK, left_eye, eye_size)
        pygame.draw.circle(self.screen, BLACK, right_eye, eye_size)
        
        # Draw food with appropriate color and flashing effect for special foods
        food_pos = self.food["position"]
        food_color = self.food["color"]
        
        # Make special foods flash
        if self.food["type"] != FoodType.REGULAR and self.food["flash_state"]:
            food_color = YELLOW
        
        pygame.draw.rect(self.screen, food_color,
                        (food_pos.x * self.cell_size, food_pos.y * self.cell_size,
                         self.cell_size, self.cell_size))
        
        # mark special foods
        if self.food["type"] == FoodType.BONUS:
            pygame.draw.circle(self.screen, WHITE, 
                             (food_pos.x * self.cell_size + self.cell_size // 2, 
                              food_pos.y * self.cell_size + self.cell_size // 2), 
                             self.cell_size // 4)
        elif self.food["type"] == FoodType.SUPER:
            pygame.draw.polygon(self.screen, WHITE, [
                (food_pos.x * self.cell_size + self.cell_size // 2, food_pos.y * self.cell_size + 2),
                (food_pos.x * self.cell_size + 2, food_pos.y * self.cell_size + self.cell_size - 2),
                (food_pos.x * self.cell_size + self.cell_size - 2, food_pos.y * self.cell_size + self.cell_size - 2)
            ])
        
        pygame.display.update()

    def show_game_over(self):
        self.screen.fill(BLUE)
        game_over_text = self.font.render(f'Game Over! Final Score: {self.score}', True, WHITE)
        restart_text = self.font.render('Press SPACE to restart or ESC to quit', True, WHITE)
        
        # Draw a red border to indicate game over
        border_width = 10
        pygame.draw.rect(self.screen, RED, (border_width, border_width, 
                                          self.width - 2*border_width, 
                                          self.height - 2*border_width), border_width)
        
        self.screen.blit(game_over_text, (self.width // 2 - game_over_text.get_width() // 2, 
                                         self.height // 2 - 50))
        self.screen.blit(restart_text, (self.width // 2 - restart_text.get_width() // 2, 
                                      self.height // 2))
        
        # Draw the final snake
        for i, segment in enumerate(self.snake.body):
            color = WHITE if i == 0 else BLACK
            pygame.draw.rect(self.screen, color,
                           (self.width // 2 - 100 + i * self.cell_size, 
                            self.height // 2 + 50,
                            self.cell_size, self.cell_size))
        
        pygame.display.update()
        
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        waiting = False
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

    def run(self):
        # set up baddies if enabled
        if self.spawn_enemies and self.enemy_count > 0:
            self.enemies = []
            for _ in range(self.enemy_count):
                # Generate a random position for the enemy that doesn't collide with anything
                while True:
                    pos = Position(
                        random.randint(0, self.grid_width - 1),
                        random.randint(0, self.grid_height - 1)
                    )
                    # Make sure enemy doesn't spawn on snake, walls, or other enemies
                    if not any(b.x == pos.x and b.y == pos.y for b in self.snake.body) and \
                       not any(w[0] == pos.x and w[1] == pos.y for w in self.walls) and \
                       not any(e.position.x == pos.x and e.position.y == pos.y for e in self.enemies) and \
                       not (self.food["position"].x == pos.x and self.food["position"].y == pos.y):
                        self.enemies.append(Enemy(pos, self.grid_width, self.grid_height, self.walls))
                        break
        
        while not self.game_over:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(Game.DIFFICULTY_SPEEDS[self.difficulty])
        
        self.show_game_over()
        return self.score

class Menu:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Snake Game')
        self.font_large = pygame.font.SysFont('Arial', 40)
        self.font = pygame.font.SysFont('Arial', 30)
        self.clock = pygame.time.Clock()
        self.difficulty = 'EASY'
        self.map_style = 'BASIC'
        self.spawn_enemies = False
        self.enemy_count = 0
    
    def draw_button(self, text, rect, selected=False):
        # button colors
        color = WHITE if selected else BLACK
        bg_color = BLACK if selected else WHITE
        pygame.draw.rect(self.screen, bg_color, rect)
        pygame.draw.rect(self.screen, color, rect, 2)
        text_surf = self.font.render(text, True, color)
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)
        return rect
    
    def show(self):
        running = True
        selected_option = 0
        options = ['Start Game', 
                  f'Difficulty: {self.difficulty}', 
                  f'Map: {self.map_style}', 
                  f'Spawn Enemies: {"ON" if self.spawn_enemies else "OFF"}',
                  f'Enemy Count: {self.enemy_count}',
                  'Exit']
        
        while running:
            self.screen.fill(BLUE)
            
            # Draw title
            title = self.font_large.render('SNAKE GAME', True, WHITE)
            self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 50))
            
            # Draw menu options
            button_height = 60
            button_width = 300
            button_margin = 20
            start_y = 150
            
            buttons = []
            for i, option in enumerate(options):
                rect = pygame.Rect((self.width - button_width) // 2, 
                                  start_y + i * (button_height + button_margin),
                                  button_width, button_height)
                buttons.append(self.draw_button(option, rect, i == selected_option))
            
            pygame.display.update()
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % len(options)
                    elif event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        if selected_option == 0:  # Start Game
                            game = Game(self.width, self.height)
                            game.difficulty = self.difficulty
                            game.map_style = self.map_style
                            game.walls = Game.MAP_LAYOUTS[self.map_style]
                            game.spawn_enemies = self.spawn_enemies
                            game.enemy_count = self.enemy_count
                            game.run()
                            # After game over, continue the menu loop
                            # Reset pygame display to ensure we return to menu properly
                            self.screen = pygame.display.set_mode((self.width, self.height))
                            pygame.display.set_caption('Snake Game')
                        elif selected_option == 1:  # Change Difficulty
                            difficulties = list(Game.DIFFICULTY_SPEEDS.keys())
                            current_index = difficulties.index(self.difficulty)
                            self.difficulty = difficulties[(current_index + 1) % len(difficulties)]
                            options[1] = f'Difficulty: {self.difficulty}'
                        elif selected_option == 2:  # Change Map
                            maps = list(Game.MAP_LAYOUTS.keys())
                            current_index = maps.index(self.map_style)
                            self.map_style = maps[(current_index + 1) % len(maps)]
                            options[2] = f'Map: {self.map_style}'
                        elif selected_option == 3:  # Toggle Spawn Enemies
                            self.spawn_enemies = not self.spawn_enemies
                            options[3] = f'Spawn Enemies: {"ON" if self.spawn_enemies else "OFF"}'
                        elif selected_option == 4:  # Change Enemy Count
                            if self.spawn_enemies:
                                # Cycle through 1-5 enemies
                                self.enemy_count = (self.enemy_count % 5) + 1
                                options[4] = f'Enemy Count: {self.enemy_count}'
                        elif selected_option == 5:  # Exit
                            running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    for i, rect in enumerate(buttons):
                        if rect.collidepoint(pos):
                            selected_option = i
                            # Simulate Enter key press
                            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_RETURN}))
            
            self.clock.tick(30)

def main():
    pygame.init()
    menu = Menu()
    menu.show()
    pygame.quit()

if __name__ == "__main__":
    main()