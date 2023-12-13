import os
import datetime
import discord
import common
import logger
import farm
import utils

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
        self.description_filename = "description.txt"

        self.load_prefix()


    async def process_message(self, raw: discord.Message):

        message: str = raw.content

        if not message.startswith(self.prefix) or raw.author.bot:
            return

        # logger.log(f"Passed message {repr(message)}")
        logger.log(f"{raw.author.name} issued the following command: {message}")

        command = message[self.prefix.__len__():]
        base = command.split(" ")[0]
        branch = command.split(" ", 1)[1] if command.split().__len__() >= 2 else None
        branches = branch.split(" ") if branch is not None else [""]

        if base == "help":
            embed_data = {
                "title": "Theseus bot help menu",
                "description": "Commands:",
                "footer": {
                    "text": f"Executed by {raw.author}",
                    "icon_url": raw.author.avatar.url if raw.author.avatar is not None else None
                },
                "fields": [
                    {
                        "name": f"{self.prefix}help",
                        "value": "Displays a help menu.",
                        "inline": True
                    },
                    {
                        "name": f"{self.prefix}prefix [prefix: str]",
                        "value": "Changes the current prefix.",
                        "inline": False
                    },
                    {
                        "name": f"{self.prefix}prefixspace [prefix: str]",
                        "value": "Changes the current prefix, but with space after the prefix.",
                        "inline": True
                    },
                    {
                        "name": f"{self.prefix}ping",
                        "value": "Displays the latency of the bot in ms.",
                        "inline": False
                    },
                    {
                        "name": f"{self.prefix}create [name: str]",
                        "value": "Creates a new farm.",
                        "inline": True
                    },
                    {
                        "name": f"{self.prefix}harvest",
                        "value": "Harvests items in your farm.",
                        "inline": False
                    },
                    {
                        "name": f'{self.prefix}render [mode: str > "all"/""]',
                        "value": 'Renders your current farm, with argument "all", every single farm that exist including inventory.',
                        "inline": True
                    },
                    {
                        "name": f'{self.prefix}place [mode: str > "fill"] [start_x] [start_y] [end_x] [end_y] [item]',
                        "value": "Places items in your farm from your inventory. Overwritten items in the farm are stored back, and missing items are purchased automatically.",
                        "inline": False
                    },
                    {
                        "name": f'{self.prefix}sell [item] ["all"/amount: int]',
                        "value": "Sells items from your inventory. Negative values can be used to purchase the item directly.",
                        "inline": True
                    },
                    {
                        "name": f'{self.prefix}view_description',
                        "value": "Displays the current public description.",
                        "inline": False
                    },
                    {
                        "name": f'{self.prefix}set_description [text: str]',
                        "value": "Edits the current public description.",
                        "inline": True
                    }
                ]}
            embed = await common.create_embed(embed_data)
            await raw.reply(embed=embed)

        elif base == "ping":
            await raw.reply(f"Ping: {client.latency * 1000}ms")

        elif base == "prefix":
            self.prefix = str(branch)
            self.save_prefix()
            await raw.reply("Prefix set to " + str(branch))

        elif base == "prefixspace":
            self.prefix = str(branch) + ' '
            self.save_prefix()
            await raw.reply("Prefix set to " + str(branch) + " (with space)")

        elif base == "create":
            id = raw.author.id
            author_name = raw.author.name
            farm_name = str(branch)
            f = farm.Farm(farm_name, 1, datetime.datetime.now())
            filename = os.path.join('farms', str(id) + '.json')
            existed = True

            try:
                f.load(filename)
            except FileNotFoundError:

                if not branch:
                    await raw.reply("Please provide a name for your farm, with syntax '=create [name]'")
                    return

                f.save(filename)
                existed = False

            if existed:
                await raw.reply(f"You already have a farm!")
            else:
                await raw.reply(f"Created farm for user '{raw.author.name}' with name '{str(branch)}'")

            await raw.reply(f.render())

        elif base == "render":
            if str(branch) == "all":
                message = ''
                f = farm.Farm()
                for filename in os.listdir('farms'):
                    f.load(os.path.join('farms', filename))

                    message += ('[' + str(f.level) + ']' + ' '
                                + f.name + ' (' + client.get_user(int(filename.split('.', 1)[0])).name + ')' + '\n'
                                + f.decomplie_total_harvests() + '\n'
                                + '[' + str(f.get_total_harvests()) + '/' + str(f.get_inventory_limit()) + ']' + '\n'
                                + f.render() + '\n')

                await raw.reply(message if message != '' else "No farms found!")
                return

            try:
                id = raw.author.id
                f = farm.Farm()
                f.load(os.path.join('farms', str(id) + '.json'))
            except FileNotFoundError:
                await raw.reply('Your farm has not been found!')
                return

            await raw.reply(f.render())

        elif base == "harvest":
            try:
                f = farm.Farm()
                f.load(os.path.join('farms', str(raw.author.id) + ".json"))

                a = f.decompile_harvest_result(f.harvest())

                logger.log(a)
                await raw.reply(a)
                f.save("farms/" + str(raw.author.id) + ".json")
            except FileNotFoundError:
                await raw.reply('You currently have no farm!')
                return
            return

        elif base == "upgrade":

            try:
                f = farm.Farm()
                f.load(os.path.join('farms', str(raw.author.id) + ".json"))
            except FileNotFoundError:
                await raw.reply('You currently have no farm!')
                return

            cost = f.get_level_cost(f.level + 1)

            if f.harvests["moneybag"] - cost < 0:
                await raw.reply(f"You don't have enough money to upgrade your farm to level {f.level + 1}! ({cost} needed, you only have {f.harvests['moneybag']}:moneybag:)")
                return

            f.level += 1

            for _ in range(f.get_level_cost(f.level)):
                f.farm.append(farm.Harvests.GREEN_SQUARE)

            f.save("farms/" + str(raw.author.id) + ".json")

            await raw.reply(f"Succesfully upgraded you farm to level {f.level} (-{cost}:moneybag:)")

        elif base == "place":

            try:
                f = farm.Farm()
                f.load(os.path.join('farms', str(raw.author.id) + ".json"))
            except FileNotFoundError:
                await raw.reply('You currently have no farm!')
                return

            if len(branches) < 6:
                await raw.reply(f"Too few arguments! send {self.prefix}help for help.")
                return

            mode = branches[0]

            if mode.lower() not in farm.PLACE_MODE:
                await raw.reply(f"{mode.lower()} not in place mode, available: {farm.PLACE_MODE}")
                return

            try:
                start_x = int(branches[1])
                start_y = int(branches[2])
                end_x = int(branches[3])
                end_y = int(branches[4])
            except ValueError:
                await raw.reply("Failed to parse coordinate arguments to 'int'!")
                return

            if (start_x >= f.get_farm_length_from_level(f.level)[0]
                    or start_x < 0):
                await raw.reply(f"Start position {start_x} (x) is out of bounds!")
                return

            if (start_y >= f.get_farm_length_from_level(f.level)[1]
                    or start_y < 0):
                await raw.reply(f"Start position {start_y} (y) is out of bounds!")
                return

            if (end_x >= f.get_farm_length_from_level(f.level)[0]
                    or end_x < 0):
                await raw.reply(f"End position {end_x} (x) is out of bounds!")
                return

            if (end_y >= f.get_farm_length_from_level(f.level)[1]
                    or end_y < 0):
                await raw.reply(f"End position {end_y} (y) is out of bounds!")
                return

            harvest = branches[5]

            try:
                parsed_harvest = farm.Harvests.__getitem__(harvest.upper())
            except KeyError:
                await raw.reply(f"{harvest} is not a valid harvest!")
                return

            if mode == "fill":

                failed = []

                for y in range(start_y, end_y + 1):
                    for x in range(start_x, end_x + 1):
                        i = y * f.get_farm_length_from_level(f.level)[0] + x
                        # print(x, y, i, parsed_harvest)

                        if not f.set_index(i, parsed_harvest):
                            failed.append(f"{parsed_harvest.name} at {i}")

                f.save("farms/" + str(raw.author.id) + ".json")

                failed_str = "\n".join(failed)
                await raw.reply(f"Finished placing!\n\nFailed farm squares:\n{failed_str}")

            else:

                await raw.reply(f"Place mode {mode} is currently unsupported.")

        elif base == "sell":

            if len(branches) < 2:
                await raw.reply(f"Too few arguments! send {self.prefix}help for help.")
                return

            raw_item = branches[0]

            try:
                parsed_item = farm.Harvests.__getitem__(raw_item.upper())
            except KeyError:
                await raw.reply(f"{raw_item} is not a valid item to sell!")
                return

            if parsed_item.value.plantable == farm.Plantable.UNOBTAINABLE:
                await raw.reply(f"{parsed_item.name.lower()} can not be obtained but sold???")
                await raw.reply(f"<@827421329497128981>")
                return

            try:
                f = farm.Farm()
                f.load(os.path.join('farms', str(raw.author.id) + ".json"))
            except FileNotFoundError:
                await raw.reply('You currently have no farm!')
                return

            try:
                sell_amount = int(branches[1]) if branches[1].lower() != "all" else 0.69 # special flag to sell everything
            except ValueError:
                await raw.reply(f"{branches[1]} is not a valid number to sell! send {self.prefix}help for more help.")
                return

            inventory_amount = f.harvests[parsed_item.name.lower()]

            if inventory_amount <= 0:
                await raw.reply("You don't have any of that item!")
                return

            if sell_amount == 0.69:

                f.harvests[parsed_item.name.lower()] = 0
                f.harvests["moneybag"] += (inventory_amount * parsed_item.value.price)

                await raw.reply(f"Success! (:moneybag:+{inventory_amount * parsed_item.value.price}, :{parsed_item.name.lower()}:0)")
            else:

                if inventory_amount < sell_amount:
                    await raw.reply(f"You cannot sell more amounts then you have! ({inventory_amount} in inventory, tried to sell {sell_amount})")
                    return

                f.harvests[parsed_item.name.lower()] -= sell_amount
                f.harvests["moneybag"] += (sell_amount * parsed_item.value.price)

                await raw.reply(f"Success! (:moneybag:+{sell_amount * parsed_item.value.price}, :{parsed_item.name.lower()}:{f.harvests[parsed_item.name.lower()]})")

            f.save("farms/" + str(raw.author.id) + ".json")

        elif base == "view_description":
            await raw.reply(self.load_description())

        elif base == "set_description":

            logger.log(f"{utils.generate_diff(self.load_description(), str(branch))}")
            await raw.reply(f"{utils.generate_diff(self.load_description(), str(branch))}")

            self.save_description(str(branch))
            await raw.reply("Finished!")



    def save_description(self, text: str):
        with open(self.description_filename, "w") as f:
            f.write(text)
            f.close()

    def load_description(self) -> str:
        try:
            with open(self.description_filename, "r") as f:
                return f.read()
        except FileNotFoundError:
            self.save_description("This is the test message!!")
            return "Created new file, since e couldn't find one!"

    def save_prefix(self):
        with open("prefix.txt", "w") as f:
            f.write(self.prefix)
            f.close()

    def load_prefix(self):
        try:
            with open("prefix.txt", "r") as f:
                self.prefix = f.read()
        except FileNotFoundError:
            return "="


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
