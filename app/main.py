import requests
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz
import logging
from datetime import datetime
from opencensus.ext.azure.log_exporter import AzureLogHandler

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
GUILD_ID = int(os.getenv("GUILD_ID"))
API_BASE_URL = os.getenv("API_BASE_URL")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Scheduler setup
scheduler = AsyncIOScheduler()


# api ref https://github.com/axsddlr/vlrggapi
# http://4.246.48.236:3001/match?q=upcoming
def get_matches(url, query_params=None):
    # query params are required
    # options are: "upcoming", "live_score", "results"
    # returns a dict of matches
    url = url + "?q=" + query_params
    logging.debug(f"API URL we are using, along with params: {url}")
    response = requests.get(url).json()
    matches = response["data"]["segments"]
    if not matches:
        logging.debug("unable to pull matches, we got an empty return.")
    return matches


def filter_match_list(matches: list, list_we_care_about: list) -> list:
    filtered_matches = []
    for match in matches[:]:
        if match["team1"] in list_we_care_about or match["team2"] in list_we_care_about:
            logging.debug(f"adding this match to the filtered list: {match}.")
            filtered_matches.append(match)
    return filtered_matches


list_to_filter_on = [
    "Evil Geniuses",
    "Leviatán",
    "LOUD",
    "Sentinels",
    "Cloud9",
    "DRX",
    "Paper Rex",
    "100 Thieves",
    "Team Heretics",
    "G2 Esports",
    "NRG Esports",
    "KRÜ Esports" "FNATIC",
    "Natus Vincere",
]

match_url = API_BASE_URL + "/match"
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# setup app insights logging
if os.getenv("APPINSIGHTS_CONNECTION_STRING"):
    logger = logging.getLogger("valobot")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    azure_handler = AzureLogHandler(
        connection_string=os.environ["APPINSIGHTS_CONNECTION_STRING"]
    )
    azure_handler.setFormatter(formatter)
    logger.addHandler(azure_handler)


@bot.event
async def on_ready():
    logging.info(f"The bot has connected as {bot.user}")

    guild = bot.get_guild(GUILD_ID)
    if guild:
        logging.info(f"bot has connected to the guild: {guild.name} (ID: {guild.id})")
    else:
        print("Guild not found")
        logging.info(f"Bot was unable to find the guild. Guild ID attempted {GUILD_ID}")

    # Define the job to send a message every morning at 9:00 AM
    scheduler.add_job(send_morning_message, "cron", hour=16, minute=0)
    # scheduler.add_job(send_morning_message, "interval", minutes=2)
    scheduler.start()


async def send_morning_message():
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        try:
            logging.debug("attempting to pull upcoming matches...")
            upcoming_matches = get_matches(match_url, query_params="upcoming")
        except Exception as E:
            logging.error("failed to pull upcoming matches.")

        filtered_matches = filter_match_list(upcoming_matches, list_to_filter_on)
        if filtered_matches:
            await channel.send("Upcoming VCT matches: \n")

        full_match_message = ""
        for match in filtered_matches:
            timestamp_str = match["unix_timestamp"]
            # Convert string timestamp to datetime object
            utc_dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            # Convert UTC datetime to PST datetime
            pst_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(
                pytz.timezone("America/Los_Angeles")
            )
            # Format PST datetime as a string in 12-hour format
            pst_time_str = pst_dt.strftime("%Y-%m-%d %I:%M:%S %p %Z")

            match_message = (
                f'**{match["team1"]}** vs **{match["team2"]}** @ __{pst_time_str}__\n'
            )
            full_match_message += match_message
        logging.info(f"Full match message: {full_match_message}")
        if full_match_message:
            await channel.send(full_match_message)
            await channel.send(
                "\nMore details can be found here: https://www.vlr.gg/matches"
            )


bot.run(DISCORD_TOKEN)
