import datetime
import json
import random
from enum import Enum


class Harvest:
    def __init__(self, name: str, plantable: int, days_needed=-1, product="undefined", rare="undefined", flag=0, a=1, b=1):
        self.name = name
        self.product = product
        self.rare = rare

        if self.product == "undefined":
            self.product = self.name

        self.plantable = plantable # 0 = not plantable, 1 = only plantable, 2 = plantable and consumable

        self.days_needed = days_needed # how many days its need to be fully growed out

        self.flag = flag  # 0 = default, 1 = random range, 2 = percentage, 3 = random different item drop
        self.a = a
        self.b = b

    def get(self) -> (str, int):
        if self.flag == 0:
            return self.product, 1

        if self.flag == 1:
            return self.product, random.randint(self.a, self.b)

        if self.flag == 2:
            return self.product, int(random.randint(self.a, self.b) == self.a)

        if self.flag == 3:
            if random.randint(self.a, self.b) == self.a:
                return self.rare, 1
            else:
                return self.product, 1

class Harvests(Enum):

    CORN = Harvest("corn", 2, days_needed=2)
    WATERMELON = Harvest("watermelon", 2, flag=1, a=3, b=7)
    DECIDUOUS_TREE = Harvest("deciduous_tree", 1, days_needed=1, product="apple", flag=2, a=1, b=4)
    PEANUTS = Harvest("peanuts", 2, days_needed=2, flag=1, a=2, b=5)
    HERB = Harvest("herb", 2, days_needed=1)
    COW = Harvest("cow", 1, days_needed=1, product="milk")
    POTATO = Harvest("potato", 2, days_needed=2, rare="sweet_potato", flag=3, a=1, b=50)
    APPLE = Harvest("apple", 0)
    MILK = Harvest("milk", 0)
    SWEET_POTATO = Harvest("sweet_potato", 0)

class Farm:

    def __init__(self, name, lx, ly, last_harvest: datetime.datetime):
        self.name = name
        self.lx = lx
        self.ly = ly

        self.last_harvest = last_harvest

        self.farm = [
            Harvests.CORN,
            Harvests.POTATO,
            Harvests.COW,
            Harvests.DECIDUOUS_TREE
        ]

        self.harvests = []
        self.reset()


    def harvest(self):
        for square in self.farm:

            harvest = square.value

            if datetime.datetime.now() - self.last_harvest >= datetime.timedelta(days=harvest.days_needed):
                print("passed:", datetime.datetime.now() - self.last_harvest)
                self.add(harvest.get()[0], harvest.get()[1])

        self.last_harvest = datetime.datetime.now()

        print(self.harvests)

    def add(self, product, amount):
        for slot in self.harvests:
            if slot[0] == product:
                print(f"{product} added: {amount}")
                slot[1] += amount
                break


    def reset(self):

        self.harvests = []

        for harvest in list(Harvests):
            if harvest.value.plantable != 1:
                self.harvests.append([harvest.value.name, 0])


    def get_farm_to_int_list(self):
        res = []

        for square in self.farm:
            res.append(list(Harvests).index(square))

        print(res)
        return res

    def save(self):
        with open(self.name + ".json", "w") as f:

            data = {
                "name": self.name,
                "lx": self.lx,
                "ly": self.ly,
                "last_harvest": self.last_harvest.strftime("%Y-%m-%d %H:%M:%S"),
                "harvests": self.harvests,
                "farm": self.get_farm_to_int_list()
            }

            f.write(json.dumps(data))

    def load(self, filename):
        try:
            with open(filename, "r") as f:
                f.close()

        except FileNotFoundError:
            print(f"farm {filename} not found.")
            return

        with open(filename, "r+") as f:
            try:
                farm_data: dict = json.loads(f.read())

                try:
                    self.name = farm_data["name"]
                    self.lx = farm_data["lx"]
                    self.ly = farm_data["lx"]
                    self.last_harvest = datetime.datetime.strptime(farm_data["last_harvest"], "%Y-%m-%d %H:%M:%S")
                    self.harvests = farm_data["harvests"]

                except KeyError:
                    print("Broken farm detected! Reformatting...")
                    f.truncate()
                    self.save()

            except json.decoder.JSONDecodeError as jde:
                print(f'{filename} JSONDecodeError')
                print(jde)
                print(f'{filename}:')
                f.seek(0)
                print("'" + str(f.read()) + "'")


f = Farm("amogoes", 420, 2, datetime.datetime.now() - datetime.timedelta(days=2, minutes=1))

f.load("Test farm.json")
f.harvest()
print(f.__dict__)
f.save()