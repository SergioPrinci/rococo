import asyncio
from distutils import util
import traceback #logging
import lxml.etree as ET #writing xml user database
import untangle #xml database
import os #local machine functions
import time #timer
import discord #main library
import random #random functions
import datetime
from discord.ext import commands #class of discord.py
from PIL import Image #image manipulation and creation

'''declarations'''
VERSION = "1.3.5" #version of the bot
answersdrop = [line.strip() for line in open("Sources\\dropanswers.txt", "r", newline="\n")] #add string/strings with what the bot needs to say on a drop
factlist = [line.strip() for line in open("Sources\\facts.txt", "r", newline="\n")] #add string/strings for facts
log = open("log.txt", "w", buffering=1, newline="\n", encoding="utf-8") #opens the log file
botdata = open("Sources\\botdata.txt", "r", encoding="utf-8") #opens file with token, password and the id of the manager of the bot
password: int = int(botdata.readline().replace("password: ", "")) #password for resets
token: str = botdata.readline().replace("token: ", "").strip("\n") #discord bot token
botadminid: int = int(botdata.readline().replace("adminid: ", "")) #bot manager
prefix: str = botdata.readline().replace("prefix: ", "").strip("\n") #bot manager
cardgame: bool = bool(util.strtobool(botdata.readline().replace("cardgame: ", "").strip("\n"))) #card games flag
botname: str = botdata.readline().replace("botname: ", "").strip("\n") #the bot name
def printproperties():
    print("Properties of botdata.txt")
    print("Password: " + str(password))
    print("Bot token: " + token)
    print("Bot Admin ID: " + str(botadminid))
    print("Prefix: " + prefix)
    print("Cardgame Flag: " + str(cardgame))
    print("Bot name: " + botname)
printproperties()
GREY = (70, 70, 70) #color grey in RGB
RED = (200, 100, 100) #color red in RGB
intents = discord.Intents(messages=True, guilds=True, members=True)
bot = commands.Bot(command_prefix=prefix) #command prefix and client object declaration
bot.remove_command('help')

'''events'''
@bot.event
async def on_ready(): #when the bot connects to the server and it's ready
    global mainchannel
    os.system("cls")
    await bot.user.edit(username=botname)
    print('Connected as ' + str(bot.user) + ' in ' + str(len(bot.guilds)) + ' servers||||' + 'VERSION ' + VERSION)
    for guild in bot.guilds:
        mainchannel = discord.utils.get(guild.text_channels, name=botname)
        if mainchannel is None:
            channel = await guild.create_text_channel(botname)
            mainchannel = bot.get_channel(channel.id)
        await mainchannel.send("**" + botname + "(rococò engine) is online!**")
    log.write("Bot started at " + str(datetime.datetime.now()) + "\n")
    log.flush()

@bot.event
async def on_guild_join(guild): #when the bot joins a new guild
    global mainchannel
    print("New guild joined! Guild name: " + guild.name)
    log.write("New guild joined! Guild name: " + guild.name + "\n")
    mainchannel = discord.utils.get(guild.text_channels, name=botname)
    if mainchannel is None:
        channel = await guild.create_text_channel(botname)
        mainchannel = bot.get_channel(channel.id)
        await mainchannel.send("Write '" + prefix + "setup' with the mention of the lowest mod role to finish the setup of the bot in this server")

@bot.event
async def on_error(event, *args, **kwargs):
    message = args[0]
    log.write("=====================================================================================================\nON_ERROR LOGGING STARTS HERE\n")
    log.write(traceback.format_exc())
    log.write(str(message) + '\n')
    log.write(str(datetime.datetime.now()) + '\n')
    log.write('====================================================================================================\n')
    log.flush()

@bot.event
async def on_command_error(ctx, error):
    log.write("=====================================================================================================\nON_COMMAND_ERROR LOGGING STARTS HERE\n")
    log.write(ctx.message.content + " " + str(error) + '\n')
    log.write(str(datetime.datetime.now()) + '\n')
    log.write('====================================================================================================\n')
    log.flush()
    await help(ctx)

@bot.event
async def on_guild_remove(guild):
    serverroot = ET.parse("Sources\\ServerDatabase.xml", ET.XMLParser(remove_blank_text=True)).getroot()
    serverbranch = serverroot.find("servers")
    for server in serverbranch.findall("server"):
        if server.attrib["ID"] == guild.id:
            serverbranch.remove(server)
    serverbranch.attrib["nservers"] = str(int(serverbranch.attrib["nservers"])-1)

@bot.event
async def on_voice_state_update(member, before, after): #when a member has his voice state updated
    if after.afk and "[AFK]" not in member.display_name and len(member.display_name) < 27:
        await member.edit(reason="AFK", nick = member.display_name + "[AFK]")
    elif before.afk:
        await member.edit(reason="No more AFK", nick = member.display_name.rstrip("[AFK]"))

'''commands'''
@bot.command(aliases = ['coc'])
async def cock(ctx):
    await ctx.send("n i c e " + str(round(bot.latency, 2)*100) + "ms")

@bot.command(aliases = ['firstsetup', 'fs'])
async def setup(ctx, mention: discord.Role):
    serverroot = ET.parse("Sources\\ServerDatabase.xml", ET.XMLParser(remove_blank_text=True)).getroot()
    serverbranch = serverroot.find("servers")
    start = time.time()
    serverbranch.attrib["nservers"] = str(int(serverbranch.attrib["nservers"])+1)
    foundFlag = False
    setupFlag = False
    for server in serverbranch.findall("server"):
        if server.attrib["ID"] == str(ctx.guild.id):
            foundFlag = True
            if server.find("setup").text == "True":
                setupFlag = True

    if foundFlag and setupFlag:
        await ctx.send("This server has already been setup.")
    else:
        newserverbranch = ET.Element("server")
        newserverbranch.attrib["ID"] = str(ctx.guild.id)
        newservername = ET.SubElement(newserverbranch, "name")
        newservername.text = str(ctx.guild.name)
        newserversetup = ET.SubElement(newserverbranch, "setup")
        newserversetup.text = str(True)
        newservernmembers = ET.SubElement(newserverbranch, "nmembers")
        newservernmembers.text = str(len(ctx.guild.members))
        newservermainchannelid = ET.SubElement(newserverbranch, "mainchannelid")
        newservermainchannelid.text = str(mainchannel.id)
        newserveradminroleid = ET.SubElement(newserverbranch, "adminroleid")
        newserveradminroleid.text = str(mention.id)
        serverbranch.append(newserverbranch)
        newroot = ET.tostring(serverroot, encoding="UTF-8", pretty_print=True)
        open("Sources\\ServerDatabase.xml", "wb").write(newroot)
        await ctx.send("Setup completed! Enjoy the bot!")

    print('Used successfully the command setup from "' + str(ctx.author) + '"(' + ctx.author.top_role.name + '), in the server ' + ctx.guild.name + ' in ' + str(round(time.time()-start, 2)) + ' seconds.') #console log
    log.write('Used successfully the command setup from "' + str(ctx.author) + '"(' + ctx.author.top_role.name + '), in the server ' + ctx.guild.name + ' in ' + str(round(time.time()-start, 2)) + ' seconds.\n')
    log.flush()

@bot.command(aliases = ['f', 'fact']) 
async def facts(ctx):
    start = time.time()
    if factlist: await ctx.send(random.choice(factlist))
    else: await ctx.send("No facts found! Tell the admin to put facts in the bot!")
    print('Used successfully the command facts from "' + str(ctx.author) + '"(' + ctx.author.top_role.name + '), in the server ' + ctx.guild.name + ' in ' + str(round(time.time()-start, 2)) + ' seconds.') #console log
    log.write('Used successfully the command facts from "' + str(ctx.author) + '"(' + ctx.author.top_role.name + '), in the server ' + ctx.guild.name + ' in ' + str(round(time.time()-start, 2)) + ' seconds.\n')
    log.flush()

@bot.command(aliases = ['D', 'd', 'drop'])
async def dropcard(ctx): #cards dropping
    if cardgame: 
        carddata = untangle.parse("Sources\\CardDatabase.xml")
        if carddata is not None: cardrarity = [int(cards.rarityweight.cdata) for cards in carddata.root.card]
        dropFlag = False
        foundFlag = False
        start = time.time() #starting timer

        root = ET.parse("Sources\\UsersDatabase.xml", ET.XMLParser(remove_blank_text=True)).getroot()
        usersbranch = root.find("users")
        for users in usersbranch.findall("user"):
            if users.attrib["ID"] == str(ctx.author.id):
                foundFlag = True
                if time.time()-int(users.find("lastdrop").text) > 300:
                    dropFlag = True
        if not foundFlag:
            dropFlag = True
        
        if dropFlag:
            imagetodrop = imagecreation(3, GREY, "Temp\\temp.png", cardrarity) #list of paths of images dropped for parsing database info

            cardsdropped=[0, 0, 0] #string parsing
            for i in range(len(imagetodrop)):
                cardsdropped[i] = imagetodrop[i].replace('.png', '')

            drop = await ctx.send(file=discord.File("Temp\\temp.png"), content=ctx.author.mention + ' ' + random.choice(answersdrop)) #memorizing the Message class in drop for after
            await drop.add_reaction('1️⃣') #adding reactions to the drop message
            await drop.add_reaction('2️⃣')
            await drop.add_reaction('3️⃣')

            fracture = time.time() #now the time that takes the machine to do the work is partially finished, we don't want to measure the time that the user needs to select a card
            
            def checkreactions(reaction, user): #function to get the reaction used and the user who used it 
                if (user == ctx.message.author and str(reaction.emoji) == '1️⃣'): return user
                elif (user == ctx.message.author and str(reaction.emoji) == '2️⃣'): return user
                elif (user == ctx.message.author and str(reaction.emoji) == '3️⃣'): return user

            reaction, user = await bot.wait_for('reaction_add',check=checkreactions) #using the function to check on the reactions under drop message
            
            fracturestart = time.time() #another timer for another piece of code
            if str(reaction) == '1️⃣': #determining which card the user has chosen to pick
                await drop.edit(content="*" + drop.content + "*" + " **\nThese cards are no more available**")
                await ctx.send(user.mention + " took the card " + carddata.root.card[int(cardsdropped[0])-1].name.cdata)
                carddroppedindex = 0
            elif str(reaction) == '2️⃣':
                await drop.edit(content="*" + drop.content + "*" + " **\nThese cards are no more available**")
                await ctx.send(user.mention + " took the card " + carddata.root.card[int(cardsdropped[1])-1].name.cdata)
                carddroppedindex = 1
            elif str(reaction) == '3️⃣':
                await drop.edit(content="*" + drop.content + "*" + " **\nThese cards are no more available**")
                await ctx.send(user.mention + " took the card " + carddata.root.card[int(cardsdropped[2])-1].name.cdata)
                carddroppedindex = 2

            foundFlag = False
            for users in usersbranch.findall("user"):
                if users.attrib["ID"] == str(ctx.author.id):
                    users.find("lastdrop").text = str(round(time.time()))
                    tempcardliststr = users.find("cardlist").text
                    tempcardlist = tempcardliststr.split(",")
                    tempcardlist.append(str(cardsdropped[carddroppedindex]))
                    tempcardliststr = ",".join(tempcardlist)
                    users.find("cardlist").text = tempcardliststr
                    foundFlag = True
            if not foundFlag:
                newuserbranch = ET.Element("user")
                newuserbranch.attrib["ID"] = str(ctx.author.id)
                newlastdrop = ET.SubElement(newuserbranch, "lastdrop")
                newlastdrop.text = str(round(time.time()))
                newcardlist = ET.SubElement(newuserbranch, "cardlist") 
                newcardlist.text = str(cardsdropped[carddroppedindex])
                usersbranch.append(newuserbranch)
            newroot = ET.tostring(root, encoding="UTF-8", pretty_print=True)
            open("Sources\\UsersDatabase.xml", "wb").write(newroot)
            print('Used successfully the command drop from "' + str(ctx.author) + '"(' + ctx.author.top_role.name + '), in the server ' + ctx.guild.name + ' in ' + str(round((fracture-start)+(time.time()-fracturestart), 2)) + ' seconds.') #console log
            log.write('Used successfully the command drop from "' + str(ctx.author) + '"(' + ctx.author.top_role.name + '), in the server ' + ctx.guild.name + ' in ' + str(round((fracture-start)+(time.time()-fracturestart), 2)) + ' seconds.\n')
        else:
            await ctx.send("You got to wait 5 minutes between drops!")
            print('Used successfully the command drop from "' + str(ctx.author) + '"(' + ctx.author.top_role.name + '), in the server ' + ctx.guild.name + ' in ' + str(round(time.time()-start, 2)) + ' seconds.') #console log
            log.write('Used successfully the command drop from "' + str(ctx.author) + '"(' + ctx.author.top_role.name + '), in the server ' + ctx.guild.name + ' in ' + str(round(time.time()-start, 2)) + ' seconds.\n')
        log.flush()
    else:
        await ctx.send("Tell the bot admin to add the function by botdata.txt!")

@bot.command(aliases = ['play', 'p', 'P'])
async def playgame(ctx, versus: discord.Member, turni: int=1): #playing the cards, default turns is 1
    if cardgame:
        start = time.time() #same timer to measure performance
        carddata = untangle.parse("Sources\\CardDatabase.xml")
        if carddata is not None: cardrarity = [int(cards.rarityweight.cdata) for cards in carddata.root.card]
        if turni == 1: #only one turn
            os.chdir("Images") #changing directory for image search
            firstplayer = ctx.author.mention #memorizing the first player who sent the message
            secondplayer = versus #memorizing the mention of the second player
            imagelist = os.listdir() #creating an array for the paths of the images

            cardtoplay = random.choice(imagelist) #gets random photo paths
            cardplayed = cardtoplay.replace('.png', '') #string parsing
            value1 = int(carddata.root.card[int(cardplayed)].value.cdata) #takes the value from the xml file
            await ctx.send(file=discord.File(cardtoplay), content=firstplayer + ' ,you played a card with value '+ str(value1)) #message with card and the value of it

            cardtoplay = random.choice(imagelist) #same as up
            cardplayed = cardtoplay.replace('.png', '')
            value2 = int(carddata.root.card[int(cardplayed)].value.cdata)
            await ctx.send(file=discord.File(cardtoplay), content=secondplayer + ' ,you played a card with value '+ str(value2))
            
            os.chdir("..") #exiting the branch

            if value1 < value2: #checking who won based on value of the card
                await ctx.send(secondplayer + ' won! \n')
            elif value2 < value1:
                await ctx.send(firstplayer + ' won! \n')
            elif value2 == value1:
                await ctx.send(firstplayer + ' and ' + secondplayer + ' got a draw!')
            else:
                await ctx.send('WTF just happened.')
        
        elif turni > 1 and turni < 6: #if the round quantity is over 1, this happens
            cardstoplay1 = imagecreation(turni, RED, "Temp\\temp1.png", cardrarity)
            cardstoplay2 = imagecreation(turni, RED, "Temp\\temp2.png", cardrarity)
            
            value1 = value2 = 0

            for i in range(turni):
                firstplayer = ctx.author.mention #saving the player who used the command
                secondplayer = versus #saving the player mentioned by firstplayer

                cardplayed1 = cardstoplay1[i].replace('.png', '') #string parsing
                cardplayed2 = cardstoplay2[i].replace('.png', '')

                value1 += int(carddata.root.card[int(cardplayed1)].cdata)
                value2 += int(carddata.root.card[int(cardplayed2)].cdata)

            await ctx.send(file=discord.File("Temp\\temp1.png"), content=firstplayer + ' , you played cards with a total value '+ str(value1)) #loading the cards in a message
            await ctx.send(file=discord.File("Temp\\temp2.png"), content=secondplayer + ' , you played cards with a total value '+ str(value2))

            if value1 < value2:
                await ctx.send('Congrats ' + secondplayer + ' !, You won!') #checking the winner
            elif value2 < value1:
                await ctx.send('History is written by winners. And now ' + firstplayer + ' will write that ' + secondplayer + ' has been defeated.')
            else:
                await ctx.send(firstplayer + ' and ' + secondplayer + ' got a draw!')

        else:
            await ctx.send("Too many rounds!") #with number of rounds over 5
        
        print('Used successfully the command play from "' + str(ctx.author) + '"(' + ctx.author.top_role.name + '), in the server ' + ctx.guild.name + ' in ' + str(round(time.time()-start, 2)) + ' seconds.') #console log
        log.write('Used successfully the command play from "' + str(ctx.author) + '"(' + ctx.author.top_role.name + '), in the server ' + ctx.guild.name + ' in ' + str(round(time.time()-start, 2)) + ' seconds.\n')
        log.flush()
    else:
        await ctx.send("Tell the bot admin to add the function by botdata.txt!")

@bot.command(aliases = ['col'])
async def collection(ctx, mention: discord.Member=None): #outputs the list of cards possessed by the user in a embed message
    if cardgame:
        start = time.time()
        userdata = untangle.parse("Sources\\UsersDatabase.xml")
        carddata = untangle.parse("Sources\\CardDatabase.xml")
        useridlist = [elements["ID"] for elements in userdata.root.users.user]
        if mention is not None and str(mention.id) not in useridlist:
            await ctx.send("The user never took a card from the bot!")
        else: 
            for users in userdata.root.users.user:
                if mention is None:
                    if users["ID"] == str(ctx.author.id):
                        strcardlist = str(users.cardlist.cdata)
                        title = ctx.author.name + "'s collection"
                else:
                    if users["ID"] == str(mention.id):
                        strcardlist = str(users.cardlist.cdata)
                        title = mention.name + "'s collection"
            
            tempcardlist = set(map(int, strcardlist.split(",")))
            cardlist = sorted(tempcardlist)
            if len(cardlist) == int(carddata.root["ncards"]):
                title = "⭐" + title + "⭐"
            embed = discord.Embed(title=title)
            embed.add_field(name="Number of cards", value="```You have " + str(len(cardlist)) + " cards in your collection.```", inline=False)
            for cardid in cardlist:
                embed.add_field(name="\u200b", value="Card ID: " + str(cardid) + "\t" + str(carddata.root.card[int(cardid)-1].name.cdata), inline=False)
            await ctx.send(embed=embed)
        print('Used successfully the command collection from "' + str(ctx.author) + '"(' + ctx.author.top_role.name + '), in the server ' + ctx.guild.name + ' in ' + str(round(time.time()-start, 2)) + ' seconds.')
        log.write('Used successfully the command collection from "' + str(ctx.author) + '"(' + ctx.author.top_role.name + '), in the server ' + ctx.guild.name + ' in ' + str(round(time.time()-start, 2)) + ' seconds.\n')
        log.flush()
    else:
        await ctx.send("Tell the bot admin to add the function by botdata.txt!")

@bot.command(aliases = ['clearchat', 'cl'])
async def clear(ctx, amount: int = 5): #command to clear the chat by amount
    serverroot = ET.parse("Sources\\ServerDatabase.xml", ET.XMLParser(remove_blank_text=True)).getroot()
    serverbranch = serverroot.find("servers")
    start = time.time()
    rolelist = [int(server.find("adminroleid").text) for server in serverbranch.findall("server")]
    if ctx.author.top_role.id in rolelist:
        await ctx.channel.purge(limit=amount+1)
    print('Used successfully the command clear from "' + str(ctx.author) + '"(' + ctx.author.top_role.name + '), in the server ' + ctx.guild.name + ' in ' + str(round(time.time()-start, 2)) + ' seconds.') #console log
    log.write('Used successfully the command clear from "' + str(ctx.author) + '"(' + ctx.author.top_role.name + '), in the server ' + ctx.guild.name + ' in ' + str(round(time.time()-start, 2)) + ' seconds.\n')
    log.flush()

@bot.command(aliases = ['helpbot', 'hb', 'h'])
async def help(ctx): #command for help
    start = time.time()
    embed = discord.Embed(title="Commands")
    embed.add_field(name= prefix + "setup", value="Starts the setup for the essentials functions of the bot -Syntax: " + prefix + "setup", inline=False)
    embed.add_field(name= prefix + "drop(alias rd)", value="Drops 3 casual cards -Syntax: " + prefix + "drop", inline=False)
    embed.add_field(name= prefix + "play(alias rp)", value="Card game based on cards value -Syntax: " + prefix + "play mention rounds(default 1, max 5)", inline=False)
    embed.add_field(name= prefix + "clear(alias rc)", value="Clears the chat by n times -Syntax: " + prefix + "clear numberofmessages(default 5)", inline=False)
    embed.add_field(name= prefix + "help(alias rh)", value="Shows this page -Syntax: " + prefix + "help", inline=False)
    embed.add_field(name= prefix + "collection(alias rcol)", value="Outputs the card possessed by the user -Syntax: " + prefix + "collection mention", inline=False)
    embed.add_field(name= prefix + "facts(alias rf)", value="Outputs a random fact -Syntax: " + prefix + "facts", inline=False)
    embed.add_field(name= prefix + "maintenance(alias rstop)", value="Stops the bot -Syntax: " + prefix + "stop password", inline=False)
    embed.add_field(name= prefix + "restart(alias rreboot)", value="Reboot the drop(helpful for code editing) -Syntax: " + prefix + "restart password", inline=False)
    embed.add_field(name= prefix + "afk", value="Send the user who called the command in the AFK channel -Syntax: " + prefix + "afk", inline=False)
    await ctx.send(embed=embed)
    print('Used successfully the command help from "' + str(ctx.author) + '"(' + ctx.author.top_role.name + '), in the server ' + ctx.guild.name + ' in ' + str(round(time.time()-start, 2)) + ' seconds.')
    log.write('Used successfully the command help from "' + str(ctx.author) + '"(' + ctx.author.top_role.name + '), in the server ' + ctx.guild.name + ' in ' + str(round(time.time()-start, 2)) + ' seconds.\n')
    log.flush()

@bot.command(aliases = ['stop', 'shutdown'])
async def maintenance(ctx, passwordinput: str):
    await ctx.channel.purge(limit=1)
    if int(passwordinput) == password and ctx.author.id == botadminid:
        await ctx.send("The bot is stopping.")
        print(str(ctx.author) + " has shutdown the bot from the server " + ctx.guild.name)
        log.write(str(ctx.author) + " has shutdown the bot from the server " + ctx.guild.name + "\n")
        log.write("Goodnight :D")
        time.sleep(5)
        exit()
    else: 
        print(str(ctx.author) + " has tried to shutdown the bot from the server " + ctx.guild.name + " with the ID being " + str(ctx.author.id))
        log.write(str(ctx.author) + " has tried to shutdown the bot from the server " + ctx.guild.name + " with the ID being " + str(ctx.author.id) + "\n")
    log.flush()

@bot.command(aliases = ['reboot'])
async def restart(ctx, passwordinput: str):
    await ctx.channel.purge(limit=1)
    if int(passwordinput) == password and ctx.author.id == botadminid:
        await ctx.send("The bot is rebooting, wait some seconds...")
        print(str(ctx.author) + " has rebooted the bot from the server " + ctx.guild.name)
        log.write(str(ctx.author) + " has rebooted the bot from the server " + ctx.guild.name)
        print("Rebooting...")
        os.system("bot.py")
        exit()
    else:
        print(str(ctx.author) + " has tried to reboot the bot from the server " + ctx.guild.name + " with the ID being " + str(ctx.author.id))
        log.write(str(ctx.author) + " has tried to reboot the bot from the server " + ctx.guild.name + " with the ID being " + str(ctx.author.id) + "\n")
    log.flush()

@bot.command()
async def afk(ctx, mention: discord.Member=None):
    if mention is None:
        await ctx.send(ctx.author.nick + " has gone AFK")
        await ctx.author.move_to(bot.get_channel(ctx.guild.afk_channel.id))
        print(str(ctx.author) + " has gone AFK in the server " + ctx.guild.name)
        log.write(str(ctx.author) + "  in the server " + ctx.guild.name + "\n")
        log.flush()
    else:
        await ctx.send(mention.nick + " has gone AFK")
        await mention.move_to(bot.get_channel(ctx.guild.afk_channel.id))
        print(str(mention) + " has gone AFK in the server " + ctx.guild.name)
        log.write(str(mention) + " has gone AFK in the server " + ctx.guild.name + "\n")
        log.flush()

def imagecreation(nphotos: int, color: tuple, savename: str, cardrarity: list): #function to create an image
    os.chdir("Images")
    imagelist = os.listdir()
    imagetodrop = random.choices(imagelist, weights=cardrarity, k=nphotos)
    images = [Image.open(x) for x in imagetodrop]
    widths, heights = zip(*(i.size for i in images))
    total_width = sum(widths)+140
    max_height = max(heights)+60
    new_im = Image.new('RGB', (total_width, max_height), color)
    x_offset = 50
    y_offset = 30
    for im in images:
        new_im.paste(im, (x_offset,y_offset))
        x_offset += im.size[0]+20
    os.chdir("..")
    new_im.save(savename)
    return imagetodrop

bot.run(token)

