import configparser
import os

DEFAULT_SIZE = 8
DEFAULT_DEPTH = 3


def load_settings():
    """Charge les paramètres depuis config.ini au niveau du package si présent."""
    settings = {"size": DEFAULT_SIZE, "ai_depth": DEFAULT_DEPTH}
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.ini")
    config_path = os.path.normpath(config_path)
    if os.path.exists(config_path):
        config = configparser.ConfigParser()
        config.read(config_path)
        if config.has_section("game"):
            settings["size"] = config.getint("game", "size", fallback=settings["size"])
            settings["ai_depth"] = config.getint("game", "ai_depth", fallback=settings["ai_depth"])
    if settings["size"] < 6:
        settings["size"] = DEFAULT_SIZE
    if settings["size"] % 2 != 0:
        settings["size"] += 1
    return settings
