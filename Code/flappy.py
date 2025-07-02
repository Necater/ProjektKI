import math
import pygame, random, time
from pygame.locals import *

# Statische Dummy-Surface für Headless-Modus
_DUMMY_SURFACE = pygame.Surface((1, 1))

SCREEN_WIDHT = 400
SCREEN_HEIGHT = 600
SPEED = 20
GRAVITY = 2.5
GAME_SPEED = 15

GROUND_WIDHT = 2 * SCREEN_WIDHT
GROUND_HEIGHT = 100

PIPE_WIDHT = 80
PIPE_HEIGHT = 500
PIPE_GAP = 150


class Bird(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.images = [
            pygame.image.load('assets/sprites/bluebird-upflap.png').convert_alpha(),
            pygame.image.load('assets/sprites/bluebird-midflap.png').convert_alpha(),
            pygame.image.load('assets/sprites/bluebird-downflap.png').convert_alpha()
        ]
        self.speed = SPEED
        self.current_image = 0
        self.image = pygame.image.load('assets/sprites/bluebird-upflap.png').convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect[0] = SCREEN_WIDHT / 6
        self.rect[1] = SCREEN_HEIGHT / 2

    def update(self):
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[self.current_image]
        self.speed += GRAVITY
        self.rect[1] += self.speed

    def bump(self):
        self.speed = -SPEED

    def begin(self):
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[self.current_image]


class Pipe(pygame.sprite.Sprite):
    def __init__(self, inverted, xpos, ysize):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/sprites/pipe-green.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (PIPE_WIDHT, PIPE_HEIGHT))
        self.rect = self.image.get_rect()
        self.rect[0] = xpos

        if inverted:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect[1] = -(self.rect[3] - ysize)
        else:
            self.rect[1] = SCREEN_HEIGHT - ysize

        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect[0] -= GAME_SPEED


class Ground(pygame.sprite.Sprite):
    def __init__(self, xpos):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/sprites/base.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (GROUND_WIDHT, GROUND_HEIGHT))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect[0] = xpos
        self.rect[1] = SCREEN_HEIGHT - GROUND_HEIGHT

    def update(self):
        self.rect[0] -= GAME_SPEED


def is_off_screen(sprite):
    return sprite.rect[0] < -sprite.rect[2]


def get_random_pipes(xpos):
    size = random.randint(100, 300)
    pipe = Pipe(False, xpos, size)
    pipe_inverted = Pipe(True, xpos, SCREEN_HEIGHT - size - PIPE_GAP)
    return pipe, pipe_inverted


class FlappyGame:
    def __init__(self, render=True):
        self.render = render
        pygame.init()

        # [OPTIMIERUNG] Minimales 1×1-Fenster ohne Rahmen, wenn render=False
        if self.render:
            self.screen = pygame.display.set_mode((SCREEN_WIDHT, SCREEN_HEIGHT))
        else:
            self.screen = pygame.display.set_mode((1, 1), pygame.NOFRAME)

        # [OPTIMIERUNG] Dummy-Hintergrund bei render=False
        if self.render:
            self.BACKGROUND = pygame.image.load('assets/sprites/background-day.png')
            self.BACKGROUND = pygame.transform.scale(self.BACKGROUND, (SCREEN_WIDHT, SCREEN_HEIGHT))
        else:
            self.BACKGROUND = pygame.Surface((1, 1))

        self.bird_group = pygame.sprite.Group()
        self.ground_group = pygame.sprite.Group()
        self.pipe_group = pygame.sprite.Group()
        self.clock = pygame.time.Clock()
        
        self.passed_pipes = [] #speichert die pipes, die der vogel bereits durchquert hat
        self.num_passed_pipes = 0 #speichert die anzahl der pipes, die der vogel bereits durchquert hat

        self.reset()

    def reset(self):
        # Bird initialisieren
        if self.render:
            self.bird = Bird()
        else:
            # [OPTIMIERUNG] Dummy-Bird
            self.bird = pygame.sprite.Sprite()
            self.bird.image = _DUMMY_SURFACE
            self.bird.rect = self.bird.image.get_rect()
            self.bird.rect[0] = SCREEN_WIDHT / 6
            self.bird.rect[1] = SCREEN_HEIGHT / 2
            self.bird.speed = SPEED
            self.bird.bump = lambda: setattr(self.bird, 'speed', -SPEED)
            self.bird.update = lambda: (setattr(self.bird, 'speed', self.bird.speed + GRAVITY),
                                        setattr(self.bird.rect, 'y', self.bird.rect.y + self.bird.speed))

        self.bird_group.empty()
        self.bird_group.add(self.bird)

        # Ground initialisieren
        self.ground_group.empty()
        for i in range(2):
            if self.render:
                ground = Ground(GROUND_WIDHT * i)
            else:
                ground = pygame.sprite.Sprite()
                ground.image = _DUMMY_SURFACE
                ground.rect = ground.image.get_rect()
                ground.rect[0] = GROUND_WIDHT * i
                ground.rect[1] = SCREEN_HEIGHT - GROUND_HEIGHT
                ground.update = lambda g=ground: setattr(g.rect, 'x', g.rect.x - GAME_SPEED)
            self.ground_group.add(ground)

        # Pipes initialisieren
        self.pipe_group.empty()
        for i in range(2):
            if self.render:
                pipes = get_random_pipes(SCREEN_WIDHT * i + 800)
                self.pipe_group.add(pipes[0])
                self.pipe_group.add(pipes[1])
            else:
                for _ in range(2):
                    dummy_pipe = pygame.sprite.Sprite()
                    dummy_pipe.image = _DUMMY_SURFACE
                    dummy_pipe.rect = dummy_pipe.image.get_rect()
                    dummy_pipe.rect.x = SCREEN_WIDHT * i + 800
                    dummy_pipe.rect.y = random.randint(100, 300)
                    dummy_pipe.update = lambda p=dummy_pipe: setattr(p.rect, 'x', p.rect.x - GAME_SPEED)
                    self.pipe_group.add(dummy_pipe)

        self.done = False
        self.start_time = time.time()

        self.passed_pipes = []
        self.num_passed_pipes = 0

        return self.get_state()

    def get_state(self):
        bird_y_position = self.bird.rect.y
        pipes_sorted = sorted(self.pipe_group, key=lambda p: p.rect.x)
        next_pipes = []
        if pipes_sorted[0].rect.x + PIPE_WIDHT > self.bird.rect.x:
            next_pipes = pipes_sorted[:2]
        elif len(pipes_sorted) >= 4 and pipes_sorted[2].rect.x + PIPE_WIDHT > self.bird.rect.x:
            next_pipes = pipes_sorted[2:4]

        if not next_pipes:
            return [bird_y_position, SCREEN_WIDHT, 0, SCREEN_HEIGHT]
        top_pipe_y = next_pipes[1].rect.bottom
        bot_pipe_y = next_pipes[0].rect.top
        return [bird_y_position, next_pipes[0].rect.x, top_pipe_y, bot_pipe_y]
    
    # --- Reward-Methoden ---

    # Reward fürs Überleben
    def reward_exist(self):
        return 0.1
    
    # Reward für die Anzahl der durchquerten Pipes, höhere Anzahl = höherer Reward
    def reward_pipes_strike(self):
        return self.num_passed_pipes
    
    # Reward sofort nach dem Durchqueren einer Pipe
    def reward_for_passing_pipes(self):
        reward = 0
        for pipe in self.pipe_group:
            if pipe.rect.right < self.bird.rect.left and pipe not in self.passed_pipes:
                self.passed_pipes.append(pipe)
                self.num_passed_pipes += 1
                reward += 2
                reward += self.reward_pipes_strike()  # Reward für das gestaffelte Durchqueren der Pipes
        return reward
    
    # Höherer Reward, wenn Vogel sich der Mitte der nächsten beiden Pipes nähert
    def reward_for_centering_between_pipes(self):
        pipes = self.pipe_group.sprites()  # Länge 4
        upper_next_pipe = pipes[0]
        lower_next_pipe = pipes[1]

        # Mittelpunkt zweier Pipes
        center_next_pipe_x = (upper_next_pipe.rect.left + upper_next_pipe.rect.right) / 2
        center_next_pipe_y = (upper_next_pipe.rect.top + lower_next_pipe.rect.bottom) / 2

        # Distanz Vogel und Mittelpunkt zweier Pipes
        # Euklidische Distanz
        distance = math.sqrt((self.bird.rect.centerx - center_next_pipe_x) ** 2 + (self.bird.rect.centery - center_next_pipe_y) ** 2)

        return 100 / (distance + 1)  # Je näher der Vogel an der Mitte der Pipe ist, desto höher der Reward
    
    # Reward, wenn sich der Vogel mittig im Bildschirm befindet und falls er zu sehr am Rand ist, gibt es eine Strafe
    def reward_for_vertical_position(self):
        if 100 < self.bird.rect.centery < 400:
            return 0.5
        else:
            return -1
        
     # Strafe nach dem Überschreiten der Mitte der Pipes erster Ansatz
    def penalty_for_passing_pipe_middle_first_approach(self):
        pipes = self.pipe_group.sprites()
        upper_next_pipe = pipes[0]
        lower_next_pipe = pipes[1]

        middle_pipe_x = abs(self.bird.rect.centerx - upper_next_pipe.rect.centerx)

        passed_upper_middle = self.bird.rect.centery >= upper_next_pipe.rect.centery - 100  # Problem hierbei: Es wird nicht richtig die Mitte der Pipe betrachtet
        passed_lower_middle = self.bird.rect.centery <= lower_next_pipe.rect.centery + 100  # Wahrscheinlich liegt es daran, dass die Mitte der Sprite des Pipes betrachtet wird

        if passed_upper_middle or passed_lower_middle:
            return -(3 + (150 / (middle_pipe_x + 1)))  # Wenn Vogel sich dabei der X Position der Pipe nähert, erhöht sich diese Strafe
        else:
            return 0

    # Strafe nach dem Überschreiten der Mitte der Pipes zweiter Ansatz
    def penalty_for_passing_pipe_middle(self):
        pipes = self.pipe_group.sprites()
        upper_next_pipe = pipes[0]
        lower_next_pipe = pipes[1]

        middle_pipe_x = abs(self.bird.rect.centerx - upper_next_pipe.rect.centerx)

        # Zweiter Ansatz (die Mitte einer Pipe wird nun anhand des Mittelpunktes beider Pipes betrachtet)
        center_next_pipe_y = (upper_next_pipe.rect.top + lower_next_pipe.rect.bottom) / 2

        passed_upper_middle_2 = self.bird.rect.centery >= (center_next_pipe_y + 150)
        passed_lower_middle_2 = self.bird.rect.centery <= (center_next_pipe_y - 150)

        if passed_upper_middle_2 or passed_lower_middle_2:
            return -(3 + (150 / (middle_pipe_x + 1)))  # Wenn Vogel sich dabei der X Position der Pipe nähert, erhöht sich diese Strafe
        else:
            return 0
        
    # Gesamt-Reward-Berechnung
    def calculate_reward(self):
        reward = 0 # Initialisierung des Rewards

        reward += self.reward_exist()
        reward += self.reward_for_passing_pipes()
        reward += self.reward_for_centering_between_pipes()
        reward += self.reward_for_vertical_position()
        reward += self.penalty_for_passing_pipe_middle()

        return reward
        
    # --- Reward-Methoden Ende ---

    def step(self, action):
        if action == 1:
            self.bird.bump()

        self.bird_group.update()
        self.ground_group.update()
        self.pipe_group.update()

        # Ground recyclen
        if is_off_screen(self.ground_group.sprites()[0]):
            self.ground_group.remove(self.ground_group.sprites()[0])
            if self.render:
                new_ground = Ground(GROUND_WIDHT - 20)
            else:
                new_ground = pygame.sprite.Sprite()
                new_ground.image = pygame.Surface((1, 1))
                new_ground.rect = new_ground.image.get_rect()
                new_ground.rect[0] = GROUND_WIDHT - 20
                new_ground.rect[1] = SCREEN_HEIGHT - GROUND_HEIGHT
                new_ground.update = lambda g=new_ground: setattr(g.rect, 'x', g.rect.x - GAME_SPEED)
            self.ground_group.add(new_ground)

        # Pipes recyclen
        if is_off_screen(self.pipe_group.sprites()[0]):
            self.pipe_group.remove(self.pipe_group.sprites()[0])
            self.pipe_group.remove(self.pipe_group.sprites()[0])
            if self.render:
                pipes = get_random_pipes(SCREEN_WIDHT * 2)
                self.pipe_group.add(pipes[0])
                self.pipe_group.add(pipes[1])
            else:
                for _ in range(2):
                    dummy_pipe = pygame.sprite.Sprite()
                    dummy_pipe.image = pygame.Surface((1, 1))
                    dummy_pipe.rect = dummy_pipe.image.get_rect()
                    dummy_pipe.rect.x = SCREEN_WIDHT * 2
                    dummy_pipe.rect.y = random.randint(100, 300)
                    dummy_pipe.update = lambda p=dummy_pipe: setattr(p.rect, 'x', p.rect.x - GAME_SPEED)
                    self.pipe_group.add(dummy_pipe)

        # Reward
        reward = self.calculate_reward()

        # Kollision im Render-Modus
        if self.render and (pygame.sprite.groupcollide(self.bird_group, self.ground_group, False, False, pygame.sprite.collide_mask) or
            pygame.sprite.groupcollide(self.bird_group, self.pipe_group, False, False, pygame.sprite.collide_mask)):
            self.done = True
            reward = -10

        # Kollision im nicht Render-Modus
        if (pygame.sprite.groupcollide(self.bird_group, self.ground_group, False, False, pygame.sprite.collide_mask) or
            pygame.sprite.groupcollide(self.bird_group, self.pipe_group, False, False, pygame.sprite.collide_mask)):
            self.done = True
            reward = -10  #wenn vogel mit boden oder pipe collidiert, strafe

        #Spiel abbrechen wenn Vogel oben aus dem Bild rausfliegt
        if (self.bird.rect.y <= 0):
            self.done = True
            reward = -10

        #wenn vogel aus dem spiel rausfliegt strafe und game beenden
        if (is_off_screen(self.bird_group.sprites()[0])):
            self.done = True
            reward = -10 

        # [OPTIMIERUNG] Rendering nur bei render=True
        if self.render:
            self.screen.blit(self.BACKGROUND, (0, 0))
            self.bird_group.draw(self.screen)
            self.pipe_group.draw(self.screen)
            self.ground_group.draw(self.screen)
            pygame.display.update()

        # [OPTIMIERUNG] nur im Render-Modus warten
        if self.render:
            self.clock.tick(15)
        return self.get_state(), reward, self.done
    
'''
def play():
    game = FlappyGame()
    state = game.reset()
    done = False
    gesamtReward = 0
    while not done:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_SPACE or event.key == K_UP:
                    state, reward, done = game.step(1)
                    gesamtReward += reward
                    continue
    

        state, reward, done = game.step(0)
        gesamtReward += reward
        #print(gesamtReward)
        print(reward)
    pygame.quit()
         
play()
'''