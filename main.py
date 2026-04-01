from core.game import Game
from scenes.game_over_scene import GameOverScene
from scenes.game_scene import GameScene
from scenes.level_select_scene import LevelSelectScene
from scenes.menu_scene import MenuScene
from scenes.pause_scene import PauseScene
from scenes.settings_scene import SettingsScene


def main() -> None:
    game = Game()
    game.register_scene("menu", MenuScene)
    game.register_scene("level_select", LevelSelectScene)
    game.register_scene("settings", SettingsScene)
    game.register_scene("game", GameScene)
    game.register_scene("pause", PauseScene)
    game.register_scene("game_over", GameOverScene)
    game.run("menu")


if __name__ == "__main__":
    main()
