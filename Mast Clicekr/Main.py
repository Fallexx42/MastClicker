import pygame
from time import sleep
from random import randint
import os
import json

background_color = 0,66,66
global balance
balance = 0

pygame.init()
pygame.font.init()

display_info = pygame.display.Info()

screen_width = 500
screen_height = 700
screen_title = "Mast Clicker"
screen = pygame.display.set_mode((screen_width, screen_height))
icon = pygame.image.load(os.path.join("sprites", "gui", "token.png"))
pygame.display.set_icon(icon)
pygame.display.set_caption(screen_title)
clock = pygame.time.Clock()
tickrate = 60

#====================================Классы

class Hitbox():
    def __init__(self, screen, x, y, width, height, color, weight):
        self.screen = screen
        self.x = x
        self.y = y
        self.width = width 
        self.height = height
        self.color = color
        if weight < 1:
            weight = 1
        self.weight = weight  
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw_hitbox(self):
        pygame.draw.rect(self.screen, self.color, self.rect, self.weight)

class Picture(Hitbox):
    def __init__(self, screen, x, y, width, height, color, weight, path):
        Hitbox.__init__(self, screen, x, y, width, height, color, weight)
        self.path = path
        self.original_image = pygame.image.load(self.path).convert_alpha()
        self.image = pygame.transform.scale(self.original_image, (self.width, self.height))

    def draw_picture(self):
        self.screen.blit(self.image, (self.rect.x, self.rect.y))

class Coin(Picture):
    def __init__(self, screen, x, y, width, height, color, weight, path):
        Picture.__init__(self, screen, x, y, width, height, color, weight, path)
        self.scale = 1.0
        self.animating = False
        self.anim_time = 0
        self.original_width = width
        self.original_height = height
        self.original_x = x
        self.original_y = y
    
    def on_click(self, play_sound=True):
        global balance, click_power
        balance += click_power
        if play_sound:
            coin_clicked_sound.play()
        self.animating = True
        self.anim_time = pygame.time.get_ticks()

    def check_click(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def update_animation(self):
        if self.animating:
            elapsed = pygame.time.get_ticks() - self.anim_time
            if elapsed < 100: 
                if elapsed < 50:  
                    self.scale = 0.8 + (elapsed / 50) * 0.1
                else: 
                    self.scale = 0.9 + ((elapsed - 50) / 50) * 0.1
            else:
                self.animating = False
                self.scale = 1.0
            
            new_width = int(self.original_width * self.scale)
            new_height = int(self.original_height * self.scale)
            self.image = pygame.transform.scale(self.original_image, (new_width, new_height))
            self.rect.x = self.original_x + (self.original_width - new_width) // 2
            self.rect.y = self.original_y + (self.original_height - new_height) // 2
            
    def get_random_position(self):
        random_x = randint(self.rect.x, self.rect.x + self.rect.width)
        random_y = randint(self.rect.y, self.rect.y + self.rect.height)
        return random_x, random_y

class Button:
    def __init__(self, x, y, width, height, text, color, text_color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = pygame.font.Font(None, 16)
        self.is_hovered = False
    
    def draw(self, screen):
        color = self.color
        if self.is_hovered:
            color = (min(color[0] + 30, 255), min(color[1] + 30, 255), min(color[2] + 30, 255))
        
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
        
        lines = self.text.split('\n')
        y_offset = -18
        for line in lines:
            text_surface = self.font.render(line, True, self.text_color)
            text_rect = text_surface.get_rect(center=(self.rect.centerx, self.rect.centery + y_offset))
            screen.blit(text_surface, text_rect)
            y_offset += 16

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
    def check_click(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

class Picture_button(Picture):
    def __init__(self, screen, x, y, width, height, color, weight, path):
        Picture.__init__(self, screen, x, y, width, height, color, weight, path)
        self.scale = 1.0
        self.animating = False
        self.anim_time = 0
        self.original_width = width
        self.original_height = height
        self.original_x = x
        self.original_y = y

    def on_click(self):
        Scene_button_clicked_sound.play()
        self.animating = True
        self.anim_time = pygame.time.get_ticks()

    def check_click(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)    

    def update_animation(self):
        if self.animating:
            elapsed = pygame.time.get_ticks() - self.anim_time
            if elapsed < 100: 
                if elapsed < 50:  
                    self.scale = 0.8 + (elapsed / 50) * 0.1
                else: 
                    self.scale = 0.9 + ((elapsed - 50) / 50) * 0.1
            else:
                self.animating = False
                self.scale = 1.0
            
            new_width = int(self.original_width * self.scale)
            new_height = int(self.original_height * self.scale)
            self.image = pygame.transform.scale(self.original_image, (new_width, new_height))
            self.rect.x = self.original_x + (self.original_width - new_width) // 2
            self.rect.y = self.original_y + (self.original_height - new_height) // 2
        
class FloatingText:
    def __init__(self, x, y, text, color=(255, 255, 0)):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.create_time = pygame.time.get_ticks()
        self.font = pygame.font.Font(None, 32)
        self.lifetime = 500
    
    def draw(self, screen):
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.create_time
        
        if elapsed < self.lifetime:
            y_offset = -elapsed // 20

            font_size = 32 - (elapsed // 25)
            if font_size < 18:
                font_size = 18
            
            font = pygame.font.Font(None, font_size)
            text_surface = font.render(self.text, True, self.color)
            
            screen.blit(text_surface, (self.x - text_surface.get_width() // 2, self.y + y_offset))
            return True
        return False

class AutoClicker:
    def __init__(self):
        self.level = 0
        self.power_level = 0
        self.base_cost = 50
        self.base_power_cost = 500
        self.last_click_time = 0
        
    def get_cost(self):
        if self.level == 0:
            return self.base_cost
        return self.base_cost * (2 ** self.level)
    
    def get_power_cost(self):
        if self.power_level == 0:
            return self.base_power_cost
        return self.base_power_cost * (4 ** self.power_level)
    
    def get_clicks_per_second(self):
        return self.level
    
    def get_power_multiplier(self):
        if self.power_level == 0:
            return 1
        return 2 ** self.power_level
    
    def get_interval(self):
        if self.level == 0:
            return 0
        return 1000 // self.get_clicks_per_second()
    
    def buy_upgrade(self):
        global balance
        cost = self.get_cost()
        if balance >= cost:
            balance -= cost
            self.level += 1
            return True
        return False
    
    def buy_power_upgrade(self):
        global balance, click_power
        cost = self.get_power_cost()
        if balance >= cost:
            balance -= cost
            self.power_level += 1
            click_power = 2 ** self.power_level
            return True
        return False
    
    def update(self, current_time, play_sound):
        if self.level > 0:
            interval = self.get_interval()
            if current_time - self.last_click_time >= interval:
                global balance
                power = self.get_power_multiplier()
                balance += power
                if play_sound:
                    coin_clicked_sound.play()
                coin.animating = True
                coin.anim_time = pygame.time.get_ticks()
                self.last_click_time = current_time

class Database():
    def __init__(self, path):
        self.path = path
        self.data = dict()
        try:
            self.open()
        except FileNotFoundError:
            self.data = {"Balance": 0, "AutoClickerLevel": 0, "AutoClickerPowerLevel": 0, "ClickPowerLevel": 0, "ShootingRangeUnlocked": False, "BackgroundColor": [0, 66, 66], "BgColorLevel": 0, "CoinVolume": 0.5, "SfxVolume": 0.5, "MusicVolume": 0.5}
            self.save()

    def open(self):
        with open(self.path, mode = "r", encoding="utf-8") as file:
            self.data = json.load(file)
    
    def save(self):
        with open(self.path, mode = "w", encoding="utf-8") as file:
            json.dump(self.data, file)

    def get_balance(self):
        return self.data.get("Balance", 0)
    
    def set_balance(self, value):
        self.data["Balance"] = value
        self.save()
    
    def get_auto_clicker_level(self):
        return self.data.get("AutoClickerLevel", 0)
    
    def set_auto_clicker_level(self, value):
        self.data["AutoClickerLevel"] = value
        self.save()
    
    def get_auto_clicker_power_level(self):
        return self.data.get("AutoClickerPowerLevel", 0)
    
    def set_auto_clicker_power_level(self, value):
        self.data["AutoClickerPowerLevel"] = value
        self.save()
    
    def get_click_power_level(self):
        return self.data.get("ClickPowerLevel", 0)
    
    def set_click_power_level(self, value):
        self.data["ClickPowerLevel"] = value
        self.save()
    
    def is_shooting_range_unlocked(self):
        return self.data.get("ShootingRangeUnlocked", False)
    
    def set_shooting_range_unlocked(self, value):
        self.data["ShootingRangeUnlocked"] = value
        self.save()
    
    def get_background_color(self):
        return self.data.get("BackgroundColor", [0, 66, 66])
    
    def set_background_color(self, value):
        self.data["BackgroundColor"] = value
        self.save()
    
    def get_bg_color_level(self):
        return self.data.get("BgColorLevel", 0)
    
    def set_bg_color_level(self, value):
        self.data["BgColorLevel"] = value
        self.save()
    
    def get_coin_volume(self):
        return self.data.get("CoinVolume", 0.5)
    
    def set_coin_volume(self, value):
        self.data["CoinVolume"] = value
        self.save()
    
    def get_sfx_volume(self):
        return self.data.get("SfxVolume", 0.5)
    
    def set_sfx_volume(self, value):
        self.data["SfxVolume"] = value
        self.save()
    
    def get_music_volume(self):
        return self.data.get("MusicVolume", 0.5)
    
    def set_music_volume(self, value):
        self.data["MusicVolume"] = value
        self.save()

class GameSelectButton:
    def __init__(self, x, y, width, height, text, game_name, locked=False, unlock_cost=10000):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.game_name = game_name
        self.font = pygame.font.SysFont('Comic Sans MS', 30)
        self.is_hovered = False
        self.locked = locked
        self.unlock_cost = unlock_cost
        self.color = (50, 50, 80)
        self.locked_color = (80, 50, 50)
        self.hover_color = (80, 80, 110)
        
    
    def draw(self, screen):
        if self.locked:
            color = self.locked_color
        else:
            color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 3)
        
        if self.locked:
            text_surface = self.font.render(self.text, True, (150, 150, 150))
            cost_surface = small_font.render(f"{self.unlock_cost} монет", True, (255, 200, 0))
            text_rect = text_surface.get_rect(center=(self.rect.centerx, self.rect.centery - 15))
            cost_rect = cost_surface.get_rect(center=(self.rect.centerx, self.rect.centery + 20))
            screen.blit(text_surface, text_rect)
            screen.blit(cost_surface, cost_rect)
        else:
            text_surface = self.font.render(self.text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)
    
    def check_hover(self, mouse_pos):
        if not self.locked:
            self.is_hovered = self.rect.collidepoint(mouse_pos)
    
    def check_click(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
    
    def try_unlock(self):
        global balance
        if self.locked and balance >= self.unlock_cost:
            balance -= self.unlock_cost
            self.locked = False
            return True
        return False

class Target:
    def __init__(self, x, y, size):
        self.rect = pygame.Rect(x, y, size, size)
        self.size = size
        self.create_time = pygame.time.get_ticks()
        self.lifetime = 3000
        self.animating = True
        self.scale = 0.3
    
    def update_animation(self):
        if self.animating:
            elapsed = pygame.time.get_ticks() - self.create_time
            if elapsed < 200:
                if elapsed < 100:
                    self.scale = 0.3 + (elapsed / 100) * 0.7
                else:
                    self.scale = 1.0
            else:
                self.animating = False
                self.scale = 1.0
    
    def draw(self, screen):
        self.update_animation()
        
        elapsed = pygame.time.get_ticks() - self.create_time
        if elapsed < self.lifetime:
            if elapsed > self.lifetime - 500:
                pulse = abs((elapsed % 200) - 100) / 100
                color = (255, int(100 + 155 * pulse), int(100 + 155 * pulse))
            else:
                color = (255, 0, 0)
            
            current_size = int(self.size * self.scale)
            offset = (self.size - current_size) // 2
            
            center_x = self.rect.centerx
            center_y = self.rect.centery
            
            pygame.draw.circle(screen, color, (center_x, center_y), current_size // 2)
            pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), current_size // 2, 2)
            pygame.draw.circle(screen, (255, 0, 0), (center_x, center_y), current_size // 4)
            
            if elapsed > self.lifetime - 500:
                if (elapsed // 50) % 2 == 0:
                    pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), current_size // 2 + 5, 2)
            
            return True
        return False
    
    def check_click(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.text = text
        self.dragging = False
        self.font = pygame.font.Font(None, 20)
    
    def draw(self, screen):
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        screen.blit(text_surface, (self.rect.x, self.rect.y - 20))
        
        pygame.draw.rect(screen, (80, 80, 80), self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
        
        handle_x = self.rect.x + (self.value - self.min_val) / (self.max_val - self.min_val) * self.rect.width
        handle_rect = pygame.Rect(handle_x - 10, self.rect.y - 5, 20, self.rect.height + 10)
        pygame.draw.rect(screen, (0, 150, 0), handle_rect)
        pygame.draw.rect(screen, (255, 255, 255), handle_rect, 2)
        
        value_text = self.font.render(str(int(self.value * 100)) + "%", True, (255, 255, 255))
        screen.blit(value_text, (self.rect.x + self.rect.width + 10, self.rect.y + 5))
    
    def check_click(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.dragging = True
            self.update_value(mouse_pos)
            return True
        return False
    
    def check_release(self):
        self.dragging = False
    
    def update_value(self, mouse_pos):
        if self.dragging:
            rel_x = mouse_pos[0] - self.rect.x
            rel_x = max(0, min(rel_x, self.rect.width))
            self.value = self.min_val + (rel_x / self.rect.width) * (self.max_val - self.min_val)
            return True
        return False

class PopupExit():
    def __init__(self):
        self.width = 300
        self.height = 150
        self.x = screen_width // 2 - self.width // 2
        self.y = screen_height // 2 - self.height // 2
        self.active = True
        self.font = pygame.font.Font(None, 24)
        self.yes_button = pygame.Rect(self.x + 50, self.y + 100, 80, 35)
        self.no_button = pygame.Rect(self.x + 170, self.y + 100, 80, 35)

    def draw(self, screen):
        pygame.draw.rect(screen, (50, 50, 50), (self.x, self.y, self.width, self.height))

        text = self.font.render("Вы уверены, что хотите выйти?", True, (255, 255, 255))
        text_rect = text.get_rect(center = (self.x + 150, self.y + 40))
        screen.blit(text, text_rect)

        pygame.draw.rect(screen, (0, 100, 0), self.yes_button)
        yes_text = self.font.render("Да", True, (255, 255, 255))
        yes_rect = yes_text.get_rect(center=self.yes_button.center)
        screen.blit(yes_text, yes_rect)

        pygame.draw.rect(screen, (100, 0, 0), self.no_button)
        no_text = self.font.render("Нет", True, (255, 255, 255))
        no_rect = no_text.get_rect(center=self.no_button.center)
        screen.blit(no_text, no_rect)

        return True

    def check_click(self, mouse_pos):
        if self.yes_button.collidepoint(mouse_pos):
            return "yes"
        elif self.no_button.collidepoint(mouse_pos):
            return "no"
        return None

class Achievement:
    def __init__(self, x, y, width, height, achievement_title, description, locked=True):
        self.rect = pygame.Rect(x, y, width, height)
        self.x = x
        self.y = y
        self.achievement_title = achievement_title
        self.description = description
        self.font = pygame.font.SysFont('Comic Sans MS', 30)
        self.is_hovered = False
        self.locked = locked
        self.color = (50, 50, 80)
        self.locked_color = (80, 50, 50)
        self.hover_color = (80, 80, 110)
        self.achievement_popup = None
        self.question_picture = Picture(screen, self.x + 340, self.y + 5, 47, 47, (0, 0, 0), 10, os.path.join("sprites", "gui", "question.png"))
    
    def draw(self, screen):
        if self.locked:
            color = self.locked_color
        else:
            color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 3)
        

        text_surface = self.font.render(self.achievement_title, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

        
        
        self.question_picture.draw_picture()

        mouse_pos = pygame.mouse.get_pos()

        if self.check_click(mouse_pos):
            self.achievement_popup = PopupAchievement(self)
        if self.achievement_popup:
            self.achievement_popup.draw(screen)

    
    def check_hover(self, mouse_pos):
        if not self.locked:
            self.is_hovered = self.rect.collidepoint(mouse_pos)
    
    def check_click(self, mouse_pos):
        return self.question_picture.rect.collidepoint(mouse_pos)
    
    def unlock(self):
        self.locked = False

class PopupAchievement():
    def __init__(self, Achievement=None):
        self.width = 300
        self.height = 100
        self.x = screen_width // 2 - self.width // 2
        self.y = screen_height // 2 - self.height // 2
        self.active = True
        self.achievement = Achievement
        self.font = pygame.font.Font(None, 24)
        self.accept_button = pygame.Rect(self.x + 50, self.y + 100, 80, 35)

    def draw(self, screen):
        pygame.draw.rect(screen, (50, 50, 50), (self.x, self.y, self.width, self.height))

        lines = self.achievement.description.split('\n')
        y_offset = -18
        for line in lines:
            text_surface = self.font.render(line, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2 + y_offset))
            screen.blit(text_surface, text_rect)
            y_offset += 16

        return True

    def check_click(self, mouse_pos):
        if self.accept_button.collidepoint(mouse_pos):
            return "no"
        return None


#==================================Функции для пинг-понга

def check_ball_collision(new_ball, existing_balls):
    for ball in existing_balls:
        if new_ball.rect.colliderect(ball.rect):
            return True
    return False

def handle_balls_collision(balls):
    for i in range(len(balls)):
        for j in range(i + 1, len(balls)):
            if balls[i].rect.colliderect(balls[j].rect):
                dx = balls[i].rect.centerx - balls[j].rect.centerx
                dy = balls[i].rect.centery - balls[j].rect.centery
                
                if dx != 0 or dy != 0:
                    if abs(dx) > abs(dy):
                        balls[i].speedX *= -1
                        balls[j].speedX *= -1
                    else:
                        balls[i].speedY *= -1
                        balls[j].speedY *= -1
                    
                    if dx > 0:
                        balls[i].rect.x += 5
                        balls[j].rect.x -= 5
                    elif dx < 0:
                        balls[i].rect.x -= 5
                        balls[j].rect.x += 5
                    
                    if dy > 0:
                        balls[i].rect.y += 5
                        balls[j].rect.y -= 5
                    elif dy < 0:
                        balls[i].rect.y -= 5
                        balls[j].rect.y += 5

#==================================Классы Ping pong
class Ping_Pong_Ball(Picture):
    def __init__(self, screen, x, y, width, height, color, weight, path, speed):
        Picture.__init__(self, screen, x, y, width, height, color, weight, path)
        
        rand = randint(1, 2)

        base_speed = randint(4, 8)
        self.speedY = base_speed / 10
        
        if rand == 1:
            self.speedX = base_speed / 10
        else:
            self.speedX = base_speed / 10 * -1
        
        self.max_speed = 12
        self.min_speed = 3
        
        self.animating = True
        self.anim_time = pygame.time.get_ticks()
        self.original_width = width
        self.original_height = height
        self.original_x = x
        self.original_y = y
        self.scale = 0.5
    
    def update_animation(self):
        if self.animating:
            elapsed = pygame.time.get_ticks() - self.anim_time
            if elapsed < 200:
                if elapsed < 100:
                    self.scale = 0.5 + (elapsed / 100) * 0.5
                else:
                    self.scale = 1.0
            else:
                self.animating = False
                self.scale = 1.0
            
            new_width = int(self.original_width * self.scale)
            new_height = int(self.original_height * self.scale)
            self.image = pygame.transform.scale(self.original_image, (new_width, new_height))
            self.rect.x = self.original_x + (self.original_width - new_width) // 2
            self.rect.y = self.original_y + (self.original_height - new_height) // 2
    
    def limit_speed(self):
        if self.speedX > self.max_speed:
            self.speedX = self.max_speed
        elif self.speedX < -self.max_speed:
            self.speedX = -self.max_speed
        
        if self.speedY > self.max_speed:
            self.speedY = self.max_speed
        elif self.speedY < -self.max_speed:
            self.speedY = -self.max_speed
        
        if abs(self.speedX) < self.min_speed and self.speedX != 0:
            self.speedX = self.min_speed if self.speedX > 0 else -self.min_speed
        if abs(self.speedY) < self.min_speed and self.speedY != 0:
            self.speedY = self.min_speed if self.speedY > 0 else -self.min_speed
    
    def move(self):
        if self.rect.colliderect(ping_pong_enemy.rect):
            offset = (self.rect.centerx - ping_pong_enemy.rect.centerx) / (ping_pong_enemy.rect.width / 2)
            self.speedX += offset * 1.5
            self.speedY = abs(self.speedY)
            self.rect.y = ping_pong_enemy.rect.bottom
            self.limit_speed()
        
        if self.rect.colliderect(ping_pong_player.rect):
            offset = (self.rect.centerx - ping_pong_player.rect.centerx) / (ping_pong_player.rect.width / 2)
            self.speedX += offset * 1.5
            self.speedY = -abs(self.speedY)
            self.rect.y = ping_pong_player.rect.top - self.rect.height
            self.limit_speed()
        
        if self.rect.x <= 30:
            self.rect.x = 31
            self.speedX = abs(self.speedX)
        
        if self.rect.x + self.rect.width >= 470:
            self.rect.x = 470 - self.rect.width - 1
            self.speedX = -abs(self.speedX)
        
        self.rect.x += self.speedX
        self.rect.y += self.speedY
        
        self.limit_speed()

class Ping_Pong_Player(Hitbox):
    def __init__(self, screen, x, y, width, height, color, weight, speed):
        Hitbox.__init__(self, screen, x, y, width, height, color, weight)
        self.speed = speed
        self.dx = 0

    def move(self):
        new_x = self.rect.x + int(self.speed * self.dx)
        if new_x >= 30 and new_x + self.width <= 470:
            self.rect.x = new_x

    def contoller(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and not keys[pygame.K_d]:
            self.dx = -1
        elif keys[pygame.K_d] and not keys[pygame.K_a]:
            self.dx = 1
        else:
            self.dx = 0
        self.move()

class Ping_Pong_Enemy(Hitbox):
    def __init__(self, screen, x, y, width, height, color, weight, speed):
        Hitbox.__init__(self, screen, x, y, width, height, color, weight)
        self.speed = speed
    
    def move(self):
        self.rect.x += self.speed
        if self.rect.x <= 30:
            self.speed = abs(self.speed)
        elif self.rect.x + self.width >= 470:
            self.speed = -abs(self.speed)

#==================================Объекты

Game_data = Database(os.path.join("info.json"))
balance = Game_data.get_balance()
background_color = Game_data.get_background_color()
bg_color_level = Game_data.get_bg_color_level()

font = pygame.font.SysFont('Comic Sans MS', 36)
small_font = pygame.font.SysFont('Comic Sans MS', 20)

coin = Coin(screen, 125, 180, 250, 250, (0,0,0), 10, os.path.join("sprites", "clicker", "coin.png"))

Clicker_button = Picture_button(screen, 50, 635, 50, 50, (0,0,0), 10, os.path.join("sprites", "gui", "token.png"))
Games_button = Picture_button(screen, 225, 635, 50, 50, (0,0,0), 10, os.path.join("sprites", "gui", "console-controller.png"))
Lydka_button = Picture_button(screen, 400, 635, 50, 50, (0,0,0), 10, os.path.join("sprites", "gui", "dice-alt.png"))
Settings_button = Picture_button(screen, 440, 20, 40, 40, (0,0,0), 10, os.path.join("sprites", "gui", "settings.png"))

achievement_button = Picture_button(screen, 440, 280, 40, 40, (0, 0, 0), 10, os.path.join("sprites", "gui", "award.png"))
exit_popup = None
exit_button = Picture_button(screen, 440, 230, 40, 40, (0, 0, 0), 10, os.path.join("sprites", "gui", "switch.png"))
return_button = Picture_button(screen, 20, 20, 40, 40, (0, 0, 0), 10, os.path.join("sprites", "gui", "logout.png"))

coin_clicked_sound = pygame.mixer.Sound(os.path.join("sounds", "coin_clicked.wav"))
Scene_button_clicked_sound = pygame.mixer.Sound(os.path.join("sounds", "Scene_button_clicked.wav"))

auto_clicker = AutoClicker()
auto_clicker.level = Game_data.get_auto_clicker_level()
auto_clicker.power_level = Game_data.get_auto_clicker_power_level()

click_power_level = Game_data.get_click_power_level()
click_power = 2 ** click_power_level

floating_texts = []

buy_click_power_button = Button(340, 550, 150, 65, f"Сила клика\n{click_power} (ур.{click_power_level})\n{500 * (2 ** click_power_level)} монет", (210, 240, 210), (0, 0, 0))
buy_auto_button = Button(20, 550, 150, 65, f"Автокликер\nур.{auto_clicker.level}\n{auto_clicker.get_cost()} монет", (210, 240, 210), (0, 0, 0))
buy_auto_power_button = Button(180, 550, 150, 65, f"Сила автокликера\nур.{auto_clicker.power_level}\n{auto_clicker.get_power_cost()} монет", (210, 240, 210), (0, 0, 0))

shooting_range_unlocked = Game_data.is_shooting_range_unlocked()
game1_button = GameSelectButton(60, 200, 380, 150, "Ping-Pong", "pingpong", False, 0)
game2_button = GameSelectButton(60, 400, 380, 150, "Тир", "shooting_range", not shooting_range_unlocked, 10000)


coin_volume = Game_data.get_coin_volume()
sfx_volume = Game_data.get_sfx_volume()
music_volume = Game_data.get_music_volume()

coin_clicked_sound.set_volume(coin_volume)
Scene_button_clicked_sound.set_volume(sfx_volume)

coin_slider = Slider(100, 400, 300, 15, 0, 1, coin_volume, "Звук монеты")
sfx_slider = Slider(100, 450, 300, 15, 0, 1, sfx_volume, "Звуки эффектов")
music_slider = Slider(100, 500, 300, 15, 0, 1, music_volume, "Музыка")

#================Casino
casino_buttons = []
casino_scroll_y = 0
casino_min_scroll = -300
casino_max_scroll = 0

casino_buttons.append(GameSelectButton(60, 100, 380, 100, "Игра 1", "game1", False, 0))
casino_buttons.append(GameSelectButton(60, 220, 380, 100, "Игра 2", "game2", False, 0))
casino_buttons.append(GameSelectButton(60, 340, 380, 100, "Игра 3", "game3", False, 0))
casino_buttons.append(GameSelectButton(60, 460, 380, 100, "Игра 4", "game4", False, 0))
casino_buttons.append(GameSelectButton(60, 580, 380, 100, "Игра 5", "game5", False, 0))
casino_buttons.append(GameSelectButton(60, 700, 380, 100, "Игра 6", "game6", False, 0))

casino_max_scroll = 0
casino_min_scroll = -(len(casino_buttons) * 120 - 440)

#================Ping pong

Ping_Pong_Balls = []

while len(Ping_Pong_Balls) < 3:
    overlap = True
    attempts = 0
    while overlap and attempts < 50:
        random_x = randint(50, 400)
        random_y = randint(120, 180)
        new_ball = Ping_Pong_Ball(screen, random_x, random_y, 25, 25, (0,0,0), 10, os.path.join("sprites", "pingpong", "tennis-ball.png"), 10)
        overlap = check_ball_collision(new_ball, Ping_Pong_Balls)
        attempts += 1
    Ping_Pong_Balls.append(new_ball)

ping_pong_player = Ping_Pong_Player(screen, 225, 500, 50, 10, (0,0,0), 10, 8)
ping_pong_enemy = Ping_Pong_Enemy(screen, 225, 100, 50, 10, (0,0,0), 10, 3)

ping_pong_screen_frame = Hitbox(screen, 30, 80, 440, 500, (0, 0, 0), 10)
pign_pong_background = Picture(screen, 40, 90, 420, 480, (0, 0, 0), 10, os.path.join("sprites", "pingpong", "ping_pong_background.png"))

#=============Achievements





#================

clicker_scene = True
games_scene = False
lydka_scene = False
settings_scene = False
games_menu = True
current_game = None
pingpong_active = False
shooting_range_active = False
achievements_scene = False

shooting_range_score = 0
shooting_range_time = 30
shooting_range_game_started = False
shooting_range_game_over = False
shooting_range_last_spawn = 0
shooting_range_targets = []
shooting_range_targets_count = 3
shooting_range_start_time = 0

is_clicking = False
is_working = True

input_active = False
input_text = ""
input_color = (255, 255, 255)
color_change_cost = 100 * (2 ** bg_color_level)

#============================Цикл

while is_working:
    current_time = pygame.time.get_ticks() 
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            Game_data.set_balance(balance)
            Game_data.set_auto_clicker_level(auto_clicker.level)
            Game_data.set_auto_clicker_power_level(auto_clicker.power_level)
            Game_data.set_click_power_level(click_power_level)
            Game_data.set_shooting_range_unlocked(not game2_button.locked)
            Game_data.set_background_color(background_color)
            Game_data.set_bg_color_level(bg_color_level)
            Game_data.set_coin_volume(coin_volume)
            Game_data.set_sfx_volume(sfx_volume)
            Game_data.set_music_volume(music_volume)
            is_working = False
        
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if settings_scene:
                if exit_button.check_click(mouse_pos):
                    exit_popup = PopupExit()
                if exit_popup:
                    result = exit_popup.check_click(mouse_pos)
                    if result == "yes":
                        Game_data.set_balance(balance)
                        Game_data.set_auto_clicker_level(auto_clicker.level)
                        Game_data.set_auto_clicker_power_level(auto_clicker.power_level)
                        Game_data.set_click_power_level(click_power_level)
                        Game_data.set_shooting_range_unlocked(not game2_button.locked)
                        Game_data.set_background_color(background_color)
                        Game_data.set_bg_color_level(bg_color_level)
                        Game_data.set_coin_volume(coin_volume)
                        Game_data.set_sfx_volume(sfx_volume)
                        Game_data.set_music_volume(music_volume)
                        is_working = False
                    elif result == "no":
                        exit_popup = None 

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if Settings_button.check_click(mouse_pos):
                Settings_button.on_click()
                clicker_scene = False
                games_scene = False
                lydka_scene = False
                settings_scene = True
                achievements_scene = False
            elif Clicker_button.check_click(mouse_pos):
                Clicker_button.on_click()
                clicker_scene = True
                games_scene = False
                lydka_scene = False
                settings_scene = False
                achievements_scene = False
            elif Games_button.check_click(mouse_pos):
                Games_button.on_click()
                clicker_scene = False
                games_scene = True                
                lydka_scene = False
                settings_scene = False
                games_menu = True
                achievements_scene = False
                current_game = None
                pingpong_active = False
                shooting_range_active = False
                shooting_range_game_started = False
                shooting_range_game_over = False
                shooting_range_score = 0
                shooting_range_time = 30
                shooting_range_targets = []
            elif Lydka_button.check_click(mouse_pos):
                Lydka_button.on_click()
                clicker_scene = False
                games_scene = False
                lydka_scene = True
                settings_scene = False
                achievements_scene = False
            elif achievement_button.check_click(mouse_pos):
                achievement_button.on_click()
                clicker_scene = False
                games_scene = False
                lydka_scene = False
                settings_scene = False
                achievements_scene = True

            if achievements_scene:
                if return_button.check_click(mouse_pos):
                    return_button.on_click()
                    Settings_button.on_click()
                    clicker_scene = False
                    games_scene = False
                    lydka_scene = False
                    settings_scene = True
                    achievements_scene = False

            if clicker_scene:
                if coin.check_click(mouse_pos):
                    is_clicking = True

                if buy_click_power_button.check_click(mouse_pos):
                    cost = 500 * (2 ** click_power_level)
                    if balance >= cost:
                        balance -= cost
                        click_power_level += 1
                        click_power = 2 ** click_power_level
                        buy_click_power_button.text = f"Сила клика\n{click_power} (ур.{click_power_level})\n{500 * (2 ** click_power_level)} монет"
                        floating_texts.append(FloatingText(buy_click_power_button.rect.centerx, buy_click_power_button.rect.y - 20, f"Сила клика {click_power}!", (0, 255, 0)))
                    else:
                        floating_texts.append(FloatingText(buy_click_power_button.rect.centerx, buy_click_power_button.rect.y - 20, f"Не хватает!", (255, 0, 0)))
                
                if buy_auto_button.check_click(mouse_pos):
                    if auto_clicker.buy_upgrade():
                        buy_auto_button.text = f"Автокликер\nур.{auto_clicker.level}\n{auto_clicker.get_cost()} монет"
                        floating_texts.append(FloatingText(buy_auto_button.rect.centerx, buy_auto_button.rect.y - 20, f"Автокликер {auto_clicker.level} ур!", (0, 255, 0)))
                    else:
                        floating_texts.append(FloatingText(buy_auto_button.rect.centerx, buy_auto_button.rect.y - 20, f"Не хватает!", (255, 0, 0)))
                
                if buy_auto_power_button.check_click(mouse_pos):
                    if auto_clicker.buy_power_upgrade():
                        buy_auto_power_button.text = f"Сила автокликера\nур.{auto_clicker.power_level}\n{auto_clicker.get_power_cost()} монет"
                        floating_texts.append(FloatingText(buy_auto_power_button.rect.centerx, buy_auto_power_button.rect.y - 20, f"Сила автокликера x{auto_clicker.get_power_multiplier()}!", (0, 255, 0)))
                    else:
                        floating_texts.append(FloatingText(buy_auto_power_button.rect.centerx, buy_auto_power_button.rect.y - 20, f"Не хватает!", (255, 0, 0)))
            
            if games_scene and games_menu:
                if game1_button.check_click(mouse_pos):
                    games_menu = False
                    current_game = "pingpong"
                    pingpong_active = True
                elif game2_button.check_click(mouse_pos):
                    if game2_button.locked:
                        if game2_button.try_unlock():
                            floating_texts.append(FloatingText(screen_width//2, 350, f"Тир разблокирован!", (0, 255, 0)))
                            game2_button.locked = False
                        else:
                            floating_texts.append(FloatingText(screen_width//2, 350, f"Не хватает {game2_button.unlock_cost} монет!", (255, 0, 0)))
                    else:
                        games_menu = False
                        current_game = "shooting_range"
                        shooting_range_active = True
                        shooting_range_game_started = True
                        shooting_range_start_time = current_time
                        shooting_range_score = 0
                        shooting_range_targets = []
            
            if shooting_range_active and shooting_range_game_started and not shooting_range_game_over:
                for target in shooting_range_targets[:]:
                    if target.check_click(mouse_pos):
                        shooting_range_targets.remove(target)
                        shooting_range_score += 1
                        floating_texts.append(FloatingText(mouse_pos[0], mouse_pos[1], "+1", (255, 255, 0)))
                        hit_sound = pygame.mixer.Sound(os.path.join("sounds", "coin_clicked.wav"))
                        hit_sound.set_volume(sfx_volume)
                        hit_sound.play()
            
            if games_scene and not games_menu and shooting_range_game_over:
                if Games_button.check_click(mouse_pos):
                    games_menu = True
                    current_game = None
                    pingpong_active = False
                    shooting_range_active = False
                    shooting_range_game_started = False
                    shooting_range_game_over = False
                    shooting_range_score = 0
                    shooting_range_targets = []
            
            if settings_scene:
                change_color_rect = pygame.Rect(150, 220, 200, 50)
                if change_color_rect.collidepoint(mouse_pos):
                    input_active = True
                    input_text = ""
                
                coin_slider.check_click(mouse_pos)
                sfx_slider.check_click(mouse_pos)
                music_slider.check_click(mouse_pos)
                
                if input_active:
                    submit_rect = pygame.Rect(150, 390, 200, 50)
                    if submit_rect.collidepoint(mouse_pos):
                        parts = input_text.split(",")
                        if len(parts) == 3:
                            try:
                                r = int(parts[0].strip())
                                g = int(parts[1].strip())
                                b = int(parts[2].strip())
                                if 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255:
                                    cost = 100 * (2 ** bg_color_level)
                                    if balance >= cost:
                                        balance -= cost
                                        background_color = [r, g, b]
                                        bg_color_level += 1
                                        floating_texts.append(FloatingText(screen_width//2 - 150, 450, f"Цвет изменён! Следующий будет стоить {100 * (2 ** bg_color_level)} монет", (0, 255, 0)))
                                        input_active = False
                                        input_text = ""
                                    else:
                                        floating_texts.append(FloatingText(screen_width//2 - 150, 450, f"Не хватает {cost} монет!", (255, 0, 0)))
                                else:
                                    floating_texts.append(FloatingText(screen_width//2 - 150, 450, "Ошибка! Значения от 0 до 255", (255, 0, 0)))
                            except:
                                floating_texts.append(FloatingText(screen_width//2 - 150, 450, "Ошибка! Формат: R,G,B", (255, 0, 0)))
                        else:
                            floating_texts.append(FloatingText(screen_width//2 - 150, 450, "Ошибка! Введите 3 числа", (255, 0, 0)))
                
                
        
        if event.type == pygame.KEYDOWN and input_active:
            if event.key == pygame.K_RETURN:
                pass
            elif event.key == pygame.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                input_text += event.unicode
        
        if event.type == pygame.MOUSEBUTTONUP:
            coin_slider.check_release()
            sfx_slider.check_release()
            music_slider.check_release()
        
        if lydka_scene:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    casino_scroll_y = max(casino_min_scroll, casino_scroll_y - 30)
                elif event.button == 5:
                    casino_scroll_y = min(casino_max_scroll, casino_scroll_y + 30)

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and is_clicking:
            if clicker_scene:
                mouse_pos = pygame.mouse.get_pos()
                if coin.check_click(mouse_pos):
                    coin.on_click(True)
                    random_x, random_y = coin.get_random_position()
                    floating_texts.append(FloatingText(random_x, random_y, f"+{click_power}"))
                is_clicking = False

    screen.fill(background_color)       


    if clicker_scene:
        buy_click_power_button.check_hover(mouse_pos)
        buy_auto_button.check_hover(mouse_pos)
        buy_auto_power_button.check_hover(mouse_pos)
        
        coin.draw_picture()
        coin.update_animation()
        
        buy_click_power_button.draw(screen)
        buy_auto_button.draw(screen)
        buy_auto_power_button.draw(screen)
        
        for text in floating_texts[:]:
            if not text.draw(screen):
                floating_texts.remove(text) 

        if auto_clicker.level > 0:
            auto_info = small_font.render(f"Автокликер ур.{auto_clicker.level}: {auto_clicker.get_clicks_per_second()} кл/сек x{auto_clicker.get_power_multiplier()}", True, (200, 200, 200))
            screen.blit(auto_info, (10, 60))
    elif settings_scene:
        settings_text = font.render("Настройки", True, (255, 255, 255))
        screen.blit(settings_text, (screen_width//2 - settings_text.get_width()//2, 80))
        
        color_text = small_font.render(f"Текущий цвет: RGB{tuple(background_color)}", True, (255, 255, 255))
        screen.blit(color_text, (screen_width//2 - color_text.get_width()//2, 140))
        
        cost_text = small_font.render(f"Следующая смена цвета: {100 * (2 ** bg_color_level)} монет", True, (255, 200, 0))
        screen.blit(cost_text, (screen_width//2 - cost_text.get_width()//2, 180))
        
        change_color_rect = pygame.Rect(150, 220, 200, 50)
        color = (0, 100, 0) if change_color_rect.collidepoint(mouse_pos) else (0, 80, 0)
        pygame.draw.rect(screen, color, change_color_rect)
        pygame.draw.rect(screen, (255, 255, 255), change_color_rect, 2)
        change_text = small_font.render("Изменить цвет", True, (255, 255, 255))
        screen.blit(change_text, (change_color_rect.centerx - change_text.get_width()//2, change_color_rect.centery - change_text.get_height()//2))
        
        if input_active:
            input_rect = pygame.Rect(150, 300, 200, 40)
            pygame.draw.rect(screen, (50, 50, 50), input_rect)
            pygame.draw.rect(screen, (255, 255, 255), input_rect, 2)
            input_surface = small_font.render(input_text, True, (255, 255, 255))
            screen.blit(input_surface, (input_rect.x + 5, input_rect.y + 10))
            
            info_text = small_font.render("Введите R,G,B (0-255)", True, (200, 200, 200))
            screen.blit(info_text, (screen_width//2 - info_text.get_width()//2, 360))
            
            submit_rect = pygame.Rect(150, 390, 200, 50)
            submit_color = (0, 100, 0) if submit_rect.collidepoint(mouse_pos) else (0, 80, 0)
            pygame.draw.rect(screen, submit_color, submit_rect)
            pygame.draw.rect(screen, (255, 255, 255), submit_rect, 2)
            submit_text = small_font.render("Подтвердить", True, (255, 255, 255))
            screen.blit(submit_text, (submit_rect.centerx - submit_text.get_width()//2, submit_rect.centery - submit_text.get_height()//2))
        else:
            coin_slider.draw(screen)
            sfx_slider.draw(screen)
            music_slider.draw(screen)
        
        exit_button.draw_picture()
        achievement_button.draw_picture()
        achievement_button.update_animation()
        
        if coin_slider.update_value(mouse_pos):
            coin_volume = coin_slider.value
            coin_clicked_sound.set_volume(coin_volume)
        
        if sfx_slider.update_value(mouse_pos):
            sfx_volume = sfx_slider.value
            Scene_button_clicked_sound.set_volume(sfx_volume)
        
        if music_slider.update_value(mouse_pos):
            music_volume = music_slider.value
        
        for text in floating_texts[:]:
            if not text.draw(screen):
                floating_texts.remove(text)
    
    elif achievements_scene:

        return_button.draw_picture()

        Achievement_100k_money = Achievement(50, 70, 400, 60, "100K Баланс", "Достигните баланса в 100 000 монет")
        Achievement_100k_money.draw(screen)
    
    elif lydka_scene:
        title_text = font.render("Casino", True, (255, 255, 255))
        screen.blit(title_text, (screen_width//2 - title_text.get_width()//2, 20 + casino_scroll_y))
        
        for button in casino_buttons:
            scrolled_rect = button.rect.move(0, casino_scroll_y)
            button.rect.y = scrolled_rect.y
            button.check_hover(mouse_pos)
            button.draw(screen)
            button.rect.y = scrolled_rect.y

    if games_scene:
        if games_menu:
            game1_button.check_hover(mouse_pos)
            game2_button.check_hover(mouse_pos)
            game1_button.draw(screen)
            game2_button.draw(screen)
            title_text = font.render("Выберите игру", True, (255, 255, 255))
            screen.blit(title_text, (screen_width//2 - title_text.get_width()//2, 100))
        else:
            if current_game == "pingpong":
                pign_pong_background.draw_picture()
                ping_pong_enemy.draw_hitbox()
                ping_pong_enemy.move()
                
                for ball in Ping_Pong_Balls[:]:
                    ball.update_animation()
                    ball.draw_picture()
                    ball.move()
                
                handle_balls_collision(Ping_Pong_Balls)
                
                for ball in Ping_Pong_Balls[:]:
                    if ball.rect.centery >= 560:
                        Ping_Pong_Balls.remove(ball)
                    
                    if ball.rect.centery <= 95:
                        reward = click_power * 3
                        balance += reward
                        floating_texts.append(FloatingText(ball.rect.centerx, ball.rect.centery, f"+{reward}", (0, 255, 0)))
                        Ping_Pong_Balls.remove(ball)
                                    
                while len(Ping_Pong_Balls) < 3:
                    overlap = True
                    attempts = 0
                    while overlap and attempts < 50:
                        random_x = randint(50, 400)
                        random_y = randint(120, 180)
                        new_ball = Ping_Pong_Ball(screen, random_x, random_y, 25, 25, (0,0,0), 10, os.path.join("sprites", "pingpong", "tennis-ball.png"), 10)
                        overlap = check_ball_collision(new_ball, Ping_Pong_Balls)
                        attempts += 1
                    Ping_Pong_Balls.append(new_ball)
                
                ping_pong_player.draw_hitbox()
                ping_pong_player.contoller()
                ping_pong_screen_frame.draw_hitbox()

                for text in floating_texts[:]:
                    if not text.draw(screen):
                        floating_texts.remove(text)

            elif current_game == "shooting_range":
                if shooting_range_game_over:
                    game_over_text = font.render("Игра окончена!", True, (255, 255, 255))
                    screen.blit(game_over_text, (screen_width//2 - game_over_text.get_width()//2, 300))
                    score_text = font.render(f"Счёт: {shooting_range_score}", True, (255, 255, 0))
                    screen.blit(score_text, (screen_width//2 - score_text.get_width()//2, 350))
                    reward = shooting_range_score * click_power
                    reward_text = small_font.render(f"Вы заработали {reward} монет!", True, (0, 255, 0))
                    screen.blit(reward_text, (screen_width//2 - reward_text.get_width()//2, 400))
                elif shooting_range_game_started:
                    elapsed_time = (current_time - shooting_range_start_time) // 1000
                    remaining_time = max(0, shooting_range_time - elapsed_time)
                    
                    if remaining_time <= 0 and not shooting_range_game_over:
                        shooting_range_game_over = True
                        shooting_range_game_started = False
                        reward = shooting_range_score * click_power
                        balance += reward
                        floating_texts.append(FloatingText(screen_width//2, 300, f"+{reward} монет!", (0, 255, 0)))
                    
                    while len(shooting_range_targets) < shooting_range_targets_count and not shooting_range_game_over:
                        size = randint(30, 60)
                        x = randint(20, screen_width - size - 20)
                        y = randint(100, 500)
                        new_target = Target(x, y, size)
                        overlap = False
                        for target in shooting_range_targets:
                            if target.rect.colliderect(new_target.rect):
                                overlap = True
                                break
                        if not overlap:
                            shooting_range_targets.append(new_target)
                    
                    for target in shooting_range_targets[:]:
                        if not target.draw(screen):
                            shooting_range_targets.remove(target)
                    
                    score_text = font.render(f"Счёт: {shooting_range_score}", True, (255, 255, 255))
                    screen.blit(score_text, (10, 100))
                    
                    time_text = font.render(f"Время: {remaining_time}", True, (255, 255, 255))
                    screen.blit(time_text, (screen_width - 190, 100))

    auto_clicker.update(current_time, clicker_scene)

    Clicker_button.draw_picture()
    Clicker_button.update_animation()
    Games_button.draw_picture()
    Games_button.update_animation()
    Lydka_button.draw_picture()
    Lydka_button.update_animation()
    
    if exit_popup:
        exit_popup.draw(screen)

    if not achievements_scene:
        balance_len = len(str(balance))
        balance_text = font.render(f"Баланс: {round(balance / 10 ** (balance_len - 3))}", True, (255, 255, 255))
        screen.blit(balance_text, (10, 20))
        Settings_button.draw_picture()
        Settings_button.update_animation()

    pygame.display.update()
    clock.tick(tickrate)

pygame.quit()