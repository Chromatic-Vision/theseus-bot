import datetime
import json
import random
from enum import Enum


class Flag(Enum):
    SINGLE = 0
    RANDOM_RANGE = 1
    PERCENTAGE = 2
    RANDOM_DIFFERENT_ITEM_DROP = 3


class Plantable(Enum):
    NOT_PLANTABLE = 0
    PLANTABLE = 1
    CONSUMABLE_PLANTABLE = 2
    UNOBTAINABLE = 3

class Harvest:
    def __init__(self, name: str, plantable: Plantable, days_needed=-1, product="undefined", rare="undefined", flag: Flag=Flag.SINGLE, a=1, b=1):
        self.name = name
        self.product = product
        self.rare = rare

        if self.product == "undefined":
            self.product = self.name

        self.plantable = plantable

        self.days_needed = days_needed  # how many days it needs to become fully grown

        self.flag = flag
        self.a = a
        self.b = b


    def get(self) -> (str, int):
        if self.flag == Flag.SINGLE:
            return self.product, 1

        if self.flag == Flag.RANDOM_RANGE:
            return self.product, random.randint(self.a, self.b)

        if self.flag == Flag.PERCENTAGE:
            # TODO: allow more than 100%
            return self.product, int(random.randint(self.a, self.b) == self.a)

        if self.flag == Flag.RANDOM_DIFFERENT_ITEM_DROP:
            if random.randint(self.a, self.b) == self.a:
                return self.rare, 1
            else:
                return self.product, 1


class Harvests(Enum):
    GREEN_SQUARE = Harvest("green_square", Plantable.UNOBTAINABLE)
    CORN = Harvest("corn", Plantable.CONSUMABLE_PLANTABLE, days_needed=2)
    WATERMELON = Harvest("watermelon", Plantable.CONSUMABLE_PLANTABLE, flag=Flag.RANDOM_RANGE, a=3, b=7)
    DECIDUOUS_TREE = Harvest("deciduous_tree", Plantable.PLANTABLE, days_needed=1, product="apple", flag=Flag.PERCENTAGE, a=1, b=4)
    PEANUTS = Harvest("peanuts", Plantable.CONSUMABLE_PLANTABLE, days_needed=2, flag=Flag.RANDOM_RANGE, a=2, b=5)
    HERB = Harvest("herb", Plantable.CONSUMABLE_PLANTABLE, days_needed=1)
    COW = Harvest("cow", Plantable.PLANTABLE, days_needed=1, product="milk")
    POTATO = Harvest("potato", Plantable.CONSUMABLE_PLANTABLE, days_needed=2, rare="sweet_potato", flag=Flag.RANDOM_DIFFERENT_ITEM_DROP, a=1, b=50)
    APPLE = Harvest("apple", Plantable.NOT_PLANTABLE)  # TODO: maybe in the future plant an apple and get an apple tree?
    MILK = Harvest("milk", Plantable.NOT_PLANTABLE)
    SWEET_POTATO = Harvest("sweet_potato", Plantable.NOT_PLANTABLE)

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

        self.harvests = {}
        self.reset()


    def harvest(self):

        res = {}

        for square in self.farm:

            harvest = square.value

            if datetime.datetime.now() - self.last_harvest >= datetime.timedelta(days=harvest.days_needed):
                print("passed:", datetime.datetime.now() - self.last_harvest)
                name, value = harvest.get()

                if res.get(name) is None:
                    res[name] = 0

                res[name] += value
                self.add(name, value)

        self.last_harvest = datetime.datetime.now()

        print(self.harvests)
        print("res:", res)
        return res

    def decompile_harvest_result(self, result):
        res = "Added harvests: "
        harvests = []

        for name in result:

            if result[name] == 0:
                continue

            harvests.append(f":{name}:{result[name]}")

        res += str(", ".join(harvests))
        return res if harvests else "Nothing could be harvested!"

    def decomplie_total_harvests(self):
        res = ""
        harvests = []

        for name in self.harvests:

            if self.harvests[name] == 0:
                continue

            harvests.append(f":{name}:{self.harvests[name]}")

        res += str(", ".join(harvests))
        return res

    def get_total_harvests(self) -> int:

        amount = 0

        for name in self.harvests:
            amount += self.harvests[name]

        return amount

    def add(self, product, amount):
        for slot in self.harvests:
            if slot == product:
                print(f"{product} added: {amount}")
                self.harvests[slot] += amount
                break


    def reset(self):

        self.harvests = {}

        for harvest in list(Harvests):
            if not (harvest.value.plantable == Plantable.PLANTABLE or harvest.value.plantable == Plantable.UNOBTAINABLE):
                self.harvests[harvest.value.name] = 0

    def get_farm_to_str_list(self) -> list[str]:
        res = []

        for square in self.farm:
            res.append(square.value.name)

        return res

    def save(self, filename):
        with open(filename, "w") as f:

            data = {
                "name": self.name,
                "lx": self.lx,
                "ly": self.ly,
                "last_harvest": self.last_harvest.strftime("%Y-%m-%d %H:%M:%S"),
                "harvests": self.harvests,
                "farm": self.get_farm_to_str_list()
            }

            f.write(json.dumps(data))

    def load(self, filename):
        with open(filename, "r+") as f:
            try:
                farm_data: dict = json.load(f)

                try:
                    self.name = farm_data["name"]
                    self.lx = farm_data["lx"]
                    self.ly = farm_data["ly"]
                    self.last_harvest = datetime.datetime.strptime(farm_data["last_harvest"], "%Y-%m-%d %H:%M:%S")
                    self.harvests = farm_data["harvests"]

                    self.farm = []
                    for harvest in farm_data["farm"]:
                        self.farm.append(Harvests.__getitem__(harvest.upper()))

                except KeyError:
                    print("Broken farm detected!")
                    # f.truncate()
                    # self.save()

            except json.decoder.JSONDecodeError as jde:
                print(f'{filename} JSONDecodeError')
                print(jde)
                print(f'{filename}:')
                f.seek(0)
                print("'" + str(f.read()) + "'")

    def render(self) -> str:
        out = ''
        for y in range(self.ly):
            for x in range(self.lx):
                i = y * self.lx + x
                out += ':' + self.farm[i].value.name + ':'
            out += '\n'
        return out


if __name__ == '__main__':
    f = Farm("amogoes", 420, 2, datetime.datetime.now() - datetime.timedelta(days=2, minutes=1))

    f.load("amogoes.json")
    f.harvest()
    # print(f.__dict__)
    print(f.get_farm_to_str_list())
    f.save("farms/test.json")
