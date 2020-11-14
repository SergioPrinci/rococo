import os
import lxml.etree as ET
from PIL import Image, ImageFont, ImageDraw

frame = Image.open(input("Drag the frame to use: ").strip('"'), 'r')
content = Image.open(input("Drag the image of the card: ").strip('"'), 'r')
cardname = input("Write the name of the card: ")
cardnamefontsize = input("Write the size of the font(18 is the max suggested): ")
seriesname = input("Write the name of the series: ")
seriesnamefontsize = input("Write the size of the font(18 is the max suggested): ")
fontfile = input("Drag the font .ttf file: ").strip('"')
while True: 
    value = int(input("Insert the value of the card(from 1 to 20): ")) 
    if value>1 and value<20: break
frame.paste(content.resize((196, 196)), box=(11, 11, 207, 207))

os.chdir("..")
listindexes = os.listdir("Images")

root = ET.parse("Sources\\CardDatabase.xml", ET.XMLParser(remove_blank_text=True)).getroot()
root.attrib["ncards"] = str(int(root.attrib["ncards"])+1)
newcardbranch = ET.Element("card")
newcardbranch.attrib["ID"] = str(len(listindexes)+1)
newcardname = ET.SubElement(newcardbranch, "name")
newcardname.text = cardname
newcardseries = ET.SubElement(newcardbranch, "series")
newcardseries.text = seriesname
newcardvalue = ET.SubElement(newcardbranch, "value")
newcardvalue.text = str(value)
newcardrarity = ET.SubElement(newcardbranch, "rarityweight")
newcardrarity.text = str(21-value)
root.append(newcardbranch)
newroot = ET.tostring(root, encoding="UTF-8", pretty_print=True)
open("Sources\\CardDatabase.xml", "wb").write(newroot)

draw = ImageDraw.Draw(frame)
font = ImageFont.truetype(fontfile, int(cardnamefontsize))
w, h = draw.textsize(cardname, font=font)
draw.text(((218-w)/2,217), cardname, fill="black", font=font)
font = ImageFont.truetype(fontfile, int(seriesnamefontsize))
w, h = draw.textsize(seriesname, font=font)
draw.text(((218-w)/2,260), seriesname, fill="black", font=font)


frame.save("Images//" + str(len(listindexes)+1) + ".png")
print("Card created.")
os.system("pause")
