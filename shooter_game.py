import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 700, 500
FPS = 60
WHITE = (255, 255, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Game")

background = pygame.image.load("galaxy.jpg")
player_image = None
enemy_image = pygame.transform.scale(pygame.image.load("ufo.png"), (60, 60))
bullet_image = pygame.Surface((5, 15))  
bullet_image.fill((255, 0, 0))

pygame.mixer.music.load("space.ogg")
pygame.mixer.music.play(-1)

fire_sound = pygame.mixer.Sound("fire.ogg")

font = pygame.font.Font(None, 36)
clock = pygame.time.Clock()

class GameSprite(pygame.sprite.Sprite):
    def __init__(self, image, *groups):
        super().__init__(*groups)
        self.image = image
        self.rect = self.image.get_rect()

class Player(GameSprite):
    def __init__(self):
        super().__init__(player_image)
        self.rect.center = (WIDTH // 2, HEIGHT - 50)
        self.speed = 10
        self.speed_boost_timer = 0

    def update(self):
        keys = pygame.key.get_pressed()
        current_speed = self.speed
        
        if self.speed_boost_timer > 0:
            current_speed = self.speed * 2
            self.speed_boost_timer -= 1
        
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= current_speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += current_speed

    def apply_speed_boost(self):
        self.speed_boost_timer = 300

class Player2(GameSprite):
    def __init__(self):
        super().__init__(player_image)
        self.rect.center = (WIDTH // 4, HEIGHT - 50)
        self.shoot_timer = 0
        self.direction = 1
        self.speed = 5
        self.speed_boost_timer = 0

    def update(self):
        current_speed = self.speed
        
        if self.speed_boost_timer > 0:
            current_speed = self.speed * 2
            self.speed_boost_timer -= 1
        
        self.rect.x += self.direction * current_speed
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.direction *= -1
        
        self.shoot_timer += 1
        if self.shoot_timer >= 20:
            new_bullets = create_weapon_bullet(self.rect.centerx, self.rect.top)
            for bullet in new_bullets:
                bullets.add(bullet)
                all_sprites.add(bullet)
            fire_sound.play()
            self.shoot_timer = 0

    def apply_speed_boost(self):
        self.speed_boost_timer = 300

class Enemy(GameSprite):
    def __init__(self, speed=3):
        super().__init__(enemy_image)
        self.speed = speed
        self.x_speed = random.choice([-2, -1, 1, 2])
        self.reset_pos()

    def update(self):
        self.rect.y += self.speed
        self.rect.x += self.x_speed
        
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.x_speed *= -1
        
        if self.rect.top > HEIGHT:
            self.reset_pos()
            global missed
            missed += 1

    def reset_pos(self):
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-150, -60)
        self.x_speed = random.choice([-2, -1, 1, 2])

class BossEnemy(GameSprite):
    def __init__(self):
        boss_image = pygame.transform.scale(enemy_image, (150, 150))
        super().__init__(boss_image)
        self.health = 10
        self.max_health = 10
        self.speed = 1
        self.rect.center = (WIDTH // 2, 50)
        self.direction = 1

    def update(self):
        self.rect.x += self.direction * self.speed
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.direction *= -1

    def take_damage(self):
        self.health -= 1
        if self.health <= 0:
            self.kill()
            return True
        return False

class Bullet(GameSprite):
    def __init__(self, x, y, image, speed=7):
        super().__init__(image)
        self.rect.center = (x, y)
        self.speed = speed

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()

class PowerUp(GameSprite):
    def __init__(self):
        powerup_image = pygame.Surface((30, 30))
        powerup_image.fill((0, 255, 255))
        super().__init__(powerup_image)
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = -50
        self.type = random.choice(['life', 'speed'])
        
        if self.type == 'life':
            self.image.fill((255, 0, 255))
        else:
            self.image.fill((255, 255, 0))

    def update(self):
        self.rect.y += 3
        if self.rect.top > HEIGHT:
            self.kill()

def show_menu():
    global player_mode
    menu_running = True
    
    while menu_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    player_mode = 1
                    menu_running = False
                elif event.key == pygame.K_2:
                    player_mode = 2
                    menu_running = False
        
        screen.blit(background, (0, 0))
        
        title_text = font.render("SPACE GAME", True, WHITE)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//2 - 100))
        
        question_text = font.render("Would you like 1 player or 2 players?", True, WHITE)
        screen.blit(question_text, (WIDTH//2 - question_text.get_width()//2, HEIGHT//2 - 50))
        
        option1_text = font.render("Press 1 for Single Player", True, WHITE)
        screen.blit(option1_text, (WIDTH//2 - option1_text.get_width()//2, HEIGHT//2))
        
        option2_text = font.render("Press 2 for Two Players", True, WHITE)
        screen.blit(option2_text, (WIDTH//2 - option2_text.get_width()//2, HEIGHT//2 + 50))
        
        pygame.display.flip()
        clock.tick(FPS)

def show_rocket_selection():
    global selected_rocket
    
    rocket1_image = pygame.transform.scale(pygame.image.load("rocket.png"), (110, 110))
    rocket2_image = pygame.transform.scale(pygame.image.load("rocket2.png"), (110, 110))
    
    selection_running = True
    
    while selection_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    selected_rocket = "rocket.png"
                    selection_running = False
                elif event.key == pygame.K_2:
                    selected_rocket = "rocket2.png"
                    selection_running = False
        
        screen.blit(background, (0, 0))
        
        title_text = font.render("SELECT YOUR ROCKET", True, WHITE)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//2 - 150))
        
        screen.blit(rocket1_image, (WIDTH//2 - 200, HEIGHT//2 - 50))
        rocket1_text = font.render("Press 1 for Rocket 1", True, WHITE)
        screen.blit(rocket1_text, (WIDTH//2 - 200 + 55 - rocket1_text.get_width()//2, HEIGHT//2 + 80))
        
        screen.blit(rocket2_image, (WIDTH//2 + 90, HEIGHT//2 - 50))
        rocket2_text = font.render("Press 2 for Rocket 2", True, WHITE)
        screen.blit(rocket2_text, (WIDTH//2 + 90 + 55 - rocket2_text.get_width()//2, HEIGHT//2 + 80))
        
        pygame.display.flip()
        clock.tick(FPS)

def show_weapon_selection():
    global selected_weapon
    
    
    weapon1_image = bullet_image  
    weapon2_image = pygame.transform.scale(pygame.image.load("ball.png"), (30, 30))
    weapon3_image = pygame.transform.scale(pygame.image.load("gum.png"), (30, 30))
    
    selection_running = True
    
    while selection_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    selected_weapon = "default"
                    selection_running = False
                elif event.key == pygame.K_2:
                    selected_weapon = "ball"
                    selection_running = False
                elif event.key == pygame.K_3:
                    selected_weapon = "gum"
                    selection_running = False
        
        screen.blit(background, (0, 0))
        
        title_text = font.render("SELECT YOUR WEAPON", True, WHITE)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//2 - 150))
        
        
        screen.blit(weapon1_image, (WIDTH//2 - 150, HEIGHT//2 - 50))
        weapon1_text = font.render("1 - Default Bullet", True, WHITE)
        screen.blit(weapon1_text, (WIDTH//2 - 150, HEIGHT//2 + 20))
        
        
        screen.blit(weapon2_image, (WIDTH//2 - 15, HEIGHT//2 - 50))
        weapon2_text = font.render("2 - Ball (Fast)", True, WHITE)
        screen.blit(weapon2_text, (WIDTH//2 - 15, HEIGHT//2 + 20))
        
       
        screen.blit(weapon3_image, (WIDTH//2 + 120, HEIGHT//2 - 50))
        weapon3_text = font.render("3 - Gum (Triple)", True, WHITE)
        screen.blit(weapon3_text, (WIDTH//2 + 120, HEIGHT//2 + 20))
        
        pygame.display.flip()
        clock.tick(FPS)

def load_player_image():
    global player_image
    player_image = pygame.transform.scale(pygame.image.load(selected_rocket), (110, 110))

def create_weapon_bullet(x, y):
    bullets_created = []
    
    if selected_weapon == "default":
        
        bullet = Bullet(x, y, bullet_image, 7)
        bullets_created.append(bullet)
    
    elif selected_weapon == "ball":
        
        ball_image = pygame.transform.scale(pygame.image.load("ball.png"), (10, 10))
        bullet = Bullet(x, y, ball_image, 12)  
        bullets_created.append(bullet)
    
    elif selected_weapon == "gum":
        
        gum_image = pygame.transform.scale(pygame.image.load("gum.png"), (8, 8))
        bullet1 = Bullet(x - 15, y, gum_image, 8)  
        bullet2 = Bullet(x, y, gum_image, 8)       
        bullet3 = Bullet(x + 15, y, gum_image, 8) 
        bullets_created.extend([bullet1, bullet2, bullet3])
    
    return bullets_created

def show_pause_menu():
    pause_running = True
    while pause_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        
        screen.blit(background, (0, 0))
        all_sprites.draw(screen)
        
        pause_surface = pygame.Surface((WIDTH, HEIGHT))
        pause_surface.set_alpha(128)
        pause_surface.fill((0, 0, 0))
        screen.blit(pause_surface, (0, 0))
        
        pause_text = font.render("PAUSED", True, WHITE)
        screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 - 50))
        
        resume_text = font.render("Press R to Resume", True, WHITE)
        screen.blit(resume_text, (WIDTH//2 - resume_text.get_width()//2, HEIGHT//2))
        
        exit_text = font.render("Press ESC to Exit", True, WHITE)
        screen.blit(exit_text, (WIDTH//2 - exit_text.get_width()//2, HEIGHT//2 + 50))
        
        pygame.display.flip()
        clock.tick(FPS)

def get_level_info(level):
    level_data = {
        1: (5, 3),
        2: (7, 4),
        3: (9, 5),
        4: (11, 6),
        5: (13, 7)
    }
    return level_data.get(min(level, 5), (13, 7))

def update_level():
    global level, enemies, boss
    
    if level == 5:
        for enemy in enemies:
            enemy.kill()
        enemies.empty()
        boss = BossEnemy()
        all_sprites.add(boss)
    else:
        enemy_count, enemy_speed = get_level_info(level)
        for enemy in enemies:
            enemy.kill()
        enemies.empty()
        for _ in range(enemy_count):
            enemy = Enemy(enemy_speed)
            enemies.add(enemy)


player_mode = 1
player2 = None
selected_rocket = "rocket.png"
selected_weapon = "default"
level = 1
missed = 0
hits = 0
lives_player1 = 3
lives_player2 = 3
paused = False
boss = None
last_powerup_time = 0
shots_fired = 0
reload_timer = 0
is_reloading = False


show_menu()
show_rocket_selection()
show_weapon_selection()
load_player_image()


player = Player()
if player_mode == 2:
    player2 = Player2()

enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()

enemy_count, enemy_speed = get_level_info(level)
for _ in range(enemy_count):
    enemies.add(Enemy(enemy_speed))

if player_mode == 2:
    all_sprites = pygame.sprite.Group(player, player2, *enemies)
else:
    all_sprites = pygame.sprite.Group(player, *enemies)


while True:
    current_time = pygame.time.get_ticks()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not is_reloading:
                    
                    new_bullets = create_weapon_bullet(player.rect.centerx, player.rect.top)
                    for bullet in new_bullets:
                        bullets.add(bullet)
                        all_sprites.add(bullet)
                    fire_sound.play()
                    shots_fired += 1
                    
                    
                    if shots_fired >= 5:
                        is_reloading = True
                        reload_timer = 180  
                        shots_fired = 0
            if event.key == pygame.K_p:
                paused = not paused
                if paused:
                    show_pause_menu()
                    paused = False

    if paused:
        continue

    
    if is_reloading:
        reload_timer -= 1
        if reload_timer <= 0:
            is_reloading = False

    
    if current_time - last_powerup_time > 10000:
        powerup = PowerUp()
        powerups.add(powerup)
        all_sprites.add(powerup)
        last_powerup_time = current_time

    all_sprites.update()

    
    powerup_hits = pygame.sprite.spritecollide(player, powerups, True)
    for powerup in powerup_hits:
        if powerup.type == 'life':
            lives_player1 = min(lives_player1 + 1, 5)
        else:
            player.apply_speed_boost()

    if player_mode == 2 and player2:
        powerup_hits2 = pygame.sprite.spritecollide(player2, powerups, True)
        for powerup in powerup_hits2:
            if powerup.type == 'life':
                lives_player2 = min(lives_player2 + 1, 5)
            else:
                player2.apply_speed_boost()

   
    if level == 5 and boss:
        boss_hits = pygame.sprite.spritecollide(boss, bullets, True)
        for hit in boss_hits:
            if boss.take_damage():
                win_text = font.render("Victory! You defeated the Boss!", True, (0, 255, 0))
                screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2))
                pygame.display.flip()
                pygame.time.delay(3000)
                pygame.quit()
                sys.exit()
    else:
        hits_dict = pygame.sprite.groupcollide(enemies, bullets, False, True)
        for enemy in hits_dict:
            enemy.reset_pos()
            hits += 1
            if hits % 5 == 0 and level < 5:
                level += 1
                update_level()
                all_sprites = pygame.sprite.Group()
                all_sprites.add(player)
                if player_mode == 2 and player2:
                    all_sprites.add(player2)
                if level == 5:
                    all_sprites.add(boss)
                else:
                    all_sprites.add(*enemies)
                all_sprites.add(*bullets)
                all_sprites.add(*powerups)

    
    player_hit = pygame.sprite.spritecollideany(player, enemies)
    if level == 5 and boss:
        if pygame.sprite.collide_rect(player, boss):
            player_hit = True

    player2_hit = False
    if player_mode == 2 and player2:
        player2_hit = pygame.sprite.spritecollideany(player2, enemies)
        if level == 5 and boss:
            if pygame.sprite.collide_rect(player2, boss):
                player2_hit = True

    if player_hit:
        lives_player1 -= 1
        player.rect.center = (WIDTH // 2, HEIGHT - 50)

    if player2_hit and player_mode == 2:
        lives_player2 -= 1
        player2.rect.center = (WIDTH // 4, HEIGHT - 50)

    
    if lives_player1 <= 0 or (player_mode == 2 and lives_player2 <= 0):
        lose_text = font.render("Game Over! No more lives!", True, (255, 0, 0))
        screen.blit(lose_text, (WIDTH//2 - lose_text.get_width()//2, HEIGHT//2))
        pygame.display.flip()
        pygame.time.delay(3000)
        pygame.quit()
        sys.exit()

    if missed >= 5:
        lose_text = font.render("Too many missed! Defeat!", True, (255, 0, 0))
        screen.blit(lose_text, (WIDTH//2 - lose_text.get_width()//2, HEIGHT//2))
        pygame.display.flip()
        pygame.time.delay(3000)
        pygame.quit()
        sys.exit()

    
    if hits >= 20 and level < 5:
        win_text = font.render("Victory! You saved the galaxy!", True, (0, 255, 0))
        screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2))
        pygame.display.flip()
        pygame.time.delay(3000)
        pygame.quit()
        sys.exit()

    
    screen.blit(background, (0, 0))
    all_sprites.draw(screen)
    
    
    screen.blit(font.render(f"Level: {level}", True, WHITE), (10, 10))
    screen.blit(font.render(f"Hits: {hits}", True, WHITE), (10, 50))
    screen.blit(font.render(f"Missed: {missed}", True, WHITE), (10, 90))
    screen.blit(font.render(f"Lives P1: {lives_player1}", True, WHITE), (10, 130))

    if player_mode == 2:
        screen.blit(font.render(f"Lives P2: {lives_player2}", True, WHITE), (10, 170))

    
    if level == 5 and boss:
        pygame.draw.rect(screen, (255, 0, 0), (WIDTH//2 - 100, 10, 200, 20))
        health_width = int((boss.health / boss.max_health) * 200)
        pygame.draw.rect(screen, (0, 255, 0), (WIDTH//2 - 100, 10, health_width, 20))
        boss_health_text = font.render(f"Boss Health: {boss.health}", True, WHITE)
        screen.blit(boss_health_text, (WIDTH//2 - boss_health_text.get_width()//2, 35))

    
    if player.speed_boost_timer > 0:
        boost_text = font.render("SPEED BOOST!", True, (255, 255, 0))
        screen.blit(boost_text, (WIDTH//2 - boost_text.get_width()//2, HEIGHT - 100))

   
    if is_reloading:
        reload_text = font.render(f"RELOADING... {reload_timer//60 + 1}s", True, (255, 0, 0))
        screen.blit(reload_text, (WIDTH//2 - reload_text.get_width()//2, HEIGHT - 130))
    else:
        ammo_text = font.render(f"Shots: {shots_fired}/5", True, (255, 255, 255))
        screen.blit(ammo_text, (WIDTH - 150, 10))
        weapon_text = font.render(f"Weapon: {selected_weapon.title()}", True, (255, 255, 255))
        screen.blit(weapon_text, (WIDTH - 150, 50))

    pygame.display.flip()
    clock.tick(FPS)