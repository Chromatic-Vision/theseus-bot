import discord
import common
import logger

intents = discord.Intents.all()
client = discord.Client(intents=intents)

logger = logger.Logger(True,
                       True,
                       "LOG: $color[$info]$reset $timecolor[%H:%M:%S.%f]$reset $message $tracecolor($filename/$funcname:$line)$reset")
logger.reset_log()

# ----------------------------------------------------------------------------------------------------------------------

try:
    with open("token.txt", "r") as f:
        token = f.read()
except:
    logger.error("Token could not be read. Please provide a valid token inside token.txt.")

# ----------------------------------------------------------------------------------------------------------------------

prefix = "="

@client.event
async def on_ready():

    logger.log("Successfully initialized " + client.user.name)

    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='Sussy nike'))

@client.event
async def on_message(raw):
    try:
        await process_message(raw)
    except Exception as e:
        logger.error(repr(e))
        await raw.reply(str(e))

async def process_message(raw: discord.Message):
    message: str = raw.content

    if not message.startswith(prefix):
        return

    command = message[1:]
    base = command.split(" ")[0]

    if base == "help":
        embed_data = {
            "title": "Help list for Theseus bot",
            "description": "Commands:",
            "footer": {
                "text": f"Executed by {raw.author}",
                "icon_url": raw.author.avatar.url
            },
            "fields": [{
                "name": f"{prefix}help",
                "value": "Shows a help list.",
                "inline": True
            },
            {
                "name": f"{prefix}ping",
                "value": "Displays the ping (latency in ms) of the bot.",
                "inline": False
            }
            ]}
        embed = await common.create_embed(embed_data)
        await raw.reply(embed=embed)
    elif base == "ping":
        await raw.reply(f"Ping: {client.latency * 1000}ms")

client.run(token)