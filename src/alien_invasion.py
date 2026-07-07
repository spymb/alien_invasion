"""外星人入侵 — 主入口模块，包含游戏循环与核心逻辑."""

import sys
from time import sleep

import pygame

from settings import Settings
from game_stats import GameStats
from ship import Ship
from bullet import Bullet
from alien import Alien
from button import Button
from scoreboard import Scoreboard


class AlienInvasion:
    """管理游戏资源和行为的整体类."""

    def __init__(self):
        """初始化游戏并创建游戏资源."""
        pygame.init()

        # 禁用 IME 文本输入，防止输入法拦截按键事件
        pygame.key.stop_text_input()

        self.clock = pygame.time.Clock()
        self.settings = Settings()

        # 创建游戏窗口
        if self.settings.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            # 全屏模式下，用实际屏幕尺寸更新配置
            self.settings.screen_width = self.screen.get_rect().width
            self.settings.screen_height = self.screen.get_rect().height
        else:
            self.screen = pygame.display.set_mode(
                (self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("外星人入侵")

        # 创建游戏状态和记分牌
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        # 创建飞船
        self.ship = Ship(self)

        # 子弹编组
        self.bullets = pygame.sprite.Group()

        # 外星人编组
        self.aliens = pygame.sprite.Group()

        # 创建外星舰队
        self._create_fleet()

        # 创建 Play 按钮
        self.play_button = Button(self, "Play")

        # 游戏状态 — 默认未开始
        self.game_active = False

    def run_game(self):
        """启动游戏主循环."""
        while True:
            self._check_events()

            if self.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()

            self._update_screen()
            self.clock.tick(60)

    def _check_events(self):
        """响应按键和鼠标事件."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_keydown_events(self, event):
        """响应键盘按下事件."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q or event.scancode == 20:
            pygame.quit()
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()

    def _check_keyup_events(self, event):
        """响应键盘释放事件."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _fire_bullet(self):
        """创建一颗新子弹并加入 bullets 编组."""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        """更新子弹位置并处理碰撞."""
        # 更新子弹位置
        self.bullets.update()

        # 删除超出屏幕顶部的子弹
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """检测子弹与外星人的碰撞."""
        # 检测碰撞：双方都删除 (True, True)
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens, True, True)

        if collisions:
            # 计算并累加得分
            for aliens_hit in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens_hit)
            self.sb.prep_score()
            self.sb.check_high_score()

        # 外星人全灭 → 清空子弹、升级、创建新舰队
        if not self.aliens:
            self.bullets.empty()
            self.settings.increase_speed()
            self.stats.level += 1
            self.sb.prep_level()
            self._create_fleet()

    def _update_aliens(self):
        """更新外星人位置并检测与飞船/底边的碰撞."""
        self._check_fleet_edges()
        self.aliens.update()

        # 检测外星人与飞船碰撞
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        # 检测外星人是否到达屏幕底边
        self._check_aliens_bottom()

    def _check_fleet_edges(self):
        """有外星人到达边缘时采取相应措施."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """将整支外星舰队下移并改变移动方向."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _create_fleet(self):
        """创建外星舰队."""
        # 创建一个外星人用于测量尺寸
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size

        # 计算水平方向能容纳的外星人数量
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)
        # 防止屏幕过窄导致数量为 0
        if number_aliens_x < 1:
            number_aliens_x = 1

        # 计算垂直方向能容纳的行数
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height
                             - (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)
        if number_rows < 1:
            number_rows = 1

        # 创建外星舰队
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_number):
        """创建一个外星人并将其放置在当前行."""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size

        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = int(alien.x)
        alien.rect.y = alien_height + 2 * alien_height * row_number
        self.aliens.add(alien)

    def _check_aliens_bottom(self):
        """检查是否有外星人到达屏幕底边."""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # 像飞船被撞到一样处理
                self._ship_hit()
                break

    def _ship_hit(self):
        """响应飞船被外星人撞到."""
        if self.stats.ships_left > 0:
            # 减一条命
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            # 清空子弹和外星人
            self.bullets.empty()
            self.aliens.empty()

            # 创建新舰队并居中飞船
            self._create_fleet()
            self.ship.center_ship()

            # 暂停半秒
            sleep(0.5)
        else:
            self.game_active = False
            pygame.mouse.set_visible(True)

    def _check_play_button(self, mouse_pos):
        """在玩家单击 Play 按钮时开始新游戏."""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active:
            # 重置游戏设置
            self.settings.initialize_dynamic_settings()

            # 重置游戏状态
            self.stats.reset_stats()
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()
            self.sb.prep_high_score()

            # 清空编组
            self.aliens.empty()
            self.bullets.empty()

            # 创建新舰队并居中飞船
            self._create_fleet()
            self.ship.center_ship()

            # 隐藏鼠标光标
            pygame.mouse.set_visible(False)

            # 激活游戏
            self.game_active = True

    def _update_screen(self):
        """每帧更新屏幕上的图像，并切换到新屏幕."""
        self.screen.fill(self.settings.bg_color)

        # 绘制飞船
        self.ship.blitme()

        # 绘制子弹
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()

        # 绘制外星人
        self.aliens.draw(self.screen)

        # 绘制记分牌
        self.sb.show_score()

        # 如果游戏未激活，绘制 Play 按钮
        if not self.game_active:
            self.play_button.draw_button()

        # 刷新屏幕
        pygame.display.flip()


if __name__ == '__main__':
    # 创建游戏实例并运行
    ai = AlienInvasion()
    ai.run_game()
