import cv2 as cv, os, numpy as np

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


def getFrameSize(mask):
    """
    return size in pixels of, for now, first frame
    """
    # list of all pixel coordinates that are not in the mask
    coords = list(zip(np.where(~mask)[0], np.where(~mask)[1]))
    frames = (~mask).astype(np.uint8)

    # black magic fuckery
    n, labels, stats, c = cv.connectedComponentsWithStats(frames, connectivity=4)

    # top-left most pixel of the first frame
    y0, x0 = coords[0]
    lbl = labels[y0, x0]

    # height, width because ocv likes this format too much
    return (stats[lbl][3], stats[lbl][2])


for f in pngs:
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
    # (assuming 1st pixel is the darker color since frames don't touch the edges it seems)
    colorD = img[0, 0]
    lumD = .114*colorD[0]+.587*colorD[1]+.299*colorD[2]
    maskD = np.all(img==colorD, axis=2)

    # mask over the every pixel that's lighter than the "background"
    mask = (lum > lumD) & ~((b==255) & (g==255) & (r==255))

    # defining the "frame" color because who knows
    colorL = img[np.where(mask)[0][0], np.where(mask)[1][0]]


    # debug masks
    """
    cv.imshow("maskD", maskD.astype(np.uint8)*255)
    cv.waitKey(0)
    cv.destroyAllWindows()
    """

    # should be 47 over 23 for noelle-1-4.png
    print(getFrameSize(maskD))