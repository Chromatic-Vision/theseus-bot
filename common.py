import discord
import re, datetime

client = discord.Client()

class MessageData:

    def __init__(self, message):
        self.id = message.id
        self.guild = message.guild
        self.category = message.channel.category
        self.channel = message.channel
        self.user = message.author
        self.content = message.content if message.content else message.system_content
        self.stickers = message.stickers
        self.user_mentions = message.mentions
        self.channel_mentions = message.channel_mentions
        self.attachments = message.attachments
        self.embeds = message.embeds
        self.send_time = message.created_at
        self.edit_time = message.edited_at
        self.url = message.jump_url
    
    def __str__(self):
        return "{} : {}".format(self.get_user_name(), self.content)
    
    def __repr__(self):
        return "{} : {}".format(self.get_user_name(), self.content)

    def get_user_name(self):
        return "{}#{}".format(self.user.name, self.user.discriminator) if self.user else ""
    
    def get_text_send_time(self, fmt="%Y-%m-%d %H:%M:%S"):
        return self.send_time.strftime(fmt) if self.send_time else ""
    
    def get_text_edit_time(self, fmt="%Y-%m-%d %H:%M:%S"):
        return self.edit_time.strftime(fmt) if self.edit_time else ""

def get_id(source, digit=18):
    """
    Description
    ------------
     文字列からIDを抽出する

    Parameters
    -----------
     source: str or list or tuple
         文字列、文字列リスト
     digit: int
         IDの桁数（初期値：18）

    Returns
    --------
     ids: int or list
         ID情報

    How to use
    -----------
     Ptn 1.
      text = "<@&123456789012345678>"
      id = get_id(text)
       -> 123456789012345678
     Ptn 2.
      texts = ["<@&123456789012345678>", "<@234567890123456789>"]
      ids = get_id(texts)
       -> [123456789012345678, 234567890123456789]
     Ptn 3.
      text = "<@&123456789012345678> <@234567890123456789>"
      ids = get_id(text)
       -> [123456789012345678, 234567890123456789]
    """
        
    ids = []

    list_flg = type(source) == list or type(source) == tuple

    if type(digit) != int:
        digit = 18
    
    for s in source if list_flg else [source]:
        
        if type(s) != str:
            continue
        
        id = [int(id) for id in re.findall("[0-9]{"+str(digit)+"}", s)]
        ids.extend(id)
    
    ids = list(set(ids))
    
    if not list_flg and len(ids) <= 1:
        ids = ids[0] if ids[0:] else None
    
    return ids

async def get_discord_object(source, ids, *target):
    """
    Description
    ------------
     ID情報からDiscordのオブジェクトを取得する

    Parameters
    -----------
     source: Guild or Channel or ... etc
         取得元のオブジェクト
     
     ids: int or list or tuple
         ID情報
     
     target: str
         取得対象
     
       取得したいオブジェクト   | 指定文字列
      ------------------------------------
       Guild                  | "guild"
       Category               | "category"
       Channel                | "channel"
       User, Member           | "user"
       Message                | "message"
       Role                   | "role"

    Returns
    --------
     objects: dict or object
         オブジェクト情報

    How to use
    -----------
     Ptn 1.
      id = 123456789012345678
      role = await get_discord_object(guild, id, "role")
       -> @SampleRole

     Ptn 2.
      ids = ["234567890123456789", 345678901234567890]
      users = await get_discord_object(guild, ids, "user")
       -> [SampleUser1#1234, SampleUser2#2345]

     Ptn 3.
      ids = [123456789012345678, "234567890123456789", 345678901234567890]
      users_and_roles = await get_discord_object(guild, ids, "user", "role")
       -> {"role": [@SampleRole], "user": [SampleUser1#1234, SampleUser2#2345]}
    """
        
    objects = {}

    list_flg = type(ids) == list or type(ids) == tuple
        
    for id in ids if list_flg else [ids]:

        if type(id) != int and type(id) != str:
            continue
        
        if type(id) == str and not id.isdecimal():
            continue
        
        id = int(id)

        if "guild" in target:

            if "guild" not in objects:
                objects["guild"] = set()

            try:
                guild = source.get_guild(id)
                if guild:
                    objects["guild"].add(guild)
                    continue

            except:
                pass
        
        if "category" in target:

            if "category" not in objects:
                objects["category"] = set()

            try:
                category = source.get_category(id)
                if category:
                    objects["category"].add(category)
                    continue

            except:
                pass
        
        if "channel" in target:

            if "channel" not in objects:
                objects["channel"] = set()

            try:
                channel = source.get_channel(id)
                if channel:
                    objects["channel"].add(channel)
                    continue

            except:
                pass
        
        if "user" in target:

            if "user" not in objects:
                objects["user"] = set()

            try:
                user = source.get_member(id)
                if user:
                    objects["user"].add(user)
                    continue

            except:
                pass
        
        if "message" in target:

            if "message" not in objects:
                objects["message"] = set()

            try:
                message = await source.fetch_message(id)
                if message:
                    objects["message"].add(message)
                    continue

            except:
                pass

        if "role" in target:

            if "role" not in objects:
                objects["role"] = set()

            try:
                role = source.get_role(id)
                if role:
                    objects["role"].add(role)
                    continue

            except:
                pass
    
    if objects:
        for key, value in objects.items():
            if list_flg:
                objects[key] = list(value)
            else:
                objects[key] = list(value)[0] if list(value)[0:] else None

        if len(target) == 1:
            objects = objects[next(iter(objects))]
        
    return objects

async def create_embed(embed_data):
    """
    Description
    ------------
     埋め込みオブジェクトを生成する

    Parameters
    -----------
     embed_data: dict
         埋め込み情報
     
      キー           | 型       | 説明                 | 初期値
     -----------------------------------------------------------------------------
     "title"         | str      | タイトル             | ""
     "description"   | str      | 説明                 | ""
     "color"         | int      | 左辺の色             | 0x36393F # Discordの背景色
     "url"           | str      | タイトルに適応するURL | ""
     "timestamp"     | datetime | 右下に表示する時間    | UTC
     "fields"        | list     | フィールド           | 
     "author"        | dict     | ヘッダー             | 
     "footer"        | dict     | フッター             | 
     "image_url"     | str      | 下部に表示する画像URL | 
     "thumbnail_url" | str      | 右上に表示する画像URL | 
     
      embed_data(サンプル)
      --------------------
      {
        "title": "埋め込みのタイトル",
        "description": "埋め込みの説明",
        "color": 0xFFFF00,
        "url": "URL",
        "timestamp": datetime.datetime.now(),
        "fields": [
          {
            "name": "フィールド名1",
            "value": "フィールド値1",
            "inline": False  # 縦(False)or横(True)に並べる ※省略可(デフォルト:False)
          },
          {
            "name": "フィールド名2",
            "value": "フィールド値2",
            "inline": True
          }
        ],
        "author": {
            "name": "M1zuu#9582",
            "url": "URL",
            "icon_url": "画像URL"
        },
        "footer": {
            "text": "M1zuu#9582",
            "icon_url": "画像URL"
        },
        "image_url": "画像URL",
        "thumbnail_url": "画像URL"
      }
    

    Returns
    --------
     embed: Embed
         埋め込みオブジェクト
    """

    if "title" not in embed_data:
        embed_data["title"] = ""

    if "description" not in embed_data:
        embed_data["description"] = ""

    if "color" not in embed_data or embed_data["color"] == "":
        embed_data["color"] = 0x34aa2c

    if "url" not in embed_data:
        embed_data["url"] = discord.Embed.Empty

    if "timestamp" not in embed_data:
        embed_data["timestamp"] = datetime.datetime.utcnow()
        
    try:
        embed = discord.Embed(title=embed_data["title"],
                                description=embed_data["description"],
                                color=embed_data["color"],
                                url=embed_data["url"],
                                timestamp=embed_data["timestamp"])
    except:
        return None
        
    for key in embed_data:
        if key == "fields":
            for field in embed_data[key]:

                field["inline"] = False if "inline" not in field else field["inline"]

                if field["name"] and field["value"]:
                    embed.add_field(name=field["name"], value=field["value"], inline=field["inline"])

        elif key == "author":
            if embed_data[key]:

                embed_data[key]["url"] = discord.Embed.Empty if "url" not in embed_data[key] else embed_data[key]["url"]
                embed_data[key]["icon_url"] = discord.Embed.Empty if "icon_url" not in embed_data[key] else embed_data[key]["icon_url"]

                try:
                    embed.set_author(name=embed_data[key]["name"], url=embed_data[key]["url"], icon_url=embed_data[key]["icon_url"])
                except:
                    pass

        elif key == "footer":
            if embed_data[key]:

                embed_data[key]["icon_url"] = discord.Embed.Empty if "icon_url" not in embed_data[key] else embed_data[key]["icon_url"]

                try:
                    if "timestamp" in embed_data:
                        embed.set_footer(text=f"{embed_data[key]['text']}", icon_url=embed_data[key]["icon_url"])
                    if "timestamp" not in embed_data:
                        embed.set_footer(text=f"Executed by {embed_data[key]['text']},{datetime.datetime.utcnow()}", icon_url=embed_data[key]["icon_url"])

                except:
                    pass

        elif key == "image_url":
            if embed_data[key]:
                try:
                    embed.set_image(url=embed_data[key])
                except:
                    pass

        elif key == "thumbnail_url":
            if embed_data[key]:
                try:
                    embed.set_thumbnail(url=embed_data[key])
                except:
                    pass

    return embed
