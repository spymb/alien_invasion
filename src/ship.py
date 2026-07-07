"""玩家飞船模块 — 控制、移动与绘制."""

import sys
from pathlib import Path

import pygame
from pygame.sprite import Sprite


class Ship(Sprite):
    """管理玩家飞船的类."""

    def __init__(self, ai_game):
        """初始化飞船并设置初始位置."""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.screen_rect = ai_game.screen.get_rect()

        # 加载飞船图像
        image_path = Path(__file__).parent / 'images' / 'ship.bmp'
        try:
            self.image = pygame.image.load(str(image_path))
        except (FileNotFoundError, pygame.error):
            print(f"警告: 无法加载 {image_path}, 使用蓝色方块作为备选",
                  file=sys.stderr)
            self.image = pygame.Surface((50, 45))
            self.image.fill((0, 100, 200))

        # 获取 rect 并定位到底部中央
        self.rect = self.image.get_rect()
        self.rect.midbottom = self.screen_rect.midbottom

        # 存储精确水平位置（浮点数）
        self.x = float(self.rect.x)

        # 移动标志
        self.moving_right = False
        self.moving_left = False

    def update(self):
        """根据移动标志更新飞船位置."""
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.settings.ship_speed
        if self.moving_left and self.rect.left > 0:
            self.x -= self.settings.ship_speed

        # 更新 rect 位置
        self.rect.x = int(self.x)

    def blitme(self):
        """在指定位置绘制飞船."""
        self.screen.blit(self.image, self.rect)

    def center_ship(self):
        """将飞船重置到屏幕底部中央."""
        self.rect.midbottom = self.screen_rect.midbottom
        self.x = float(self.rect.x)
