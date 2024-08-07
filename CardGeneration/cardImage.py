from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import os, random, re, sys
from unicodedata import normalize

TEXT_WIDTH = 40
LINE_HEIGHT = 35

def image(dat, hasImage = False, output = "output"):
    if type(dat) is str:
        dat = dat.replace("N/A", "")
        dat = dat.replace('\\\"', "'")
        dat = normalize('NFKD', dat).encode('utf-8')
        dat = eval(dat)

    if not "name" in dat:
        dat["name"] = "Card Name"
    if not "type" in dat:
        dat["type"] = "Type Line"
    if not "keywords" in dat:
        dat["keywords"] = []
    if not "text" in dat:
        dat["text"] = []
    if not "flavorText" in dat:
        dat["flavorText"] = "Flavor Text"
    if not "power" in dat:
        dat["power"] = 1
    if not "toughness" in dat:
        dat["toughness"] = 1
    if not "imageDescription" in dat:
        dat["imageDescription"] = "Abstract Art"
    if type(dat["manaCost"]) == str:
        temp = dat["manaCost"] 
        numbers = [int(num) for num in re.findall(r'\d+', temp)]
        c = numbers[0] if numbers else 0

        dat["manaCost"] = {
            "red": temp.count("R"),
            "blue": temp.count("B"),
            "green": temp.count("G"),
            "black": temp.count("B"),
            "white": temp.count("W"),
            "colorless": c
        }
    elif not "manaCost" in dat or dat["type"] == "Land":
        dat["manaCost"] = {
        "red": 0,
        "blue": 0,
        "green": 0,
        "black": 0,
        "white": 0,
        "colorless": 0
    }

    tempColor = random.randint(1, 10)    
    img = Image.open("CardGeneration/Templates/" + str(tempColor) + ".png")
    draw = ImageDraw.Draw(img)

    if len(dat["name"]) > 15:
        size = 42
        fontName = ImageFont.truetype("comicbd.ttf", size)
        draw.text((96, 76 + (42 - size)),dat["name"],(0,0,0),font=fontName)
    else:
        fontName = ImageFont.truetype("comicbd.ttf", 42)
        draw.text((96, 76),dat["name"],(0,0,0),font=fontName)

    #Write Card Type
    fontType = ImageFont.truetype("comic.ttf", 42)
    draw.text((96, 766),dat["type"],(0,0,0),font=fontType)

    dat["power"] = dat["power"].replace("\t","").replace(" ","")
    dat["toughness"] = dat["toughness"].replace("\t","").replace(" ","")

    try:
        dat["power"] = str(int(dat["power"]))
        dat["toughness"] = str(int(dat["toughness"]))
    except:
        pass

    #Write Card Power / Toughness
    if not ((dat["power"] == "" and dat["toughness"] == "") or (str(dat["power"]) == "0" and str(dat["toughness"]) == "0")):
        draw.text((773, 1212),str(dat["power"]) + "/" + str(dat["toughness"]),(0,0,0),font=fontType)

    #Write Main Body
    cursorY = 864
    fontBody = ImageFont.truetype("comic.ttf", 35)

    keyWords = "" 
    for keyWord in dat["keywords"].split(" "):
        keyWords += keyWord.replace(",","") + ", "
    keyWords = keyWords[:-2]

    bodyTextSpace = [keyWords] + [dat["text"]]
    bodyText = []

    for line in bodyTextSpace:
        bodyText.extend(line.split("\\n"))

    for line in bodyText:
        # Handle unicode and newlines
        line = bytes(line, 'utf-8').decode("unicode_escape")
        sublines = line.split("\n")
        
        for subline in sublines:
            last_space = subline.rfind(' ', 0, TEXT_WIDTH)
            while subline:
                # Find the position to wrap the line
                last_space = subline.rfind(' ', 0, TEXT_WIDTH)
                
                if last_space == -1 or len(subline) <= TEXT_WIDTH:
                    draw.text((104, cursorY), subline, (0, 0, 0), font=fontBody)
                    cursorY += LINE_HEIGHT
                    break

                # Draw the subline and adjust the remaining text
                draw.text((104, cursorY), subline[:last_space], (0, 0, 0), font=fontBody)
                subline = subline[last_space + 1:]
                cursorY += LINE_HEIGHT

    # Add extra space after the paragraph or original line
    cursorY += LINE_HEIGHT * 0.5

    cursorY += 20
    if dat["flavorText"] != "":
        fontBody = ImageFont.truetype("comici.ttf", 24)
        flavorTextLines = dat["flavorText"].split('\n')
        for flavorText in flavorTextLines:
            line = '"' + flavorText + '"'
            while True:
                cursorY += 25
                last_space = line.rfind(' ', 0, TEXT_WIDTH)
                if last_space == -1 or len(line) <= TEXT_WIDTH:
                    break
                draw.text((104, cursorY), line[:last_space], (0, 0, 0), font=fontBody)
                line = line[last_space + 1:]
            
            if line:
                draw.text((104, cursorY), line, (0, 0, 0), font=fontBody)
            cursorY += 25

    #Paste Mana Icons

    cursorX = 835
    cx = 40
    cy = 90

    colors = ["green","red","black","blue","white"]
    totalMana = 0
    colorLess = dat["manaCost"]["colorless"]
    if colorLess > 0:
        totalMana = 1
    for color in colors:
        totalMana += dat["manaCost"][color]
    if totalMana > 5:
        cx = 30
        cy = 95
    
    mask = Image.new('L', (cx, cx), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, cx, cx), fill=255)
    
    for color in colors:
        try:
            icon = Image.open("CardGeneration//icons//" + color + ".png")
            icon = icon.resize((cx, cx), Image.LANCZOS)
            for i in range(dat["manaCost"][color]):
                img.paste(icon, (cursorX, cy), mask)
                cursorX -= round(cx * 1.25)
        except:
            continue


    if colorLess > 15:
        colorLess = 15
    if colorLess > 0:
        icon = Image.open("CardGeneration//icons//" + str(colorLess) + ".png")
        icon = icon.resize((cx, cx), Image.LANCZOS)
        img.paste(icon, (cursorX, cy), mask)
        

    #Paste Image
    if hasImage:
        pass #Can use if custom images are supported
    else:
        foundTag = False
        for cardType in ["Artifact", "Creature", "Enchantment", "Instant", "Sorcery"]:
            if cardType in dat["type"]:
                src = f"CardGeneration//CardArt//{cardType}//" + random.choice(os.listdir(f"CardGeneration//CardArt//{cardType}//"))
                #print(src)
                cardArt = Image.open(src)
                foundTag = True

        if not foundTag:
            cardArt = Image.open("CardGeneration//Van.gogh.paintings//" + random.choice(os.listdir("CardGeneration//Van.gogh.paintings//")))
    
    cardArt = cardArt.resize((808, 593), Image.LANCZOS)
    #cardArt = cardArt.crop((0, 28, 808, 780))
    #cardArt.save("cardArt.png")
    #alteredArt = Image.open("cardArt.png")
    img.paste(cardArt, (84, 163))
    
    cardArt.close()
    if hasImage:
        os.remove("cardArt.png")
    img.save(str(output) + '.png')
    return img

#image(gptConnect.getMagicCard(input("Describe your magic card: ")), hasImage = False)

try:
    data = sys.argv[1].replace("```","").replace("json","").replace("'","^")
    null = ""
    image(data, output = "public//cards//" + eval(data)["id"])
    print("No errors! :)")
except Exception as e:
    print(repr(e))

