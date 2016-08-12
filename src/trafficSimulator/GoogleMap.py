from __future__ import division
from TrafficSettings import GOOGLE_STATIC_MAP_API_ADDRESS, GOOGLE_STATIC_MAP_KEY
import requests
from time import sleep
from PIL import Image



def genGooglemap(top, bot, left, right):
    """
    Retrieve four google static map images using the four points and use 1/4 port of each image to
    make a new map image so that we can know the border of the new map.
    :return:
    """
    # height / width
    hwRatio = (top - bot) / (right - left)
    # file names
    images = ["map0.png", "map1.png", "map2.png", "map3.png"]
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
            box = (int(width / 2), int(height / 2), width, height)
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
    img = Image.open(images[0])
    width = img.size[0]
    height = img.size[1]
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
    # height = 640
    parameters["size"] = "%dx%d" % (width, height)

    # zoom
    parameters["zoom"] = "13"

    # scale
    parameters["scale"] = "2"

    # map type: roadmap / satellite / terrain / hybrid
    parameters["maptype"] = "roadmap"

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
    print url

    # get image from the Internet
    res = requests.session().get(url)

    # save image
    f = open(filename, 'wb')
    f.write(res.content)
    f.close()
    sleep(0.1)


# for testing
#getGoogleStaticMap(39.327503, -76.617698, "googlemap")