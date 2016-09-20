from __future__ import division
from TrafficSettings import GOOGLE_STATIC_MAP_API_ADDRESS, GOOGLE_STATIC_MAP_KEY
from config import MAP_FOLDER, BG_MAP_NAME
import requests
from time import sleep
from PIL import Image
import os
import matplotlib.pyplot as plt



def getBackgroundMap(center, height, width):
    """
    Download the static map centered at the given position (lat, lng) from Google Map API.
    Save the downloaded map and return its file address.
    :param center: (lat, lng)
    :return: file address of the downloaded map.
    """
    mapFolder = os.getcwd() + MAP_FOLDER
    if not os.path.exists(mapFolder):
        os.makedirs(mapFolder)

    filename = mapFolder + "/" + BG_MAP_NAME
    parameters = genGoogleMapAPIParameter(center[0], center[1], height / width)
    getGoogleStaticMap(parameters, filename)
    return filename

def genGooglemap(top, bot, left, right):
    """
    Retrieve four google static map images using the four points and use 1/4 port of each image to
    make a new map image so that we can know the border of the new map.
    :return:
    """
    # height / width
    hwRatio = (top - bot) / (right - left)
    # file names
    images = [MAP_FOLDER + "/topLeft.png",
              MAP_FOLDER + "/topRight.png",
              MAP_FOLDER + "/botLeft.png",
              MAP_FOLDER + "/botRight.png"]
    # centers for the four map images
    centers = [(top, left), (top, right), (bot, left), (bot, right)]

    # create four map images
    for i in range(len(images)):
        parameters = genGoogleMapAPIParameter(centers[i][0], centers[i][1], hwRatio)
        getGoogleStaticMap(parameters, images[i])

        # crop top left image
        img = Image.open(images[i])
        width = img.size[0]
        height = img.size[1]
        if i == 0:
            box = (int(width / 2), int(height / 2), width, height) # left, top, right, bot
        elif i == 1:
            box = (0, int(height / 2), int(width / 2), height)
        elif i == 2:
            box = (int(width / 2), 0, width, int(height / 2))
        else:
            box = (0, 0, int(width / 2), int(height / 2))
        newImg = img.crop(box)
        img.close()
        newImg.save(images[i])

    # merge four sub-maps
    img = Image.open(images[0]).size
    width, height = img.size
    img.close()

    mergedImage = Image.new('RGB', (width * 2, height * 2))
    coords = [
        (0, 0),
        (width, 0),
        (0, height),
        (width, height)
    ]
    for i in range(len(images)):
        img = Image.open(images[i])
        mergedImage.paste(img, coords[i])
    mergedImage.save("map.png")

def genGoogleMapAPIParameter(lat, lng, hwRatio):
    parameters = {}

    # API key
    parameters["key"] = GOOGLE_STATIC_MAP_KEY

    # center points
    parameters["center"] = "%f,%f" % (lat, lng)

    # image's width and height
    width = 640
    height = int(min(640, hwRatio * width))
    parameters["size"] = "%dx%d" % (width, height)

    # zoom: 0-21 = entire map-detail
    parameters["zoom"] = "13"

    # scale
    parameters["scale"] = "2"

    # map type: roadmap / satellite / terrain / hybrid
    parameters["maptype"] = "satellite"

    return parameters

def getGoogleStaticMap(parameters, filename):
    """
    Download Google static map using Google map api.
    :param lat:
    :param lng:
    :param filename: (str) the filename for saving the downloaded image.
    """
    # base url
    url = GOOGLE_STATIC_MAP_API_ADDRESS

    # add parameters format
    for key in parameters:
        url += key + "=" + parameters[key] + "&"
    url = url[:-1]

    # generate request url with parameters
    # url = url.format(**parameters)
    print url  # for checking correctness

    # get image from the Internet
    res = requests.session().get(url)

    # save image
    f = open(filename, 'wb')
    f.write(res.content)
    f.close()
    sleep(0.1)


# for testing
# center = (39.327503, -76.617698)
# filename = getBackgroundMap(center, 4, 6)
# img = plt.imread(filename)
# plt.imshow(img)
# plt.show()


"""
top, bot, left, right
38.9150644378 38.881276216 -77.057412562 -76.9936787843
"""
topLeft = (38.9150644378, -77.057412562)
topRight = (38.9150644378, -76.9936787843)
botLeft = (38.881276216, -77.057412562)
botRight = (38.881276216, -76.9936787843)
centers = [topLeft, topRight, botLeft, botRight]

filename = ["pic/topLeft.png", "pic/topRight.png", "pic/botLeft.png", "pic/botRight.png"]
hwRatio = 2/3
# for i in range(4):
#     param = genGoogleMapAPIParameter(centers[i][0], centers[i][1], hwRatio)
#     getGoogleStaticMap(param, filename[i])
