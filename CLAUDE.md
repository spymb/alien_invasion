# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 运行游戏

```bash
cd alien_invasion/src
python alien_invasion.py
```

无测试套件、无构建步骤 — 这是一个学习项目，直接运行入口文件即可。

## 游戏操作

| 操作 | 按键 |
|------|------|
| 开始游戏 | 点击绿色 **Play** 按钮 |
| 左移 | **←** 方向键 |
| 右移 | **→** 方向键 |
| 发射子弹 | **空格键** |
| 退出游戏 | **Q** 键 |

**游戏规则**：
- 每次最多同时存在 **3 发**子弹
- 消灭全部外星人 → **升级**，速度与得分倍率提升
- 外星人碰到飞船或到达屏幕底边 → **扣一条命**（共 3 条）
- 生命耗尽 → 游戏结束，可点击 Play 重新开始
- 最高分在同一次程序运行中**跨局保留**

## 架构概览

模块依赖为**单向无环链**，无循环导入：

```
settings.py          ← 纯配置，不 import 任何项目内模块
game_stats.py        ← 仅依赖 settings
ship.py / alien.py / bullet.py   ← 依赖 settings + pygame
button.py            ← 仅依赖 pygame
scoreboard.py        ← 依赖 settings, stats, ship（用于 prep_ships）
alien_invasion.py    ← 主入口，依赖以上所有模块
```

### 核心设计模式

**游戏主循环三段式**（`src/alien_invasion.py:run_game`）：
1. `_check_events()` — 处理键盘/鼠标输入
2. `update` 阶段 — 飞船、子弹、外星人位置更新 + 碰撞检测（仅 `game_active=True`）
3. `_update_screen()` — 绘制所有元素 → `pygame.display.flip()`
4. `clock.tick(60)` — 锁定 60 FPS

**状态机**：整个游戏仅用 `game_active` 一个布尔值切换标题画面 / 游戏进行中。切换逻辑集中在 `_ship_hit()`（掉命或游戏结束）和 `_check_play_button()`（新游戏开始）。

**精灵系统**：Ship、Bullet、Alien 都继承 `pygame.sprite.Sprite`，利用 `pygame.sprite.Group` 批量管理（update/draw 一次调用作用于整组）和 `groupcollide`/`spritecollideany` 做碰撞检测。

**浮点数位置**：Ship 和 Alien 用 `self.x`（float）累加位置，渲染时 `self.rect.x = int(self.x)`，避免每帧截断导致的精度丢失。

### 关键数据流

- **子弹碰撞**：`_check_bullet_alien_collisions()` → `groupcollide(bullets, aliens, True, True)` → 双方删除 → 加分 → 若外星人全灭则升级重建
- **外星人触边**：`_check_fleet_edges()` → 任意外星人 `check_edges()` 返回 True → 整队下移 + 翻转方向
- **飞船被击中**：`spritecollideany` 或外星人触底 → `_ship_hit()` → 扣命 → 清空重建（或游戏结束）
- **speedup_scale=1.1, score_scale=1.5**：每消灭一整波外星人触发加速，分数也随之提高

## 图片资源的 fallback

`ship.py` 和 `alien.py` 使用 `pathlib.Path(__file__).parent / 'images' / '*.bmp'` 加载图片。加载失败时自动降级为彩色 `pygame.Surface` 方块并向 stderr 输出警告，游戏不会崩溃。
