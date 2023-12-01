import datetime
import discord
import common
import logger
import os
import farm

intents = discord.Intents.all()
client = discord.Client(intents=intents)

logger = logger.Logger(True,
                       True,
                       "$color[$info]$reset $timecolor[%H:%M:%S.%f]$reset $message $tracecolor($filename/$funcname:$line)$reset")
logger.reset_log()

# ----------------------------------------------------------------------------------------------------------------------

try:
    with open("token.txt", "r") as f:
        token = f.read()
except:
    logger.error("Token could not be read. Please provide a valid token inside token.txt.")

# ----------------------------------------------------------------------------------------------------------------------

class Bot:

    def __init__(self):
        self.prefix = "="

    async def process_message(self, raw: discord.Message):

        message: str = raw.content

        if not message.startswith(self.prefix) or raw.author.bot:
            return

        logger.log(f"passed message {repr(message)}")

        command = message[self.prefix.__len__():]
        base = command.split(" ")[0]
        branch = command.split(" ", 1)[1] if command.split().__len__() >= 2 else None

        if base == "help":
            embed_data = {
                "title": "Theseus bot help menu",
                "description": "Commands:",
                "footer": {
                    "text": f"Executed by {raw.author}",
                    "icon_url": raw.author.avatar.url if raw.author.avatar is not None else None
                },
                "fields": [{
                    "name": f"{self.prefix}help",
                    "value": "Displays a help menu.",
                    "inline": True
                  },
                  {
                    "name": f"{self.prefix}ping",
                    "value": "Displays the ping (latency in ms) of the bot.",
                    "inline": False
                  }
                ]}
            embed = await common.create_embed(embed_data)
            await raw.reply(embed=embed)

        elif base == "ping":
            await raw.reply(f"Ping: {client.latency * 1000}ms")

        elif base == "prefix":
            self.prefix = str(branch)
            await raw.reply("Prefix set to " + str(branch))

        elif base == "create":
            id = raw.author.id
            author_name = raw.author.name
            farm_name = str(branch)
            f = farm.Farm(farm_name, 2, 2, datetime.datetime.now())
            filename = os.path.join('farms', str(id) + '.json')
            existed = True
            try:
                f.load(filename)
            except FileNotFoundError:
                f.save(filename)
                existed = False
            if existed:
                await raw.reply(f"You already have a farm")
            else:
                await raw.reply(f"Created farm for user '{raw.author.name}' with name '{str(branch)}'")
            await raw.reply(f.render())
            # await raw.reply(f"Creating farms is being worked on. {raw.author.id}, '{str(branch)}'")

        elif base == "render":
            if str(branch) == "all":
                try:
                    message = ''
                    f = farm.Farm("undefined", 2, 2, datetime.datetime.now())
                    for filename in os.listdir('farms'):
                        f.load(os.path.join('farms', filename))

                        message += '[' + str(f.lx) + ']' + ' ' + f.name + ' (' + client.get_user(int(filename.split('.', 1)[0])).name + ')' + '\n' + f.render() + '\n'
                    await raw.reply(message)

                except FileNotFoundError:
                    await raw.reply('No farms')
                    return
                return

            id = raw.author.id
            f = farm.Farm('undefined', 2, 2, datetime.datetime.now())
            f.load(os.path.join('farms', str(id) + '.json'))
            await raw.reply(f.render())

        elif base == "harvest":
            try:
                f = farm.Farm("undefined", 1, 1, datetime.datetime.now())
                f.load(os.path.join('farms', str(raw.author.id) + ".json"))

                a = f.decompile_harvest_result(f.harvest())

                logger.log(a)
                await raw.reply(a)
                f.save("farms/" + str(raw.author.id) + ".json")
            except FileNotFoundError:
                await raw.reply('You currently have no farm!')
                return
            return



bot = Bot()


@client.event
async def on_ready():

    logger.log("Successfully initialized " + client.user.name)

    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='Sussy nike'))


@client.event
async def on_message(raw):
    await bot.process_message(raw)


try:
    os.mkdir('farms')
except FileExistsError:
    pass

client.run(token)
