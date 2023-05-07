import functions_framework
from google_images_search import GoogleImagesSearch
import numpy as np
import os
import math
import random
import cv2
import requests
from os import path
import glob
import boto3
import uuid
import smtplib, ssl
from email.mime.text import MIMEText


def send_email(link, receiver):
    sender = "###"
    password = "###"
    mesg = "Your image has finished compiling. Here is the link to your mosaic: " + link
    message = MIMEText(mesg)

    message["From"] = sender
    message["To"] = receiver
    message["Subject"] = "CS 445 Mosaic Compiled Successfully"

    with smtplib.SMTP_SSL(
        host="smtp.gmail.com", port=465, context=ssl.create_default_context()
    ) as server:
        server.login(sender, password)

        server.sendmail(
            from_addr=sender,
            to_addrs=receiver,
            msg=message.as_string(),
        )

    server.quit()


def read_image(image_path: str, default_path: str) -> np.ndarray:
    """
    Reads image from image path, and
    return floating point RGB image

    Args:
        image_path: path to image

    Returns:
        RGB image of shape H x W x 3 in floating point format
    """
    # read image and convert to RGB
    # print('/tmp/'+image_path)
    bgr_image = cv2.imread("/tmp/" + image_path)
    if bgr_image is not None:
        rgb_image = cv2.resize(bgr_image, (160, 160))
        return rgb_image.astype(np.float32)
        #     # print('not none')
        #     if bgr_image.shape[2] > 1:
        #         rgb_image = bgr_image[:, :, [2, 1, 0]]
        #     # TODO remove when images are of the correct size (160x160)
        #     rgb_image = cv2.resize(rgb_image, (160, 160))
        #     return rgb_image.astype(np.float32) / 255
    else:
        bgr_image = cv2.imread("/tmp/" + default_path)
        rgb_image = cv2.resize(bgr_image, (160, 160))
        return rgb_image.astype(np.float32)
        #     # print('not none')
        #     if bgr_image.shape[2] > 1:
        #         rgb_image = bgr_image[:, :, [2, 1, 0]]
        #     # TODO remove when images are of the correct size (160x160)
        #     rgb_image = cv2.resize(rgb_image, (160, 160))
        #     return rgb_image.astype(np.float32) / 255


@functions_framework.http
def hello_http(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    request_json = request.get_json(silent=True)
    request_args = request.args
    if request_args and "target_image" in request_args:
        print(request_args.get("target_image"))
        target_image = request_args.get("target_image")
        search_query = request_args.get("search_query")
        receiver = request_args.get("receiver")
    else:
        print("still no")
        target_image = request_json["target_image"]
        search_query = request_json["search_query"]
        receiver = request_json["receiver"]
    img_data = requests.get(target_image).content

    l = "/tmp/{}.jpg".format("targetImage")
    with open(l, "wb") as output:
        output.write(img_data)
    # target_image = l

    datadir = "/tmp"
    images_folder = "/tmp"

    gis = GoogleImagesSearch("###", "###")
    _search_params = {
        "q": search_query,
        "num": 100,
        "fileType": "jpg",
    }
    # this will only search for images:
    gis.search(search_params=_search_params)

    res = gis.results()

    # loop over images
    i = 0
    for image in gis.results():
        #   print(image.url)
        img_data = requests.get(image.url).content

        # mp3file = urllib.request.urlopen()
        l = "/tmp/{}.jpg".format(str(i))
        with open(l, "wb") as output:
            output.write(img_data)
        i += 1

    image_files_names = [
        f
        for f in os.listdir(images_folder)
        if path.isfile(path.join(images_folder, f))
        and f.endswith((".jpg", ".png", ".jpeg"))
    ]

    # print(len(image_files_names))

    images_averages = np.zeros((160, 160, len(image_files_names)))
    # print(images_averages.shape)
    counter = 0
    for image in image_files_names:
        # images_averages[:, :, counter] = read_image(datadir + "/" + image).mean(axis=2)
        # readImage = read_image(image,'targetImage.jpg')
        # if readImage is not None:
        #     images_averages[:, :, counter] = readImage.mean(axis=2)
        #     counter += 1
        images_averages[:, :, counter] = read_image(image, "targetImage.jpg").mean(
            axis=2
        )
        counter += 1
        # read_image(image)

    # print('target_image')
    # target = cv2.imread('/tmp/targetImage.jpg')[:, :, [2, 1, 0]] / 255
    target = cv2.imread("/tmp/targetImage.jpg")

    target = cv2.resize(target, (9600, 9600))

    # bgr_image = cv2.imread('/tmp/targetImage.jpg')
    # rgb_image = cv2.resize(bgr_image, (160, 160))
    # rrr = rgb_image.astype(np.float32) / 255
    # rrrrrr = rgb_image.astype(np.float32)
    # cv2.imwrite('/tmp/tirrle.jpg', rrr)
    # cv2.imwrite('/tmp/rgb_image.jpg', rgb_image)
    # cv2.imwrite('/tmp/rrrrrrgb_image.jpg', rrrrrr)
    # cv2.imwrite('/tmp/targetrrrrrrgb_image.jpg', target)

    H_tiles = int(target.shape[1] / 160)
    V_tiles = int(target.shape[0] / 160)
    # print("Number of 160x160 tiles: ", H_tiles,"x", V_tiles," total = ", H_tiles * V_tiles)

    output = np.zeros(target.shape)
    score = np.zeros(images_averages.shape[2])
    # Create mosaic

    for h in range(H_tiles):
        for v in range(V_tiles):
            patch = (target[v * 160 : v * 160 + 160, h * 160 : h * 160 + 160, :]).mean(
                axis=2
            )

            for sample in range(images_averages.shape[2]):
                err = np.linalg.norm(cv2.subtract(images_averages[:, :, sample], patch))
                score[sample] = err
            sorted_indexes = np.argsort(score)
            random_index = random.randint(0, 15)
            tile = read_image(
                image_files_names[sorted_indexes[random_index]],
                "targetImage.jpg"
                # 'targetImage.jpg','targetImage.jpg'
            )
            output[v * 160 : v * 160 + 160, h * 160 : h * 160 + 160, :] = tile
    # print(output)

    name = "frame_output" + ".jpg"
    # print(f'Creating: {name}')
    cv2.imwrite(os.path.join("/tmp", name), output)
    cv2.imwrite("/tmp/color_img.jpg", output)
    cv2.imwrite("/tmp/tile.jpg", tile)

    BUCKET_NAME = "kerchow-content"
    FOLDER_NAME = "posts/" + str(uuid.uuid4())

    s3 = boto3.client(
        "s3",
        region_name="us-east-2",
        aws_access_key_id="###",
        aws_secret_access_key="###",
    )

    mod_files = []

    files = glob.glob("/tmp/" + name)
    # files = glob.glob("/tmp/*.jpg")
    # print(files[0])
    for f in files:
        key = "%s/%s" % (FOLDER_NAME, os.path.basename(f))
        mod_files.append(key)
        s3.upload_file(f, BUCKET_NAME, key)

    # print(mod_files[0])
    resu = "https://kerchow-content.s3.us-east-2.amazonaws.com/" + mod_files[0]
    send_email(resu, receiver)
    return resu
