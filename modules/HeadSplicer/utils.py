from random import randint

import cv2
from PIL import Image as IMG


cascades = [
    cv2.CascadeClassifier("./modules/HeadSplicer/statics/haarcascade_frontalface_alt.xml"),
    cv2.CascadeClassifier("./modules/HeadSplicer/statics/haarcascade_profileface.xml"),
    cv2.CascadeClassifier("./modules/HeadSplicer/statics/lbpcascade_animeface.xml"),
    cv2.CascadeClassifier("./modules/HeadSplicer/statics/haarcascade_frontalcatface.xml"),
    cv2.CascadeClassifier("./modules/HeadSplicer/statics/haarcascade_frontalcatface_extended.xml"),
]


class TooManyFacesDetected(Exception):
    """ 脸太tm多了！爬！ """


async def process(filename, outfile) -> bool:
    cvimg = cv2.imread(filename, cv2.IMREAD_COLOR)  # 图片灰度化
    gray = cv2.cvtColor(cvimg, cv2.COLOR_BGR2GRAY)  # 直方图均衡化
    gray = cv2.equalizeHist(gray)   # 加载级联分类器
    for cascade in cascades:
        # print(cascade_file)
        # cascade = cv2.CascadeClassifier(cascade_file)   # 加载级联分类器
        faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(24, 24))   # 多尺度检测
        if not len(faces):
            continue
        if len(faces) >= 10:
            raise TooManyFacesDetected
        img = IMG.open(filename)
        img = img.convert("RGBA")
        top_shift_scale = 0.45
        x_scale = 0.25
        for (x, y, w, h) in faces:
            y_shift = int(h * top_shift_scale)
            x_shift = int(w * x_scale)
            face_w = max(w + 2 * x_shift, h + y_shift)
            faceimg = IMG.open("./modules/HeadSplicer/statics/猫猫头_" + str(randint(0, 3)) + ".png")
            faceimg = faceimg.resize((face_w, face_w))
            r, g, b, a = faceimg.split()
            img.paste(faceimg, (x - x_shift, y - y_shift), mask=a)
        img.save(outfile)
        return True
    return False
