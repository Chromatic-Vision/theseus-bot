import discord
import logger

intents = discord.Intents.all()
client = discord.Client(intents=intents)

logger = logger.Logger(True,
                       True,
                       "LOG: $color[$info]$reset $timecolor[%H:%M:%S.%f]$reset $message $tracecolor($filename:$funcname/$line)")
logger.reset_log()

# -------------------------------------------------------------------------------

logger.log("default")
logger.warn("warn!!")
logger.error("fatal")

# @client.event
# async def on_ready():
#
#     logger.log("AAAAAAAAAAAAAAAAAAAAAAAAAAA")
#     print('Succesfully started ' + client.user.name)
#
#     await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='_help'))