import cv2 as cv, os, numpy as np
from PIL import Image

pngs = []

# scan in/ for any pngs
if os.path.exists("./in/"):
    with os.scandir("./in/") as d:
        for f in d:
            if not any(d):
                print("no files found in `in/` folder :/")
            # check if the file is a png
            if f.name.split('.')[len(f.name.split('.'))-1] == "png":
                pngs.append(f)
else:
    print("no `in/` folder found :/")

class Animation:
    def __init__(self):
        frames = 0
        frameSize = (0, 0)
        firstPx = (0, 0)
    def __repr__(self):
        return f"[frames={self.frames}, frameSize={self.frameSize}, firstPx={self.firstPx}]"

def getAnimations(mask):
    nonBg = (~mask).astype(np.uint8)
    # some numpy shit, idk
    n, labels, stats, _ = cv.connectedComponentsWithStats(nonBg, connectivity=4)

    # 
    boxes = set()
    for i in range(1, n):
        x0, y0, width, height, area = stats[i].tolist()
        boxes.add((y0, x0, width, height))

    done = set()
    anims = []
    for b in sorted(boxes):
        if b in done:
            continue

        y0, x0, width, height = b
        frameCount = 0
        currentBox = b
        while currentBox in boxes and currentBox not in done:
            done.add(currentBox)
            frameCount +=1
            currentBox = (y0, currentBox[1]+width+5, width, height)

        anim = Animation()
        anim.firstPx = (y0, x0)
        anim.frameSize = (height, width)
        anim.frames = frameCount
        anims.append(anim)
    return anims

for idx, f in enumerate(pngs):
    img = cv.imread(f.path)
    print(f"processing file {f.name}")

    # store all rgb values as a np array
    b = img[:,:, 0].astype(np.float64)
    g = img[:,:, 1].astype(np.float64)
    r = img[:,:, 2].astype(np.float64)
    # luminance values of all pixels
    lum = .114*b+.587*g+.299*r

    # here i'm assuming the image follows spriter's convention of
    # 1 darker color for the background and 1 lighter color for the frames' boundaries
    # (update: i now know that noelle's sprites for chapter 5 have 2 color palletes, couldn't be bothered rn)

    # find the darker color of the image
    # (assuming 1st pixel is the darker color since frames don't touch the edges of the spritesheet it seems)
    colorD = img[0, 0]
    lumD = .114*colorD[0]+.587*colorD[1]+.299*colorD[2]
    maskD = np.all(img==colorD, axis=2)

    # mask over the every pixel that's lighter than the "background"
    mask = (lum > lumD) & ~((b==255) & (g==255) & (r==255))

    anims = getAnimations(maskD)

    for aIndex, a in enumerate(anims):
        frames = []
        for i in range(a.frames):
            x0 = a.firstPx[1]+i*(a.frameSize[1]+5)
            # crop the image to include only the frame
            crop = img[a.firstPx[0]:a.firstPx[0]+a.frameSize[0], x0:x0+a.frameSize[1]]
            crop = cv.cvtColor(crop, cv.COLOR_BGR2BGRA)
        
            # mask out the bg color
            cmask = cv.inRange(crop, crop[0][0], crop[0][0])

            # remove all pixels out of the inverted mask
            res = cv.bitwise_and(crop, crop, mask=255-cmask)
        
            frames.append(Image.fromarray(cv.cvtColor(res, cv.COLOR_BGR2RGBA)))
        
        if not os.path.exists(f"out/{f.name.split('.')[0]}/"):
                os.makedirs(f"out/{f.name.split('.')[0]}/")
        # some pillow magic to compile the frames into a gif
        frames[0].save(f"out/{f.name.split('.')[0]}/{aIndex+1}.gif", save_all=True, append_images=frames[1:], duration=83, loop=0, disposal=2)
        print(f"saved to out/{f.name.split('.')[0]}/{aIndex+1}.gif")