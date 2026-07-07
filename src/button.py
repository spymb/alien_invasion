"""UI 按钮模块 — 绘制可点击的 Play 按钮."""

import pygame


class Button:
    """表示游戏中的可点击按钮."""

    def __init__(self, ai_game, msg):
        """初始化按钮属性."""
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()

        # 按钮尺寸与外观
        self.width, self.height = 200, 50
        self.button_color = (0, 135, 0)
        self.text_color = (255, 255, 255)
        self.font = pygame.font.Font(None, 48)

        # 创建 rect 并居中
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = self.screen_rect.center

        # 渲染按钮文字
        self._prep_msg(msg)

    def _prep_msg(self, msg):
        """将 msg 渲染为图像并居中放在按钮上."""
        self.msg_image = self.font.render(msg, True, self.text_color,
                                          self.button_color)
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center

    def draw_button(self):
        """绘制按钮（填充矩形）和文字."""
        self.screen.fill(self.button_color, self.rect)
        self.screen.blit(self.msg_image, self.msg_image_rect)
