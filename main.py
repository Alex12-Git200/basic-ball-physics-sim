import pygame
import time


# TODO: Use the sky.jpg and add it as bg

pygame.init()

# get screen info
info = pygame.display.Info()
screen_width = info.current_w
screen_height = info.current_h

font = pygame.font.SysFont("Consolas", 30)  
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
FPS = 120
pygame.display.set_caption(f"Basic Ball Physics Simulation")
clock = pygame.time.Clock()

bounce_sound = pygame.mixer.Sound("bounce.mp3")

ground = pygame.Rect(0, 950, 5000, 700)
button_rect = pygame.Rect(1700, 20, 200, 60)
ball = pygame.Rect(450, 100, 50, 50)
ball_pos_y = float(ball.y)
Y_VELOCITY = 0
X_VELOCITY = 0
GRAVITY = 19
friction = 0.99
isMoving = False
slowmo = False
BOUNCE_DAMPENING = 0.6 
EOOLTCP = False                 # stands for exiting out of loop to close programm
touchingGround = False
has_played_bounce_sound = False

# sky
bg = pygame.image.load("sky.jpg")
bg = pygame.transform.scale(bg, (screen.get_width(), screen.get_height()))

# cube vars # TODO: make the cube being able to move fom the force of the player
cube = pygame.Rect(200, 850, 100, 100)
cube_color = (0, 120, 255)

# BUTTON VARIABLES & COLORS
button_pressed = True
GREEN = (0, 255, 0)
DARK_GREEN = (0, 200, 0)
RED = (255, 0, 0)
DARK_RED = (200, 0, 0)
WHITE = (255, 255, 255)

pause_status = font.render(f"PAUSED", True, WHITE)

running = True


def pause():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    return
            if event.type == pygame.QUIT:
                global EOOLTCP, running 
                EOOLTCP = True
                running = False
                return

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            EOOLTCP = True
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                pause_status = font.render(f"PAUSED", True, WHITE)
                screen.blit(pause_status, (10, 50))
                pygame.display.flip()
                pause()
            if event.key == pygame.K_f:
                if not slowmo:
                    slowmo = True
                    FPS = 20
                else:
                    slowmo = False
                    FPS = 120
            if event.key == pygame.K_F11:
                pygame.display.toggle_fullscreen() 

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            if button_rect.collidepoint(event.pos):
                button_pressed = not button_pressed
                print(f"Button toggled to {'ON' if button_pressed else 'OFF'}")
            else:
                print(f"Mouse clicked at: {mouse_x}, {mouse_y}")
                ball.x = mouse_x
                ball.y = mouse_y
                ball_pos_y = float(ball.y)
                touchingGround = False
                has_played_bounce_sound = False
                Y_VELOCITY = 0
                if button_pressed:
                    X_VELOCITY = 0
                    isMoving = False    
    
    actualFPS = int(clock.get_fps())
    # Draw time 
    screen.blit(bg, (0, 0))  
    fps_text = font.render(f"FPS: {actualFPS}", True, WHITE)
    screen.blit(fps_text, (10, 10))
    pygame.draw.rect(screen, (0, 255, 0), ground)
    pygame.draw.ellipse(screen, (255, 0, 0), ball)
    pygame.draw.rect(screen, cube_color, cube)

    mouse_pos = pygame.mouse.get_pos()
    is_hovered = button_rect.collidepoint(mouse_pos)

    if button_pressed:
        button_color = DARK_RED if is_hovered else RED
    else:
        button_color = DARK_GREEN if is_hovered else GREEN

    # Draw button and text
    pygame.draw.rect(screen, button_color, button_rect)
    button_text_str = "OFF" if button_pressed else "ON"
    button_text = font.render(button_text_str, True, WHITE)
    screen.blit(button_text, (button_rect.x + 70, button_rect.y + 15))

    if slowmo:
        BOUNCE_DAMPENING = 0.8
        GRAVITY = 10
    else:
        BOUNCE_DAMPENING = 0.6
        GRAVITY = 19

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        X_VELOCITY -= 0.05 if touchingGround else 0.02
        isMoving = True
    elif keys[pygame.K_RIGHT]:
        X_VELOCITY += 0.05 if touchingGround else 0.02
        isMoving = True
    else:
        isMoving = False

    
    ball.x += X_VELOCITY
    if ball.colliderect(cube):
        if X_VELOCITY > 0:  # Moving right
            ball.right = cube.left
        elif X_VELOCITY < 0:  # Moving left
            ball.left = cube.right
        X_VELOCITY = 0

    
    if not touchingGround:
        Y_VELOCITY += GRAVITY / FPS 
    ball_pos_y += Y_VELOCITY
    ball.y = int(ball_pos_y)

    if ball.colliderect(cube):
        if Y_VELOCITY > 0:  
            ball.bottom = cube.top
            ball_pos_y = float(ball.y)
            Y_VELOCITY = 0
            touchingGround = True  
        elif Y_VELOCITY < 0:  
            ball.top = cube.bottom
            ball_pos_y = float(ball.y)
            Y_VELOCITY = 0

    # Ground & bounce logic
    if touchingGround and not isMoving:
        X_VELOCITY *= friction
        if abs(X_VELOCITY) < 0.25:
            X_VELOCITY = 0

    if ball.left < 0:
        ball.left = 0
        bounce_sound.play()
        X_VELOCITY = -X_VELOCITY * BOUNCE_DAMPENING

    if ball.right > screen.get_width():
        ball.right = screen.get_width()
        bounce_sound.play()
        X_VELOCITY = -X_VELOCITY * BOUNCE_DAMPENING
    
    if ball.top < 0:
        ball.top = 0
        bounce_sound.play()
        Y_VELOCITY = -Y_VELOCITY * BOUNCE_DAMPENING

    if ball.colliderect(ground):
        ball.bottom = ground.top
        ball_pos_y = float(ball.y)
        Y_VELOCITY = -Y_VELOCITY * BOUNCE_DAMPENING
        
        if abs(Y_VELOCITY) < 1.5:
            Y_VELOCITY = 0
            touchingGround = True
            ball_pos_y = ground.top - ball.height
            ball.y = int(ball_pos_y)
        else:
            touchingGround = False

        if abs(Y_VELOCITY) > 0.5 and not has_played_bounce_sound:
            bounce_sound.play()
            has_played_bounce_sound = True
    else:
        has_played_bounce_sound = False

    if Y_VELOCITY > GRAVITY or Y_VELOCITY < -GRAVITY:
        Y_VELOCITY = GRAVITY

    print(f"YV: {Y_VELOCITY:.3f} | XV: {X_VELOCITY} | TG: {touchingGround} | G: {GRAVITY} | SM: {slowmo}")

    pygame.display.flip()
    clock.tick(FPS)

if EOOLTCP:
    EOOLTCP = False
    pygame.quit()
