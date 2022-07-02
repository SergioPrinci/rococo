import os #local machine functions
import sys #logging
import json #config files
import signal #for handling the SIGINT signal
import random #random functions
import sqlite3
import discord #main library
import logging #logging
import traceback #logging
import requests #updating
from PIL import Image #image manipulation and creation
from sys import platform #multiplatform compatibility
from datetime import datetime #logging
from discord.ext import commands #class of discord.py

"""Initialization and definitions of random variables"""
password = str()
token = str()
botAdminId = str()
prefix = str()
botName = str()
syscalls = dict()
GREY = (70, 70, 70)
RED = (200, 100, 100)

"""Initial back-end configuration"""
VERSION = 2.0
if not os.path.exists(os.path.abspath("Log")): os.mkdir("Log")
logFileName = "Log/" + datetime.now().strftime("%d.%m.%Y_%H-%M-%S") + ".log"
logging.basicConfig(filename = logFileName,
                    filemode = "w",
                    format = "%(asctime)s [%(threadName)s] [%(levelname)s] %(message)s",
                    datefmt = "%d-%m-%Y %H:%M:%S",
                    level = logging.INFO)
log = logging.getLogger('discordBot')
log.addHandler(logging.StreamHandler(sys.stdout))
log.info("Logger started.")

"""Configuration fetching"""
if os.path.exists(os.path.abspath("Data/config.json")):
    log.info("Config file found.")
    try:
        botData = open(os.path.abspath("Data/config.json"), "r", encoding="utf-8")
        jsonConfig = json.load(botData)
        botData.close()
        log.info("Config file loaded.")
    except Exception as e:
        log.fatal("Error while loading config file.\n" + str(e))
        botData.close()
        os.remove(os.path.abspath("Data/config.json"))
        exit()
    """Setting up if no configuration has been found"""
else:
    log.info("Config file not found. Creating one.")
    try:
        botData = open(os.path.abspath("Data/config.json"), "w", encoding="utf-8")
        jsonConfig = {
            "token": input("Write here the discord bot token: "), 
            "password": input("Write here a password for admin commands: "), 
            "botAdminId": input("Write here your Discord ID (you have to use developer mode on Discord): "), 
            "prefix": input("Choose a prefix for your bot: "), 
            "botName": input("Choose the name of the bot on the server: "),
            "autoUpdate": input("Choose if you want to automatically update the bot (T/F): ")
            }
        json.dump(jsonConfig, botData, indent = 2)
        botData.close()
    except Exception as e:
        log.fatal("Error while creating config file.\n" + str(e))
        botData.close()
        os.remove(os.path.abspath("Data/config.json"))
        exit()

"""Setting configuration variables"""
token: str = jsonConfig["token"]
password: str = jsonConfig["password"]
botAdminId: str = jsonConfig["botAdminId"]
prefix: str = jsonConfig["prefix"]
botName: str = jsonConfig["botName"]
autoUpdate: bool = bool(jsonConfig["autoUpdate"])
log.info("Config file parsed correctly.")
log.info("Configuration completed.")

"""Util functions declarations"""
def imageCreation(fileList : list, color : tuple, savename : str):
    imagesPIL = [Image.open(image) for image in fileList]
    widths, heights = zip(*(i.size for i in imagesPIL))
    totalWidth = sum(widths)+140
    maxHeight = max(heights)+60
    newImage = Image.new("RGBA", (totalWidth, maxHeight), color)
    xOffset = 50
    yOffset = 30
    for im in imagesPIL:
        newImage.paste(im,(xOffset,yOffset))
        xOffset += im.size[0]+20
    newImage.save(savename)
    return fileList

async def query(string : str, databaseCursor : sqlite3.Cursor, ctx = None):
    try:
        databaseCursor.execute(string)
        list = databaseCursor.fetchall()
    except sqlite3.Warning as e:
        if e.args[0] == "You can only execute one statement at a time." and ctx != None:
            await ctx.send("Nice try kiddo.")
            log.fatal("Someone tried to execute a SQL injection.")
            log.fatal("Details about the lil fucker:")
            log.fatal("User: " + str(ctx.author))
            log.fatal("ID: " + str(ctx.author.id))
            log.fatal("Message: " + str(ctx.message))
            log.fatal("Command: " + str(ctx.message.content))
            exit()
    if list.__len__() == 0: return None
    elif list.__len__() == 1:
        if list[0].__len__() == 1: return list[0][0]
        else: return [element for temp in list for element in temp]
    elif list.__len__() > 1:
        if list[0].__len__() == 1: return [element for temp in list for element in temp]
        else: return list
    
def parseRarity(rarity : int):
    if rarity == 1: return "✨Shining✨"
    elif rarity == 2: return "🔥Brilliant🔥"
    elif rarity == 3: return "💯Rare💯"
    elif rarity == 4: return "❕Uncommon❕"
    elif rarity == 5: return "👍Common👍"

def parseCondition(condition : int):
    if condition == 5: return "🎉Superb🎉"
    elif condition == 4: return "♣️Fancy♣️"
    elif condition == 3: return "👌Fine👌"
    elif condition == 2: return "🪨Rough🪨"
    elif condition == 1: return "❌Ruined❌"

def updater():
    if autoUpdate:
        """Fetching files from repo"""
        try:
            version = requests.get("https://raw.githubusercontent.com/SergioPrinci/Rococo/master/version.txt")
            changelog = requests.get("https://raw.githubusercontent.com/SergioPrinci/Rococo/master/changelog.txt")
        except Exception as e:
            if version.status_code == 404 or changelog.status_code == 404:
                log.fatal("Couldn't fetch files from repo.\n" + str(e))
            log.fatal("Couldn't fetch files from repo.\n" + str(e))

        """Getting the version"""
        try:
            fetchedVersion = float(version.text.rstrip())
        except Exception as e:
            log.fatal("Couldn't fetch version from repo.\n" + str(e))
            exit()

        """Checking if the bot is updated"""
        if fetchedVersion > VERSION:
            log.info("New version available: " + fetchedVersion)
            log.info("Changelog:" + changelog.text)
            
            """Asking if admin wants to update"""
            if(input("Do you want to update? (y/n) ") == "y"):
                log.info("Updating...")
                
                """Actual update"""
                try:
                    log.info("Removing old core...")
                    os.remove("core.py")
                    newCore = open("core.py", "w")
                    log.info("Getting new core...")
                    coreDownloaded = requests.get("https://raw.githubusercontent.com/SergioPrinci/Rococo/master/core.py")
                    log.info("Installing new core...")
                    if coreDownloaded.status_code == 404: raise Exception("Couldn't fetch core from repo.")
                    newCore.write(coreDownloaded.text)
                    newCore.close()
                except Exception as e:
                    log.fatal("Error while updating.\n" + str(e))
                    exit()

                """Reboot"""
                log.info("Done!")
                log.info("Rebooting...")
                os.system(syscalls["clear"])
                os.system(syscalls["newInstance"])
                exit()

"""Bot configuration"""
bot = commands.Bot(command_prefix=prefix, intents=discord.Intents.default())
log.info("Bot intents set.")
log.info("Bot prefix set.")
bot.remove_command("help")
log.info("Default help command removed.")

"""Users database creation/access"""
if os.path.exists(os.path.abspath("Data/users.sqlite")):
    log.info("User database found.")
    try:
        userDB = sqlite3.connect(os.path.abspath("Data/users.sqlite"))
        userDBCommand = userDB.cursor()
    except Exception as e:
        log.fatal("Error while accessing user database.\n" + str(e))
        exit()
else:
    log.warning("User database not found! Creating database...")
    try:
        userDB = sqlite3.connect(os.path.abspath("Data/users.sqlite"))
        userDBCommand = userDB.cursor()
        userDBCommand.execute("""
            CREATE TABLE Users
            (   
                userid VARCHAR(18) PRIMARY KEY,
                username VARCHAR(32) NOT NULL,
                lastdrop TIME,
                lastgrab TIME
            );
        """)
        log.info("User database created.")
        userDBCommand.execute("""
            CREATE TABLE OwnedCards
            (   
                cardid INTEGER PRIMARY KEY,
                cardname VARCHAR(32) NOT NULL,
                series VARCHAR(32) NOT NULL,
                rarity SMALLINT NOT NULL checks (rarity IN (1, 2, 3, 4, 5)),
                condition SMALLINT NOT NULL checks (condition IN (1, 2, 3, 4, 5)),
                userid VARCHAR(18) REFERENCES Users(userid) ON UPDATE CASCADE ON DELETE SET NULL
            );
        """)
        log.info("Owned cards database created.")
        userDBCommand.execute("""
            CREATE TABLE Wishlist
            (
                cardnumber INTEGER PRIMARY KEY,
                cardname VARCHAR(32) NOT NULL UNIQUE,
                series VARCHAR(32) NOT NULL,
                rarity SMALLINT NOT NULL checks (rarity IN (1, 2, 3, 4, 5)),
                userid VARCHAR(18) REFERENCES Users(userid) ON UPDATE CASCADE ON DELETE SET NULL
            );
        """)
        log.info("Wishlist database created.")
        userDBCommand.execute("""
            CREATE TABLE Inventory
            (
                itemid INTEGER PRIMARY KEY,
                itemname VARCHAR(32) NOT NULL,
                itemquantity SMALLINT NOT NULL,
                userid VARCHAR(18) REFERENCES Users(userid) ON UPDATE CASCADE ON DELETE SET NULL
            );
        """)
        log.info("Inventory database created.")
    except Exception as e:
        log.fatal("Error while creating user database.\n" + str(e))
        exit()

"""Card database access/creation"""
if os.path.exists(os.path.abspath("Data/cards.sqlite")):
    log.info("Card database found.")
    try:
        cardDB = sqlite3.connect(os.path.abspath("Data/cards.sqlite"))
        cardDBCommand = cardDB.cursor()
    except Exception as e:
        log.fatal("Error while accessing card database.\n" + str(e))
        exit()
else:
    log.warning("Card database not found! Creating one...")
    try:
        cardDB = sqlite3.connect(os.path.abspath("Data/cards.sqlite"))
        cardDBCommand = cardDB.cursor()
        cardDBCommand.execute("""
            CREATE TABLE Cards 
            (
                cardnumber INTEGER PRIMARY KEY,
                cardname VARCHAR(32) NOT NULL UNIQUE,
                series VARCHAR(32) NOT NULL,
                rarity SMALLINT NOT NULL checks (rarity IN (1, 2, 3, 4, 5)),
                filename VARCHAR(256) NOT NULL,
                dropped BIGINT NOT NULL DEFAULT 0
            );
        """)
        log.info("Card database created.")
    except Exception as e:
        log.fatal("Error while creating card database.\n" + str(e))
        exit()

"""Server database access/creation"""
if os.path.exists(os.path.abspath("Data/servers.sqlite")):
    log.info("Server database found.")
    try:
        serverDB = sqlite3.connect(os.path.abspath("Data/servers.sqlite"))
        serverDBCommand = serverDB.cursor()
    except Exception as e:
        log.fatal("Error while accessing server database.\n" + str(e))
        exit()
else:
    log.warning("Server database not found! Creating database...")
    try:
        serverDB = sqlite3.connect(os.path.abspath("Data/servers.sqlite"))
        serverDBCommand = serverDB.cursor()
        serverDBCommand.execute("""
            CREATE TABLE Servers
            (
                serverid VARCHAR(18) PRIMARY KEY,
                servername VARCHAR(32) NOT NULL,
                channelid VARCHAR(18) NOT NULL,
                adminid VARCHAR(18)
            );
        """)
        log.info("Server database created.")
    except Exception as e:
        log.fatal("Error while creating server database.\n" + str(e))
        exit()
log.info("All databases loaded correctly.")

"""Searching for folders"""
if not os.path.exists(os.path.abspath("Images")):
    try:
        os.mkdir("Images")
    except Exception as e:
        log.error("Error while creating 'Images' folder: " + str(e))
if not os.path.exists(os.path.abspath("Temp")):
    try:
        os.mkdir("Temp")
    except Exception as e:
        log.error("Error while creating 'Temp' folder: " + str(e))
log.info("Folders found or created.")

"""multiplatform"""
if platform == "linux" or platform == "linux2":
    syscalls = {"clear" : "clear", "newInstance" : "python3 core.py"}
elif platform == "win32":
    syscalls = {"clear" : "cls", "newInstance" : "python core.py"}
log.info("System calls loaded.")

"""Events"""
@bot.event
async def on_ready():
    global mainChannel

    try:
        await bot.user.edit(username=botName)
        log.info("Bot name changed.")
    except Exception as e:
        log.error("Error while changing bot name.\n" + str(e))
    
    log.info("==================================================")
    log.info("Properties of config.json:")
    log.info("Password: " + password)
    log.info("Bot token: " + token)
    log.info("Bot Admin ID: " + botAdminId)
    log.info("Prefix: " + prefix)
    log.info("Bot name: " + botName)
    log.info("==================================================")
    log.info("Server running on " + str(os.cpu_count()) + " threads.")
    log.info("Bot running on " + platform + ".")
    log.info("==================================================")

    serverList = await query("SELECT serverid FROM Servers", serverDBCommand)
    for guild in bot.guilds:
        if serverList == None:
            channel = await guild.create_text_channel(botName)
            mainChannel = bot.get_channel(channel.id)
            await query(f"INSERT INTO Servers VALUES ({guild.id}, '{guild.name}', {mainChannel.id}, {botAdminId})", serverDBCommand)
        else:
            if str(guild.id) in serverList:
                mainChannel = guild.get_channel(int(await query(f"SELECT channelid FROM Servers WHERE serverid = {guild.id}", serverDBCommand)))
                if mainChannel == None:
                    channel = await guild.create_text_channel(botName)
                    mainChannel = bot.get_channel(channel.id)
                    await query(f"INSERT INTO Servers VALUES ({guild.id}, '{guild.name}', {mainChannel.id}, {botAdminId})", serverDBCommand)
            else:
                channel = await guild.create_text_channel(botName)
                mainChannel = bot.get_channel(channel.id)
                await query(f"INSERT INTO Servers VALUES ({guild.id}, '{guild.name}', {mainChannel.id}, {botAdminId})", serverDBCommand)
        await mainChannel.send("**" + botName + "(rococò engine) is online!**")
        await mainChannel.send("checks https://github.com/SergioPrinci/ for more projects!")
    log.info("Connected as " + str(bot.user) + " in " + str(len(bot.guilds)) + " servers (" + "VERSION " + VERSION + ")")

@bot.event
async def on_guild_join(guild):
    global mainChannel
    serverList = await query("SELECT serverid FROM Servers", serverDBCommand)
    if serverList == None:
        channel = await guild.create_text_channel(botName)
        mainChannel = bot.get_channel(channel.id)
        await query(f"INSERT INTO Servers VALUES ({guild.id}, '{guild.name}', {mainChannel.id}, {botAdminId})", serverDBCommand)
    else:
        if str(guild.id) in serverList:
            mainChannel = guild.get_channel(int(await query(f"SELECT channelid FROM Servers WHERE serverid = {guild.id}", serverDBCommand)))
            if mainChannel == None:
                channel = await guild.create_text_channel(botName)
                mainChannel = bot.get_channel(channel.id)
                await query(f"INSERT INTO Servers VALUES ({guild.id}, '{guild.name}', {mainChannel.id}, {botAdminId})", serverDBCommand)
        else:
            channel = await guild.create_text_channel(botName)
            mainChannel = bot.get_channel(channel.id)
            await query(f"INSERT INTO Servers VALUES ({guild.id}, '{guild.name}', {mainChannel.id}, {botAdminId})", serverDBCommand)
    await mainChannel.send("**" + botName + "(rococò engine) is online!**")
    await mainChannel.send("checks https://github.com/SergioPrinci/ for more projects!")

@bot.event
async def on_error(event, *args, **kwargs):
    message = discord.Message()
    if args.__len__() > 0: message = args[0]
    log.fatal("=====================================================================================================")
    log.fatal("ON_ERROR LOGGING STARTS HERE")
    log.fatal("Message that caused the error: " + str(message.content))
    log.fatal("Event: " + str(event))
    log.fatal("Full traceback here: " + traceback.format_exc())
    log.fatal("====================================================================================================")
    exit()

@bot.event
async def on_guild_remove(guild):
    await query(f"DELETE FROM Servers WHERE serverid = {guild.id}", serverDBCommand)

"""commands"""
@bot.command(aliases = ["D", "d", "drop"])
async def dropcard(ctx):
    dropTimeStr = datetime.now().strftime("%H:%M:%S")
    userList = await query("SELECT userid FROM Users", userDBCommand)
    lastDrop = datetime.strptime("00:00:00", "%H:%M:%S")
    message = str()

    if userList == None: 
        await query(f"INSERT INTO Users (userid, username, lastdrop) VALUES ({ctx.author.id}, '{ctx.author.name}', '{dropTimeStr}')", userDBCommand, ctx)
    elif str(ctx.author.id) not in userList:
        await query(f"INSERT INTO Users (userid, username, lastdrop) VALUES ({ctx.author.id}, '{ctx.author.name}', '{dropTimeStr}')", userDBCommand, ctx)
    elif str(ctx.author.id) in userList and await query(f"SELECT lastdrop FROM Users WHERE userid = {ctx.author.id}", userDBCommand, ctx) == None:
        await query(f"UPDATE Users SET lastgrab = '{dropTimeStr}' WHERE userid = {ctx.author.id}", userDBCommand, ctx)
    elif str(ctx.author.id) in userList and str(ctx.author.id) != botAdminId:
        lastDrop = datetime.strptime(await query(f"SELECT lastdrop FROM Users WHERE userid = {ctx.author.id}", userDBCommand, ctx), "%H:%M:%S")

    if (datetime.strptime(dropTimeStr, "%H:%M:%S") - lastDrop).seconds < 300 and str(ctx.author.id) != botAdminId:
        await ctx.send(ctx.author.mention + ", you can drop a card only every 5 minutes.", delete_after = 60)
        return
    else:
        await query(f"UPDATE Users SET lastdrop = '{dropTimeStr}' WHERE userid = {ctx.author.id}", userDBCommand)
    
    cardPathList = await query("SELECT filename FROM Cards ORDER BY cardname", cardDBCommand)
    cardRarity = await query("SELECT rarity FROM Cards ORDER BY cardname", cardDBCommand)
    while True:
        cardsToDrop = random.choices(cardPathList, cardRarity, k = 3)
        if set(cardsToDrop).__len__() == cardsToDrop.__len__(): break
    cardNames = await query(f"SELECT cardname FROM Cards WHERE filename = '{cardsToDrop[0]}' OR filename = '{cardsToDrop[1]}' OR filename = '{cardsToDrop[2]}'", cardDBCommand)
    imageCreation(cardsToDrop, GREY, os.path.abspath("Temp/drop.png"))
    
    """message for wishlists"""
    whoWishlisted = await query(f"SELECT userid FROM Wishlist WHERE cardname = '{cardNames[0]}' OR cardname = '{cardNames[1]}' OR cardname = '{cardNames[2]}'", userDBCommand)
    if whoWishlisted != None:
        if type(whoWishlisted) == str:
            user = await bot.fetch_user(int(whoWishlisted))
            message += user.mention + " "
        else:
            for userId in whoWishlisted:
                user = bot.get_user(int(userId))
                message += user.mention + " "
        message += ", a card from your wishlist is being dropped!"
        await ctx.send(message)
    
    dropEmbed = discord.Embed(title = "Dropped Cards", description = ctx.author.mention + " dropped the following cards!", color = discord.Color.dark_purple())
    dropImage = discord.File(os.path.abspath("Temp/drop.png"), filename="drop.png")
    dropEmbed.set_image(url = "attachment://drop.png")
    drop = await ctx.send(file = dropImage, embed = dropEmbed, delete_after = 120)
    await drop.add_reaction("1️⃣")
    await drop.add_reaction("2️⃣")
    await drop.add_reaction("3️⃣")

    """reaction collector"""
    def check(reaction, user): 
        if str(reaction.emoji) == "1️⃣" and user.id != bot.user.id and reaction.message.id == drop.id: return user
        elif str(reaction.emoji) == "2️⃣" and user.id != bot.user.id and reaction.message.id == drop.id: return user
        elif str(reaction.emoji) == "3️⃣" and user.id != bot.user.id and reaction.message.id == drop.id: return user
    
    """loop for every card"""
    for _ in range(3):
        reaction, user = await bot.wait_for("reaction_add", check = check)
        lastGrabStr = datetime.now().strftime("%H:%M:%S")
        userList = await query("SELECT userid FROM Users", userDBCommand)
        lastGrab = datetime.strptime("00:00:00", "%H:%M:%S")

        if userList == None:
            await query(f"INSERT INTO Users (userid, username, lastgrab) VALUES ({user.id}, '{user.name}', '{lastGrabStr}')", userDBCommand, ctx)
        elif str(user.id) not in userList:
            await query(f"INSERT INTO Users (userid, username, lastgrab) VALUES ({user.id}, '{user.name}', '{lastGrabStr}')", userDBCommand, ctx)
        elif str(user.id) in userList and await query(f"SELECT lastgrab FROM Users WHERE userid = {user.id}", userDBCommand) == None:
            await query(f"UPDATE Users SET lastgrab = '{lastGrabStr}' WHERE userid = {user.id}", userDBCommand)
        elif str(user.id) in userList and user.id != botAdminId:
            lastGrab = datetime.strptime(await query(f"SELECT lastgrab FROM Users WHERE userid = {user.id}", userDBCommand), "%H:%M:%S")

        if (datetime.strptime(lastGrabStr, "%H:%M:%S") - lastGrab).seconds > 300 or str(user.id) == botAdminId:
            if str(reaction.emoji) == "1️⃣":
                cardPath = cardsToDrop[0]
                await drop.clear_reaction("1️⃣")
            elif str(reaction.emoji) == "2️⃣":
                cardPath = cardsToDrop[1]
                await drop.clear_reaction("2️⃣")
            elif str(reaction.emoji) == "3️⃣":
                cardPath = cardsToDrop[2]
                await drop.clear_reaction("3️⃣")

            """card registration"""
            await query(f"UPDATE Cards SET dropped = dropped + 1 WHERE filename = '{cardPath}'", cardDBCommand)
            cardDropped = await query(f"SELECT cardname, series, rarity FROM Cards WHERE filename = '{cardPath}'", cardDBCommand)
            cardCondition = random.choice([1, 1, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 4, 4, 5])
            await query(f"INSERT INTO OwnedCards (cardname, series, rarity, condition, userid) VALUES ('{cardDropped[0]}', '{cardDropped[1]}', {cardDropped[2]}, {cardCondition}, {user.id})", userDBCommand)
            await ctx.send(user.mention + " took **" 
                         + cardDropped[0] + "** from the **" 
                         + cardDropped[1] + "** series! The condition of the card is **" 
                         + parseCondition(cardCondition) + "**.")
            await ctx.send(str(reaction.message.id) + " " + str(drop.id))
            await query(f"UPDATE Users SET lastgrab = '{lastGrabStr}' WHERE userid = {user.id}", userDBCommand)

            """checks for wishlist"""
            if wishlist == cardDropped[0]:
                await query(f"DELETE FROM Wishlist WHERE userid = {user.id} AND cardname = '{cardDropped[0]}'", userDBCommand)
                await ctx.send(user.mention + " has received their wishlisted card!", delete_after = 60)
        else:
            await ctx.send(user.mention + ", you can grab a card only every 5 minutes.", delete_after = 60)
    await drop.delete()

@bot.command(aliases = ["cd"])
async def cooldown(ctx):
    """fetches the cooldowns"""
    actualTime = datetime.strptime(datetime.now().strftime("%H:%M:%S"), "%H:%M:%S")
    lastDrop, lastGrab = [datetime.strptime(element, "%H:%M:%S") for element in await query(f"SELECT lastdrop, lastgrab FROM Users WHERE userid = {ctx.author.id}", userDBCommand)]

    """embed creation and sending"""
    cooldownEmbed = discord.Embed(title = "Cooldown", description = ctx.author.mention + " your cooldown is:", color = discord.Color.dark_purple())
    if lastDrop != None:
        dropCooldown = f"You have to wait {300 - (actualTime - lastDrop).seconds} seconds!" if (actualTime - lastDrop).seconds < 300 else "You can drop cards now!"
        cooldownEmbed.add_field(name = "Drop", value = dropCooldown, inline = True)
    if lastGrab != None:
        grabCooldown = f"You have to wait {300 - (actualTime - lastGrab).seconds} seconds!" if (actualTime - lastGrab).seconds < 300 else "You can grab a card now!"
        cooldownEmbed.add_field(name = "Grab", value = grabCooldown, inline = True)
    if lastGrab == None or lastDrop == None:
        cooldownEmbed.add_field(name = "No Data", value = "You must first drop some cards!", inline = True)
    await ctx.send(embed = cooldownEmbed)


@bot.command(aliases = ["col"])
async def collection(ctx, mention: discord.Member=None):
    user = ctx.author if mention == None else mention

    """fetches user collection"""
    userCollection = await query(f"SELECT cardid, cardname, series, rarity, condition FROM OwnedCards WHERE userid = {user.id}", userDBCommand)

    """embed creation and sending"""
    collectionEmbed = discord.Embed(title = f"{user.name}'s collection", color = discord.Color.dark_purple())

    if userCollection == None:
        collectionEmbed.add_field(name = "Empty", value =  f"{user.name} has no cards yet!", inline = True)
    else:
        if type(userCollection[0]) == tuple:
            for card in userCollection:
                collectionEmbed.add_field(name = f"{card[1]} - {card[2]}", value = f"Rarity: '{parseRarity(card[3])}'\nCondition: '{parseCondition(card[4])}'\nID: {card[0]}", inline = True)
        else:
            collectionEmbed.add_field(name = f"{userCollection[1]} - {userCollection[2]}", value = f"Rarity: '{parseRarity(userCollection[3])}'\nCondition: '{parseCondition(userCollection[4])}'\nID: {userCollection[0]}", inline = True)

    await ctx.send(embed = collectionEmbed)

    
@bot.command(aliases = ["W", "wl", "w"])
async def wishlist(ctx, mention: discord.Member = None):
    user = ctx.author if mention == None else mention

    """fetches user wishlist"""
    userWishlist = await query(f"SELECT cardname, series, rarity FROM Wishlist WHERE userid = {user.id}", userDBCommand)

    """embed creation and sending"""
    wishlistEmbed = discord.Embed(title = f"{user.name}'s wishlist", color = discord.Color.dark_purple())

    if userWishlist == None:
        wishlistEmbed.add_field(name = "Empty", value =  f"{user.name} has never wished for a card!", inline = True)
    else:
        if type(userWishlist[0]) == tuple:
            for card in userWishlist:
                wishlistEmbed.add_field(name = f"{card[0]} - {card[1]}", value = f"Rarity: {parseRarity(card[2])}", inline = False)
        else:
            wishlistEmbed.add_field(name = f"{userWishlist[0]} - {userWishlist[1]}", value = f"Rarity: {parseRarity(userWishlist[2])}", inline = False)

    await ctx.send(embed = wishlistEmbed)


@bot.command(aliases = ["addwishlist", "wa", "wla"])
async def wishlistadd(ctx, card):
    """fetches card list"""
    temp = await query("SELECT cardname FROM Cards", cardDBCommand)
    if temp == None:
        log.fatal("Error while reading from database: no cards found!")
        exit()
    else:
        cardList = [i.lower() for i in temp]

    """fetches wishlist of user"""
    temp = await query(f"SELECT cardname FROM Wishlist WHERE userid = {ctx.author.id}", userDBCommand)
    if temp == None:
        currentWishlist = None
    else:
        if type(temp) == str:
            currentWishlist = [temp.lower()]
        else:
            currentWishlist = [i.lower() for i in temp]
    cardLower = card.lower()

    """checks if card is in card list"""	
    if cardLower in cardList:
        """checks if wishlist is empty"""
        if currentWishlist == None:
            cardToAdd = await query(f"SELECT cardnumber, cardname, series, rarity FROM Cards WHERE cardname = '{card}'", cardDBCommand, ctx)
            await query(f"INSERT INTO Wishlist (cardnumber, cardname, series, rarity, userid) VALUES ({cardToAdd[0]}, '{cardToAdd[1]}', '{cardToAdd[2]}', {cardToAdd[3]}, {ctx.author.id})", userDBCommand)
        else: 
            """checks if card is already in wishlist"""
            if cardLower in currentWishlist:
                await ctx.send(ctx.author.mention + ", you already wished for this card!", delete_after = 60)
                return
            else:
                cardToAdd = await query(f"SELECT cardnumber, cardname, series, rarity FROM Cards WHERE cardname = '{card}'", cardDBCommand, ctx)
                await query(f"INSERT INTO Wishlist (cardnumber, cardname, series, rarity, userid) VALUES ({cardToAdd[0]}, '{cardToAdd[1]}', '{cardToAdd[2]}', {cardToAdd[3]}, {ctx.author.id})", userDBCommand)
        await ctx.send(ctx.author.mention + ", you've added **" + card + "** to your wishlist!")
    else:
        await ctx.send(ctx.author.mention + ", that card doesn't exist! Check if you have spelled the name correctly.", delete_after = 60)


@bot.command(aliases = ["removewishlist", "wr", "wlr"])
async def wishlistremove(ctx, card):
    """fetches card list"""
    temp = await query("SELECT cardname FROM Cards", cardDBCommand)
    if temp == None:
        log.fatal("Error while reading from database: no cards found!")
        exit()
    else:
        cardList = [i.lower() for i in temp]

    """fetches wishlist of user"""
    temp = await query(f"SELECT cardname FROM Wishlist WHERE userid = {ctx.author.id}", userDBCommand)
    if temp == None:
        currentWishlist = None
    else:
        if type(temp) == str:
            currentWishlist = [temp.lower()]
        else:
            currentWishlist = [i.lower() for i in temp]
    cardLower = card.lower()

    """checks if card is in card list"""
    if cardLower in cardList:
        """checks if wishlist is empty"""
        if currentWishlist == None:
            await ctx.send(ctx.author.mention + ", you don't have any cards in your wishlist!", delete_after = 60)
        else:
            """checks if card is in wishlist"""
            if cardLower not in currentWishlist:
                await ctx.send(ctx.author.mention + ", you haven't wished for this card!", delete_after = 60)
                return
            else:
                await query(f"DELETE FROM Wishlist WHERE cardname = '{card}' AND userid = {ctx.author.id}", userDBCommand, ctx)
                await ctx.send(ctx.author.mention + ", you've removed **" + card + "** from your wishlist!")
    else:
        await ctx.send(ctx.author.mention + ", that card doesn't exist! Check if you have spelled the name correctly.", delete_after = 60)

@bot.command(aliases = ["b", "br"])
async def burn(ctx, card):
    allFlag = False

    """fetches card list"""
    temp = await query("SELECT cardname FROM Cards", cardDBCommand)
    if temp == None:
        log.fatal("Error while reading from database: no cards found!")
        exit()
    else:
        cardList = [i.lower() for i in temp]

    """fetches cards owned by user"""
    temp = await query(f"SELECT cardname FROM OwnedCards WHERE userid = {ctx.author.id}", userDBCommand)
    if temp == None:
        collection = None
    else:
        if type(temp) == str:
            collection = [temp.lower()]
        else:
            collection = [i.lower() for i in temp]
    cardLower = card.lower()

    """checks if user wants to burn all cards"""
    if card == "all":
        """checks if user's collection is empty"""
        if collection == None:
            await ctx.send(ctx.author.mention + ", you don't have any cards to burn!", delete_after = 60)
            return
        else:
            message = await ctx.send(ctx.author.mention + ", are you sure you want to burn all of your cards?", delete_after = 60)
            allFlag = True
    else:
        """checks if card is in card list"""
        if cardLower in cardList:
            """checks if user's collection is empty"""
            if collection == None:
                await ctx.send(ctx.author.mention + ", you don't have any cards to burn!", delete_after = 60)
                return
            else:
                """checks if card is in collection"""
                if cardLower not in collection:
                    await ctx.send(ctx.author.mention + ", you don't own this card!", delete_after = 60)
                    return
                message = await ctx.send(ctx.author.mention + ", are you sure you want to burn this card?", delete_after = 60)
        else:
            await ctx.send(ctx.author.mention + ", that card doesn't exist! Check if you have spelled the name correctly.", delete_after = 60)
            return
    
    """adding reaction to message"""
    await message.add_reaction("✅")
    await message.add_reaction("❌")

    """reaction collector"""
    def check(reaction, user): 
        if str(reaction.emoji) == "✅" and user.id != bot.user.id and reaction.message.id == message.id: return user
        elif str(reaction.emoji) == "❌" and user.id != bot.user.id and reaction.message.id == message.id: return user
    
    """waiting for reaction"""
    reaction, user = await bot.wait_for("reaction_add", check = check)
    if str(reaction.emoji) == "✅" and user.id == ctx.author.id:
        if allFlag:
            await query(f"DELETE FROM OwnedCards WHERE userid = {ctx.author.id}", userDBCommand)
            await ctx.send(ctx.author.mention + ", you've burned all of your cards!")
        else:
            await query(f"DELETE FROM OwnedCards WHERE cardname = '{card}' AND userid = {ctx.author.id}", userDBCommand, ctx)
            await ctx.send(ctx.author.mention + ", you've burned **" + card + "**!")
    elif str(reaction.emoji) == "❌" and user.id == ctx.author.id:
        await ctx.send(ctx.author.mention + ", burn cancelled!", delete_after = 60)
    
    """reaction removing"""
    await message.clear_reactions()

"""pretty vulnerable one, be careful"""
@bot.command(aliases = ["S, s, se, search, L, l, lu, lo"])
async def lookup(ctx, args):
    """first line of defense against sql injection"""
    args = args.lower().replace("'", "''").replace("-", "").replace("\\", "").replace("|", "").replace("/", "")

    """another check for sql injection"""
    if args.count("'") > 2:
        await ctx.send(ctx.author.mention + ", no cards found with that parameter!", delete_after = 60)
        return
    
    """fetches card list with the chosen parameter"""
    possibleCards = await query(f"SELECT * FROM Cards WHERE cardname LIKE '%{args}%'", cardDBCommand, ctx)
    searchList = str()

    """checks if there are any cards matching the search await query"""
    if possibleCards == None:
        await ctx.send(ctx.author.mention + ", no cards found with that parameter!", delete_after = 60)
        return
    elif type(possibleCards[0]) == tuple:
        for card in possibleCards:
            """appends the results to a string"""
            searchList += f"**{card[1]} • {card[2]} • {parseRarity(card[3])}**\n"
        """creates embed"""
        searchEmbed = discord.Embed(title = "Search results", description = searchList, color = discord.Color.dark_gold())
        await ctx.send(file = None, embed = searchEmbed, delete_after = 120)
    else:
        card = possibleCards
        cardPath = card[4]
        lookupEmbed = discord.Embed(title = "Card look-up", color = discord.Color.dark_magenta())
        lookupImage = discord.File(os.path.abspath(cardPath), filename="card.png")
        lookupEmbed.set_image(url = "attachment://card.png")
        lookupEmbed.add_field(name = "Name", value = card[1], inline = False)
        lookupEmbed.add_field(name = "Series", value = card[2], inline = False)
        lookupEmbed.add_field(name = "Rarity", value = parseRarity(card[3]), inline = False)
        lookupEmbed.add_field(name = "Times dropped", value = card[5], inline = False)
        await ctx.send(file = lookupImage, embed = lookupEmbed, delete_after = 120)

"""
@bot.command(aliases = ["T", "t", "tr"])
async def trade(ctx, mention: discord.Member, cardID1: int, cardID2: int):


@bot.command(aliases = ["helpbot", "hb", "h"])
async def help(ctx): 
    

@bot.command(aliases = ["stop", "shutdown"])
async def maintenance(ctx, passwordInput: str):
"""

@bot.command(aliases = ["reboot"])
async def restart(ctx, passwordInput: str):
    if passwordInput == password:
        await ctx.message.delete()
        await ctx.send("Rebooting...")
        os.system(syscalls["clear"])
        os.system(syscalls["newInstance"])
        exit()

if __name__ == "__main__":
    bot.run(token)
    signal.signal(signal.SIGINT, log.fatal("SIGINT received, stopping program."))