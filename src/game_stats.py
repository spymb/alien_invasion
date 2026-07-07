"""游戏状态模块 — 管理生命、得分、等级和最高分."""


class GameStats:
    """跟踪游戏统计信息的类."""

    def __init__(self, ai_game):
        """初始化统计信息."""
        self.settings = ai_game.settings
        self.reset_stats()

        # 最高分 — 不在 reset_stats 中重置，跨游戏保留
        self.high_score = 0

    def reset_stats(self):
        """初始化在游戏运行期间变化的统计信息."""
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1
