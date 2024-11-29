import pygame
import random
import sys
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Dodge the Falling Airplanes")
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
GRAY = (169, 169, 169)
GREEN = (0, 255, 0)
FPS = 60
clock = pygame.time.Clock()
PLAYER_IMAGE = pygame.image.load("player_airplane.png").convert_alpha()
ENEMY_IMAGE = pygame.image.load("enemy_airplane.png").convert_alpha()
BACKGROUND_IMAGE = pygame.image.load("background.png").convert()
BACKGROUND_IMAGE = pygame.transform.scale(BACKGROUND_IMAGE, (SCREEN_WIDTH, SCREEN_HEIGHT))
PLAYER_IMAGE = pygame.transform.scale(PLAYER_IMAGE, (90, 90))
ENEMY_IMAGE = pygame.transform.scale(ENEMY_IMAGE, (90, 90))
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = PLAYER_IMAGE
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        self.speed = 10
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += self.speed
    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top, "up")
        return bullet
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 7
        self.direction = direction
    def update(self):
        if self.direction == "up":
            self.rect.y -= self.speed
        elif self.direction == "down":
            self.rect.y += self.speed
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = ENEMY_IMAGE
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - 50)
        self.rect.y = random.randint(-150, -50)
        self.speed = random.randint(2, 4)
        self.shoot_time = random.randint(60, 180)
    def update(self):
            self.rect.y += self.speed
            if self.rect.top > SCREEN_HEIGHT:
                self.rect.y = random.randint(-150, -50)
                self.rect.x = random.randint(0, SCREEN_WIDTH - 50)
            self.shoot_time -= 1
            if self.shoot_time <= 0:
                self.shoot_time = random.randint(60, 180)
                self.shoot()
    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.bottom, "down")
        game.enemy_bullets.add(bullet)
        game.all_sprites.add(bullet)
class Game:
    def __init__(self):
        self.running = True
        self.score = 0
        self.kills = 0
        self.game_end_reason = None
        self.player = Player()
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        self.enemies = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.enemy_spawn_time = 0
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            clock.tick(FPS)
        if self.game_end_reason == "game_over":
            self.display_game_over_message()
        elif self.game_end_reason == "win":
            self.display_win_message()
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.game_end_reason = "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    self.game_end_reason = "quit"
                if event.key == pygame.K_SPACE:
                    bullet = self.player.shoot()
                    self.all_sprites.add(bullet)
                    self.player_bullets.add(bullet)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if self.exit_button.collidepoint(x, y):
                    self.running = False
                    self.game_end_reason = "quit"
                if self.minimize_button.collidepoint(x, y):
                    pygame.display.iconify()
    def update(self):
        self.enemy_spawn_time += 1
        if self.enemy_spawn_time >= 180:
            self.enemy_spawn_time = 0
            self.spawn_enemy()
        self.all_sprites.update()
        if pygame.sprite.spritecollide(self.player, self.enemies, False):
            print("Player collided with an enemy! Game Over!")
            self.running = False
            self.game_end_reason = "game_over"
        for bullet in self.player_bullets:
            hit_enemies = pygame.sprite.spritecollide(bullet, self.enemies, True)
            for hit in hit_enemies:
                print("Enemy hit by bullet! Enemy destroyed!")
                bullet.kill()
                self.score += 10
                self.kills += 1
                if self.kills >= 10:
                    self.running = False
                    self.game_end_reason = "win"
        for bullet in self.enemy_bullets:
            if pygame.sprite.collide_rect(self.player, bullet):
                print("Player hit by enemy bullet! Game Over!")
                self.running = False
                self.game_end_reason = "game_over"
                bullet.kill()
    def spawn_enemy(self):
        """Spawn a random number of enemies (between 1 and 3)"""
        num_enemies = random.randint(1, 3)
        for _ in range(num_enemies):
            enemy = Enemy()
            while pygame.sprite.collide_rect(self.player, enemy):
                enemy = Enemy()
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)
    def draw(self):
        screen.blit(BACKGROUND_IMAGE, (0, 0))
        self.all_sprites.draw(screen)
        font = pygame.font.SysFont(None, 65)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (20, 20))
        self.exit_button = pygame.draw.rect(screen, GRAY, (SCREEN_WIDTH - 110, 10, 100, 40))
        self.minimize_button = pygame.draw.rect(screen, GRAY, (SCREEN_WIDTH - 220, 10, 100, 40))
        exit_text = pygame.font.SysFont(None, 30).render("Exit", True, WHITE)
        minimize_text = pygame.font.SysFont(None, 30).render("Minimize", True, WHITE)
        screen.blit(exit_text, (SCREEN_WIDTH - 63 - exit_text.get_width() // 2, 20))
        screen.blit(minimize_text, (SCREEN_WIDTH - 170 - minimize_text.get_width() // 2, 20))
        pygame.display.flip()
    def display_game_over_message(self):
        screen.blit(BACKGROUND_IMAGE, (0, 0))
        font = pygame.font.SysFont(None, 120)
        message = font.render("GAME OVER!", True, RED)
        screen.blit(message, (SCREEN_WIDTH // 2 - message.get_width() // 2, SCREEN_HEIGHT // 2 - 80))
        pygame.display.flip()
        pygame.time.wait(2000)
        pygame.quit()
        sys.exit()
    def display_win_message(self):
        screen.blit(BACKGROUND_IMAGE, (0, 0))
        font = pygame.font.SysFont(None, 120)
        message = font.render("You Win!", True, GREEN)
        screen.blit(message, (SCREEN_WIDTH // 2 - message.get_width() // 2, SCREEN_HEIGHT // 2 - 80))
        pygame.display.flip()
        pygame.time.wait(2000)
        pygame.quit()
        sys.exit()
if __name__ == "__main__":
    game = Game()
    game.run()