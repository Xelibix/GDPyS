import asyncio
from aiohttp import web
import logging
import random
from handlers.frontend import home_page
from handlers.login import login_handler
from handlers.register import register_handler
from handlers.profiles import profile_comment_handler, profile_handler, user_search_handler, post_account_comment_handler, update_profile_stats_handler, get_account_url_handler, save_user_data_handler, load_save_data_handler
from handlers.songs import featured_artists_handler, get_songinfo_handler
from handlers.levels import level_search_modular_hanlder, download_level, upload_level_handler
from handlers.rewards import quests_handler
from handlers.levelextras import level_comments_handler
from helpers.userhelper import user_helper
from helpers.songhelper import songs
from helpers.ratelimit import rate_limiter
from config import user_config, load_config
from constants import ASCII_ART, Colours
from conn.mysql import create_connection
from os import path

def config_routes(app: web.Application) -> None:
    """Configures all of the routes and handlers."""
    app.router.add_get("/", home_page)
    app.router.add_post("/database/accounts/loginGJAccount.php", login_handler)
    app.router.add_post("/database/accounts/registerGJAccount.php", register_handler)
    app.router.add_post("/database/getGJAccountComments20.php", profile_comment_handler)
    app.router.add_post("/database/getGJUserInfo20.php", profile_handler)
    app.router.add_post("/database/getGJTopArtists.php", featured_artists_handler)
    app.router.add_post("/database/getGJSongInfo.php", get_songinfo_handler)
    app.router.add_post("/database/getGJUsers20.php", user_search_handler)
    app.router.add_post("/database/getGJLevels21.php", level_search_modular_hanlder)
    app.router.add_post("/database/downloadGJLevel22.php", download_level)
    app.router.add_post("/database/uploadGJAccComment20.php", post_account_comment_handler)
    app.router.add_post("/database/updateGJUserScore22.php", update_profile_stats_handler)
    app.router.add_post("/database/getAccountURL.php", get_account_url_handler)
    app.router.add_post("/database/accounts/backupGJAccountNew.php", save_user_data_handler)
    app.router.add_post("/database/uploadGJLevel21.php", upload_level_handler)
    app.router.add_post("/database/accounts/syncGJAccountNew.php", load_save_data_handler)
    app.router.add_post("/database/getGJChallenges.php", quests_handler)
    app.router.add_post("/database/getGJComments21.php", level_comments_handler)

def welcome_sequence(no_ascii : bool = False):
    """Startup welcome print art things."""
    if not no_ascii:
        print(ASCII_ART.format(reset = Colours.reset, col1 = random.choice(Colours.all_col), col2 = random.choice(Colours.all_col), col3 = random.choice(Colours.all_col), col4 = random.choice(Colours.all_col), col5 = random.choice(Colours.all_col)))

def pre_run_checks():
    """Runs checks before startup to make sure all runs smoothly."""
    if not path.exists(user_config["level_path"]) or not path.exists(user_config["save_path"]):
        logging.error("Level/Save path does not exit! Please create it before starting GDPyS.")
        logging.info(f"Set level path: {user_config['level_path']}\nSet save path: {user_config['save_path']}")
        raise SystemExit

async def init(loop):
    """Initialises the app and MySQL connection and all the other systems."""
    app = web.Application(loop=loop)
    await create_connection(loop, user_config)
    await user_helper.cron_calc_ranks()
    songs.top_artists = await songs._top_artists()

    # Setting up rate limiter
    rate_limiter.add_to_struct("register", limit=2) # One IP may only register twice a day.
    rate_limiter.add_to_struct("login", limit=10) # One IP may only try to login ten times a day.
    return app

if __name__ == "__main__":
    load_config()
    # Configures the logger.
    logging_level = logging.DEBUG if user_config["debug"] else logging.INFO
    logging.basicConfig(level = logging_level)
    welcome_sequence()
    pre_run_checks()
    # Inits the app.
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init(loop))
    config_routes(app)
    try:
        web.run_app(app, port=user_config["port"])
    except KeyboardInterrupt:
        print("Shutting down! Bye!")
