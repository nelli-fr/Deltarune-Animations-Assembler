import cv2 as cv, os, numpy as np
from PIL import Image

pngs = []

# scan in/ for any pngs
if os.path.exists("./in/"):
    with os.scandir("./in/") as d:
        for f in d:
            # check if the file is a png
            if f.name.split('.')[len(f.name.split('.'))-1] == "png":
                pngs.append(f)
else:
    print("no `in/` folder")


class Animation:
    def __init__(self):
        frames = 0
        frameSize = (0, 0)
        firstPx = (0, 0)
    def __repr__(self):
        return f"[frames={self.frames}, frameSize={self.frameSize}, firstPx={self.firstPx}]"

def getAnimationsOld(img, mask, idx):
    """
    return first frame's pos, frames' size and amount of frames of, for now, first animation
    """

    # add an area to the mask that contains alr processed animation until there is no frames left!!!

    anims = []
    # list of all pixel coordinates that are not in the mask
    coords = list(zip(np.where(~mask)[0], np.where(~mask)[1]))
    while coords:
        coords = list(zip(np.where(~mask)[0], np.where(~mask)[1]))
        frames = (~mask).astype(np.uint8)
        
        # black magic fuckery
        n, labels, stats, c = cv.connectedComponentsWithStats(frames, connectivity=4)
        
        # top-left most pixel of the first frame
        y0, x0 = coords[0]
        lbl = labels[y0, x0]
        
        sizeX = stats[lbl][2]
        sizeY = stats[lbl][3]
        
        frameCount = 1
        # starting from first pixel of the anim, go over it's width +5 px to determine frame count 
        while ~mask[y0+1, x0+1+(sizeX+5)*frameCount]:
            frameCount+=1
                
        anim = Animation()
        anim.firstPx = (y0, x0)
        anim.frameSize = (stats[lbl][3], stats[lbl][2])
        anim.frames = frameCount

        mask[y0:y0+sizeY, x0:x0+(sizeX+5)*frameCount] = True
        
        anims.append(anim)
    return anims




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

    # store all rgb values as a np array
    b = img[:,:, 0].astype(np.float64)
    g = img[:,:, 1].astype(np.float64)
    r = img[:,:, 2].astype(np.float64)
    # luminance values of all pixels
    lum = .114*b+.587*g+.299*r

    # here i'm assuming the image follows spriter's convention of
    # 1 darker color for the background and 1 lighter color for the frames' boundaries

    # find the darker color of the image
    # (assuming 1st pixel is the darker color since frames don't touch the edges of the spritesheet it seems)
    colorD = img[0, 0]
    lumD = .114*colorD[0]+.587*colorD[1]+.299*colorD[2]
    maskD = np.all(img==colorD, axis=2)

    # mask over the every pixel that's lighter than the "background"
    mask = (lum > lumD) & ~((b==255) & (g==255) & (r==255))

    # defining the "frame" color because who bnows
    colorL = img[np.where(mask)[0][0], np.where(mask)[1][0]]
    print(colorL) # [255 134 195]

    # for noelle-1-4.png should be 47x23, 4 frames, starting at (5, 5) 
    anims = getAnimations(maskD)
    print(idx)

    for aIndex, a in enumerate(anims):
        frames = []
        for i in range(a.frames):
            x0 = a.firstPx[1]+i*(a.frameSize[1]+5)
            # crop the image to include only the frame
            crop = img[a.firstPx[0]:a.firstPx[0]+a.frameSize[0], x0:x0+a.frameSize[1]]
            crop = cv.cvtColor(crop, cv.COLOR_BGR2BGRA)
            #cv.imshow("crop", crop)
            #cv.waitKey(1000)
            #cv.destroyAllWindows()
        
            # mask out the bg color
            cmask = cv.inRange(crop, crop[0][0], crop[0][0])
            #cv.imshow("cmask", cmask.astype(np.uint8))
            #cv.waitKey(1000)
            #cv.destroyAllWindows()

            # remove all pixels out of the inverted mask
            res = cv.bitwise_and(crop, crop, mask=255-cmask)
        
            frames.append(Image.fromarray(cv.cvtColor(res, cv.COLOR_BGR2RGBA)))
        
        if not os.path.exists(f"out/{f.name.split('.')[0]}/"):
                os.makedirs(f"out/{f.name.split('.')[0]}/")
        # some pillow magic to compile the frames into a gif
        frames[0].save(f"out/{f.name.split('.')[0]}/{aIndex+1}.gif", save_all=True, append_images=frames[1:], duration=83, loop=0, disposal=2)
        print(f"saved #{idx}")