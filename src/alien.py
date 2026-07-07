"""外星人模块 — 外星舰队中的单个外星人."""

import sys
from pathlib import Path

import pygame
from pygame.sprite import Sprite


class Alien(Sprite):
    """表示舰队中单个外星人的类."""

    def __init__(self, ai_game):
        """初始化外星人并设置起始位置."""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings

        # 加载外星人图像
        image_path = Path(__file__).parent / 'images' / 'alien.bmp'
        try:
            self.image = pygame.image.load(str(image_path))
        except (FileNotFoundError, pygame.error):
            print(f"警告: 无法加载 {image_path}, 使用红色方块作为备选",
                  file=sys.stderr)
            self.image = pygame.Surface((45, 40))
            self.image.fill((200, 50, 50))

        self.rect = self.image.get_rect()

        # 在每个外星人的 rect 上方留空
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height

        # 存储精确水平位置
        self.x = float(self.rect.x)

    def check_edges(self):
        """如果外星人位于屏幕边缘，返回 True."""
        screen_rect = self.screen.get_rect()
        if self.rect.right >= screen_rect.right or self.rect.left <= 0:
            return True
        return False

    def update(self):
        """向左或向右移动外星人."""
        self.x += self.settings.alien_speed * self.settings.fleet_direction
        self.rect.x = int(self.x)
