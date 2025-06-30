import math
import pygame, random, time
from pygame.locals import *

SCREEN_WIDHT = 400
SCREEN_HEIGHT = 600
SPEED = 20
GRAVITY = 2.5
GAME_SPEED = 15
 
GROUND_WIDHT = 2 * SCREEN_WIDHT
GROUND_HEIGHT= 100

PIPE_WIDHT = 80
PIPE_HEIGHT = 500

PIPE_GAP = 150


class Bird(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.images =  [pygame.image.load('assets/sprites/bluebird-upflap.png').convert_alpha(),
                        pygame.image.load('assets/sprites/bluebird-midflap.png').convert_alpha(),
                        pygame.image.load('assets/sprites/bluebird-downflap.png').convert_alpha()]

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
            self.rect[1] = - (self.rect[3] - ysize)
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
    return sprite.rect[0] < -(sprite.rect[2])

def get_random_pipes(xpos):
    size = random.randint(100, 300)
    pipe = Pipe(False, xpos, size) #obere pipe
    pipe_inverted = Pipe(True, xpos, SCREEN_HEIGHT - size - PIPE_GAP) #untere pipe
    return pipe, pipe_inverted

class FlappyGame:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDHT, SCREEN_HEIGHT))

        self.BACKGROUND = pygame.image.load('assets/sprites/background-day.png')
        self.BACKGROUND = pygame.transform.scale(self.BACKGROUND, (SCREEN_WIDHT, SCREEN_HEIGHT))
        #self.BEGIN_IMAGE = pygame.image.load('assets/sprites/message.png').convert_alpha()    nicht mehr nötig da agent direkt startet

        self.bird_group = pygame.sprite.Group()
        self.ground_group = pygame.sprite.Group()
        self.pipe_group = pygame.sprite.Group()

        self.clock = pygame.time.Clock()  #game schreitet mit 15 fps vorran

        self.passed_pipes = [] #speichert die pipes, die der vogel bereits durchquert hat

        self.num_passed_pipes = 0 #speichert die anzahl der pipes, die der vogel bereits durchquert hat

        self.reset()

    def reset(self):
        self.bird = Bird()
        self.bird_group.empty()
        self.bird_group.add(self.bird)

        self.ground_group.empty()
        for i in range(2):
            ground = Ground(GROUND_WIDHT * i)
            self.ground_group.add(ground)

        self.pipe_group.empty()
        for i in range(2):
            pipes = get_random_pipes(SCREEN_WIDHT * i + 800)
            self.pipe_group.add(pipes[0])
            self.pipe_group.add(pipes[1])

        self.done = False

        self.start_time = time.time()
        self.passed_pipes = []
        self.num_passed_pipes = 0

        return self.get_state()

   

    def get_state(self):
        bird_y_position = self.bird.rect.y

        pipes_sorted_by_x = sorted(self.pipe_group, key=lambda p: p.rect.x)  #lambda ausdruck, geht über jede pipe in pipe group und sortiert sie nach ihren x positionen
        next_pipes= [] #liste für pipes rechts vom vogel

	    #schaut, ob ein pipe paar rechts vom vogel ist. Wenn ja wird es in next_pipes gespeichert
        #da wir immer 2 pipepaare haben müssen wir immer 4 pipes kontrollieren
        if pipes_sorted_by_x[0].rect.x + PIPE_WIDHT > self.bird.rect.x:
            next_pipes.append(pipes_sorted_by_x[0])
            next_pipes.append(pipes_sorted_by_x[1])
        elif pipes_sorted_by_x[2].rect.x + PIPE_WIDHT > self.bird.rect.x:
            next_pipes.append(pipes_sorted_by_x[2])
            next_pipes.append(pipes_sorted_by_x[3])  
        else:
            pass
		
	
        if len(next_pipes) == 0:
            pipe_x = SCREEN_WIDHT
            top_pipe_y = 0
            bot_pipe_y = SCREEN_HEIGHT
        else:
            pipe_x = next_pipes[0].rect.x
        #pipe x ist x position der nächsten pipe

        top_pipe = next_pipes[1]
        bot_pipe = next_pipes[0]
        top_pipe_y = top_pipe.rect.bottom
        bot_pipe_y = bot_pipe.rect.top 

        #return [bird_y_position, bird_speed, pipe_x, top_pipe_y, bot_pipe_y] wir haben uns vorerst gegen bird_speed entschieden, da er sich nicht ändert
        return [bird_y_position, pipe_x, top_pipe_y, bot_pipe_y]

    def step(self, action):
        if action == 1:
            self.bird.bump()

        self.bird_group.update()
        self.ground_group.update()
        self.pipe_group.update()

        if is_off_screen(self.ground_group.sprites()[0]):  #potentiell in andere methoden auslagerm
            self.ground_group.remove(self.ground_group.sprites()[0])
            new_ground = Ground(GROUND_WIDHT - 20)
            self.ground_group.add(new_ground)

        #TODO: reward methoden später auslagern
          
        reward = 0.1   #reward fürs existieren damit der agent länger lebt

        #

        def reward_pipes_strike():
           return self.num_passed_pipes #reward für die anzahl der durchquerten pipes, höhere anzahl = höherer reward
        
        #

        for pipe in self.pipe_group: #reward sofort nach dem durchqueren einer pipe
            if pipe.rect.right < self.bird.rect.left and pipe not in self.passed_pipes:
                self.passed_pipes.append(pipe)
                self.num_passed_pipes += 1
                reward += 2
                reward += reward_pipes_strike()  #reward für das gestaffelte durchqueren der pipes

        #höherer reward, wenn vogel sich der mitte der pipe nähert
        pipes = self.pipe_group.sprites() #länge 4

        upper_next_pipe = self.pipe_group.sprites()[0]
        lower_next_pipe = self.pipe_group.sprites()[1]

        #mittelpunkt der pipe
        #center_next_pipe_x_right = upper_next_pipe.rect.centerx
        center_next_pipe_x = (upper_next_pipe.rect.left + upper_next_pipe.rect.right) / 2
        center_next_pipe_y = (upper_next_pipe.rect.top + lower_next_pipe.rect.bottom) / 2

        #distanz vogel und center der pipe
        #eukldische distanz (omg clustering hat was gebracht)
        distance = math.sqrt((self.bird.rect.centerx - center_next_pipe_x)**2 + (self.bird.rect.centery - center_next_pipe_y)**2)

        reward += 100 / (distance + 1) #je näher der vogel an der mitte der pipe ist, desto höher der reward

        #

        #reward, wenn sich der vogel mittig im bildschirm befindet
        if 100 < self.bird.rect.centery < 400:
            reward += 0.5
        else:
            reward += -1

        #

        #weiteres
        #wenn vogel sehr nah an pipe fliegt, gibt es eine kleine strafe -> mittelpunkt der einzelnen pipes nehmen (nicht die lücke)
        #gleichmäßiges fliegen wird belohnt -> wenn delta y klein ist, ist das gut

        #

        if is_off_screen(self.pipe_group.sprites()[0]):
            self.pipe_group.remove(self.pipe_group.sprites()[0])
            self.pipe_group.remove(self.pipe_group.sprites()[0])
            pipes = get_random_pipes(SCREEN_WIDHT * 2)
            self.pipe_group.add(pipes[0])
            self.pipe_group.add(pipes[1])
            #reward = 1          #sobald eine pipe außerhalb des screens ist, wird der vogel dafür belohnt. Hier wurde getestet ob man es direkt geben soll wenn der vogel
            #pipe durchquert, läuft jedoch fast immer aufs selbe hinaus (außer vogel stirbt SOFORT nachdem er durch pipe geht) dadurch simplerer code


        if (is_off_screen(self.bird_group.sprites()[0])):
            self.done = True
            reward = -10  #wenn vogel aus dem spiel rausfliegt strafe und game beenden

        if (pygame.sprite.groupcollide(self.bird_group, self.ground_group, False, False, pygame.sprite.collide_mask) or
            pygame.sprite.groupcollide(self.bird_group, self.pipe_group, False, False, pygame.sprite.collide_mask)):
            self.done = True
            reward = -10  #wenn vogel mit boden oder pipe collidiert, strafe

            #Rewards müssen noch genauer angepasst werden, wie genau überlegen wir noch
      
        #

        self.screen.blit(self.BACKGROUND, (0, 0))
        self.bird_group.draw(self.screen)
        self.pipe_group.draw(self.screen)
        self.ground_group.draw(self.screen)

        pygame.display.update()
        self.clock.tick(15)

        return self.get_state(), reward, self.done

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
#videos vorbereiten. Screenshots, skizzen etc. 
#geht es auch ohne visuelles?
#pygame unterdrücken?