import os
from PIL import Image, ImageFont, ImageDraw

frame = Image.open(input("Drag the frame to use: "), 'r')
content = Image.open(input("Drag the image of the card: "), 'r')
cardname = input("Write the name of the card: ")
cardnamefontsize = input("Write the size of the font: ")
seriesname = input("Write the name of the series: ")
seriesnamefontsize = input("Write the size of the font: ")
fontfile = input("Drag the font .ttf file: ")
frame.paste(content.resize((196, 196)), box=(11, 11, 207, 207))

draw = ImageDraw.Draw(frame)
font = ImageFont.truetype(fontfile, int(cardnamefontsize))
w, h = draw.textsize(cardname, font=font)
draw.text(((218-w)/2,220), cardname, fill="black", font=font)
font = ImageFont.truetype(fontfile, int(seriesnamefontsize))
w, h = draw.textsize(seriesname, font=font)
draw.text(((218-w)/2,275), seriesname, fill="black", font=font)

os.chdir("..")
listindexes = os.listdir("Images")
frame.save("Images//" + str(len(listindexes)+1) + ".png")
print("Card created.")
os.system("pause")
