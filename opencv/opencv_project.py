#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Newton Augusto Reinoldes Miotto"
__license__ = "GPL"
__version__ = "1.0.1"
__email__ = "newton.a.r.miotto@gmail.com"
__status__ = "Produção"


# importa opencv e numpy
import cv2  
import numpy as np

# lê imagem
def read_image():
    img = cv2.imread(r"Resources/lena.png")
    # mostra imagem
    cv2.imshow("Output", img)
    # seta o tempo que a imagem vai ficar na tela. "0" = sempre
    cv2.waitKey(0)
    return img

# lê vídeo
def read_video():
    cap = cv2.VideoCapture(r"Resources/robo.mp4")

    # reproduz o vídeo até clicar a tecla 'espaço'  
    while True:
        success, img = cap.read()
        cv2.imshow("Video", img)
        if cv2.waitKey(1) & 0xFF ==ord(' '):
            break

# mostra web cam
def web_cam():
    cap = cv2.VideoCapture(0)
    
    # seta resoluçao
    cap.set(3, 640)
    cap.set(4, 480)
    cap.set(10, 100)

    # mostra vídeo até clicar a tecla 'espaço'
    while True:
        success, img = cap.read()
        cv2.imshow("Video", img)
        if cv2.waitKey(1) & 0xFF ==ord(' '):
            break

# funções básicas
def basic_functions():
    img = cv2.imread("Resources/hippie.png")

    # regra de interação entre os pixels
    kernel = np.ones((5, 5), np.uint8)

    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (7, 7), 0)
    imgCanny = cv2.Canny(img, 100, 100)
    imgDialation = cv2.dilate(imgCanny, kernel, iterations=1)
    imgEroded = cv2.erode(imgDialation, kernel, iterations=1)

    # para visualizar as imagens remova o comentário
    cv2.imshow("Image", img)
    cv2.imshow("Gray Image", imgGray)
    # cv2.imshow("Blur Image", imgBlur)
    cv2.imshow("Canny Image", imgCanny)
    # cv2.imshow("Dialation Image", imgDialation)
    # cv2.imshow("Eroded Image", imgEroded)
    cv2.waitKey(0)

# redimensiona a imagem
def resize():
    img = cv2.imread(r"Resources/jackie.jpg")
    # mostra o formato
    print(img.shape)

    imgResize = cv2.resize(img, (300, 200))
    print(imgResize.shape)
    cv2.imshow("Image", img)
    cv2.imshow("Image Resize", imgResize)
    cv2.waitKey(0)

# recorta a imagem
def cropped():
    img = cv2.imread(r"Resources/jackie.jpg")
    print(img.shape)
    #define os limites
    imgCropped = img[10:450, 300:800]
    print(imgCropped.shape)
    cv2.imshow("Image", img)
    cv2.imshow("Image Cropped", imgCropped)
    cv2.waitKey(0)

# desenha formatos em imagens
def draw():
    img = np.zeros((512, 512, 3), np.uint8)
    # print(img)

    # pinta centro da imagem de azul
    img[12:500, 12:500] = 255, 170, 170
    
    # desenha linhas de cores diferentes
    cv2.line(img, (0, 0), (256, 256), (0, 255, 0), 3)
    cv2.line(img, (257, 257), (512, 512), (0, 0, 255), 3)
    cv2.line(img, (0, 512), (img.shape[0], img.shape[-1]), (0, 0, 0), 3)

    cv2.rectangle(img, (192, 35), (304, 150), (255, 0, 0), cv2.FILLED)
    cv2.circle(img,(400, 50), 30, (130, 130, 255), 5)
    cv2.putText(img, " OPENCV ", (330, 300), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 150, 0), 2)

    cv2.imshow("Imagem", img)
    cv2.waitKey(0)

# Ajusta a imagem
def warp():
    img = cv2.imread("Resources/cards.jpg")
    width, height = 250, 350

    # Para ajustar você deve definir os pontos de recorte
    # Para localizar os pontos, basta utilizar um editor de imagem como o Paint e encontrar as coordenadas 
    pts1 = np.float32([[111, 219], [287, 188], [154, 482], [352, 440]]) # define os 4 pontos
    pts2 = np.float32([[0, 0], [width, 0], [0, height], [width, height]])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    imgOutput = cv2.warpPerspective(img, matrix, (width, height))

    cv2.imshow("Imagem", img)
    cv2.imshow("Output", imgOutput)

    cv2.waitKey(0)

# Junta imagens, função retirada do curso
def stackImages(scale, imgArray):
    rows = len(imgArray)
    cols = len(imgArray[0])
    rowsAvailable = isinstance(imgArray[0], list)
    width = imgArray[0][0].shape[1]
    height = imgArray[0][0].shape[0]
    if rowsAvailable:
        for x in range ( 0, rows):
            for y in range(0, cols):
                if imgArray[x][y].shape[:2] == imgArray[0][0].shape [:2]:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                else:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (imgArray[0][0].shape[1], imgArray[0][0].shape[0]), None, scale, scale)
                if len(imgArray[x][y].shape) == 2: imgArray[x][y]= cv2.cvtColor( imgArray[x][y], cv2.COLOR_GRAY2BGR)
        imageBlank = np.zeros((height, width, 3), np.uint8)
        hor = [imageBlank]*rows
        hor_con = [imageBlank]*rows
        for x in range(0, rows):
            hor[x] = np.hstack(imgArray[x])
        ver = np.vstack(hor)
    else:
        for x in range(0, rows):
            if imgArray[x].shape[:2] == imgArray[0].shape[:2]:
                imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
            else:
                imgArray[x] = cv2.resize(imgArray[x], (imgArray[0].shape[1], imgArray[0].shape[0]), None,scale, scale)
            if len(imgArray[x].shape) == 2: imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
        hor= np.hstack(imgArray)
        ver = hor
    return ver

# Para padronizar as chamadas
def stack_images():
    img = cv2.imread('Resources/lena.png')
    imgGray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    
    imgStack = stackImages(0.5,([img,imgGray,img],[img,img,img]))
    
    # imgHor = np.hstack((img,img))
    # imgVer = np.vstack((img,img))
    #
    # cv2.imshow("Horizontal",imgHor)
    # cv2.imshow("Vertical",imgVer)
    cv2.imshow("ImageStack",imgStack)
    
    cv2.waitKey(0)

# Função auxiliar para a função de baixo (detect_color)
def empty(a):
    pass

# Detecta a cor laranja da imagem
def detect_color():
    cv2.namedWindow("TrackBars")
    cv2.resizeWindow("TrackBars", 640, 240)
    # Normalmente o valor de matiz vai de 0 a 360, mas no opencv vai até 179
    cv2.createTrackbar("Hue Min", "TrackBars", 0, 179, empty)
    cv2.createTrackbar("Hue Max", "TrackBars", 19, 179, empty)
    cv2.createTrackbar("Sat Min", "TrackBars", 110, 255, empty)
    cv2.createTrackbar("Sat Max", "TrackBars", 240, 255, empty)
    cv2.createTrackbar("Val Min", "TrackBars", 153, 255, empty)
    cv2.createTrackbar("Val Max", "TrackBars", 255, 255, empty)

    while True:
        img = cv2.imread('Resources/lambo.png')
        # HSV é a abreviatura para o sistema de cores formadas pelas componentes hue (matiz), saturation (saturação) e value (valor).
        imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h_min = cv2.getTrackbarPos("Hue Min", "TrackBars")
        h_max = cv2.getTrackbarPos("Hue Max", "TrackBars")
        s_min = cv2.getTrackbarPos("Sat Min", "TrackBars")
        s_max = cv2.getTrackbarPos("Sat Max", "TrackBars")
        v_min = cv2.getTrackbarPos("Val Min", "TrackBars")
        v_max = cv2.getTrackbarPos("Val Max", "TrackBars")
        # print(h_min, h_max, s_min, s_max, v_min, v_max)
        lower = np.array([h_min, s_min, v_min])
        upper = np.array([h_max, s_max, v_max])
        mask = cv2.inRange(imgHSV, lower, upper)

        imgResult = cv2.bitwise_and(img, img, mask=mask)

        # cv2.imshow("Original", img)
        # cv2.imshow("HSV", imgHSV)
        # cv2.imshow("Mask", mask)
        # cv2.imshow("Result", imgResult)

        imgStack = stackImages(0.6, ([img, imgHSV], [mask, imgResult]))
        cv2.imshow("Stacked Images", imgStack)
        if cv2.waitKey(1) & 0xFF == ord(' '):
            break

# Retirar formatos da imagem
def detect_shapes():
    img = cv2.imread("Resources/shapes.png")
    imgContour = img.copy()

    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (7, 7), 1)
    imgCanny = cv2.Canny(imgBlur, 50, 50)
    getContours(imgCanny, imgContour)

    imgBlank = np.zeros_like(img)
    imgStack = stackImages(0.8,([img, imgGray, imgBlur], [imgCanny, imgContour, imgBlank]))
    cv2.imshow("Stack", imgStack)
    cv2.waitKey(0)

# Função auxiliar para detect_shapes()
def getContours(img, imgContour):
    # Pelo que entendi o atributo RETR_EXTERNAL define que queremos o contorno da imagem  de acordo com o filtro
    contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        # print(area)
        # Threshold
        if area > 500:
            cv2.drawContours(imgContour, cnt,-1,(255, 0, 0), 3)
            peri = cv2.arcLength(cnt, True)
            # print(peri)
            # aproxima o formato da imagem, encontra os vértices
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            # print(approx)
            # print(len(approx))
            objCor = len(approx)
            x, y, w, h = cv2.boundingRect(approx)
            
            if objCor == 3: objectType = "Triangulo"
            elif objCor == 4: 
                aspRatio = w / float(h)
                if aspRatio > 0.95 and aspRatio < 1.05: objectType = "Quadrado"
                else: objectType = "Retangulo"

            elif objCor > 4: objectType = "Circles"
            else: objectType = "None"

            cv2.rectangle(imgContour, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(imgContour, objectType, 
            (x + (w // 2) - 10, y + (h // 2) - 10), cv2.FONT_HERSHEY_COMPLEX, 0.7,
            (0, 0, 0), 2)

def face_detect():
    faceCascade = cv2.CascadeClassifier("Resources/haarcascades/haarcascade_frontalface_default.xml")
    img = cv2.imread("Resources/familia.png")
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(imgGray, 1.1, 4)
    
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)


    cv2.imshow("Result", img)
    cv2.waitKey(0)

# Valores para filtrar cores
myColors = [[95, 120 , 114, 121, 255, 190], [123, 83, 112, 154, 163, 255], [0, 128, 139, 19, 255, 239]]
myColorsValues = [[153, 0, 0], [153, 0, 153], [0, 128, 255]] ## BGR
myPoints = [] ## [x, y, colorId]

def color_picker():
    frameWidth = 640
    frameHeight = 480
    cap = cv2.VideoCapture(0)
    cap.set(3, frameWidth)
    cap.set(4, frameHeight)

    cv2.namedWindow("HSV")
    cv2.resizeWindow("HSV", 640, 240)
    cv2.createTrackbar("HUE Min", "HSV", 0, 179, empty)
    cv2.createTrackbar("HUE Max", "HSV", 179, 179, empty)
    cv2.createTrackbar("SAT Min", "HSV", 0, 255, empty)
    cv2.createTrackbar("SAT Max", "HSV", 255, 255, empty)
    cv2.createTrackbar("VALUE Min", "HSV", 0, 255, empty)
    cv2.createTrackbar("VALUE Max", "HSV", 255, 255, empty)
 
 
    while True:
    
        success, img = cap.read()
        imgHsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
        h_min = cv2.getTrackbarPos("HUE Min", "HSV")
        h_max = cv2.getTrackbarPos("HUE Max", "HSV")
        s_min = cv2.getTrackbarPos("SAT Min", "HSV")
        s_max = cv2.getTrackbarPos("SAT Max", "HSV")
        v_min = cv2.getTrackbarPos("VALUE Min", "HSV")
        v_max = cv2.getTrackbarPos("VALUE Max", "HSV")
        # print(h_min)
 
        lower = np.array([h_min, s_min, v_min])
        upper = np.array([h_max, s_max, v_max])
        mask = cv2.inRange(imgHsv, lower, upper)
        result = cv2.bitwise_and(img, img, mask=mask)
    
        mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        hStack = np.hstack([img, mask, result])
        cv2.imshow('Horizontal Stacking', hStack)
        if cv2.waitKey(1) & 0xFF == ord(' '):
            break
 
    cap.release()
    cv2.destroyAllWindows()

def findColor(img, myColors, imgResult, myColorsValues):
    
    imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    count = 0
    newPoints = []
    for color in myColors:
        lower = np.array(color[0:3])
        upper = np.array(color[3:6])
        mask = cv2.inRange(imgHSV, lower, upper)
        x, y = getContoursPaint(mask, imgResult)
        cv2.circle(imgResult, (x, y), 10, myColorsValues[count], cv2.FILLED)
        # cv2.imshow(str(color[0]), mask)
        if x != 0 and y != 0:
            newPoints.append([x, y, count])
        count += 1
    return newPoints

def find_color():
    
    frameWidth = 640
    frameHeight = 480
    cap = cv2.VideoCapture(0)
    # seta resoluçao
    cap.set(3, frameWidth)
    cap.set(4, frameHeight)
    cap.set(10, 150)

    # mostra vídeo até clicar a tecla 'espaço'
    while True:
        success, img = cap.read()
        imgResult = img.copy()
        newPoints = findColor(img, myColors, imgResult, myColorsValues)
        if len(newPoints) != 0:
            for newP in newPoints:
                myPoints.append(newP)
        if len(myPoints) != 0:
            drawOnCanvas(myPoints, myColorsValues, imgResult)

        cv2.imshow("Result", imgResult)
        if cv2.waitKey(1) & 0xFF == ord(' '):
            break

def getContoursPaint(img, imgResult):
    # Pelo que entendi o atributo RETR_EXTERNAL define que queremos o contorno da imagem  de acordo com o filtro
    contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    x, y, w, h = 0, 0, 0, 0
    for cnt in contours:
        area = cv2.contourArea(cnt)
        # print(area)
        # Threshold
        if area > 500:
            # cv2.drawContours(imgResult, cnt,-1,(255, 0, 0), 3)
            peri = cv2.arcLength(cnt, True)
            # aproxima o formato da imagem, encontra os vértices
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            x, y, w, h = cv2.boundingRect(approx)
    return x + w // 2, y

def drawOnCanvas(myPoints, myColorsValues, imgResult):
    for point in myPoints:
        cv2.circle(imgResult, (point[0], point[1]), 10, myColorsValues[point[2]], cv2.FILLED)

#Funções para digitalizar documento
widthImg = 480
heightImg = 640
def getContoursDoc(img, imgContour):
    # Pelo que entendi o atributo RETR_EXTERNAL define que queremos o contorno da imagem  de acordo com o filtro
    biggest = np.array([])
    contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    maxArea = 0
    for cnt in contours:
        area = cv2.contourArea(cnt)
        # Threshold
        if area > 5000:
            # cv2.drawContours(imgContour, cnt,-1,(255, 0, 0), 3)
            peri = cv2.arcLength(cnt, True)
            # print(peri)
            # aproxima o formato da imagem, encontra os vértices
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            if area > maxArea and len(approx) == 4:
                biggest = approx
                maxArea = area
    cv2.drawContours(imgContour, biggest,-1,(255, 0, 0), 20)
    return biggest

def getWarp(img, biggest):
    biggest = reorder(biggest)
    pts1 = np.float32(biggest)
    pts2 = np.float32([[0, 0], [widthImg, 0], [0, heightImg], [widthImg, heightImg]])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    imgOutput = cv2.warpPerspective(img, matrix, (widthImg, heightImg))
    return imgOutput

# Reorganiza os pontos de contorno do documento para poder cortar corretamente
def reorder(myPoints):
    myPoints = myPoints.reshape((4, 2))
    myPointsNew = np.zeros((4, 1, 2), np.int32)
    add = myPoints.sum(1)
    #print("add", add)
    myPointsNew[0] = myPoints[np.argmin(add)]
    myPointsNew[3] = myPoints[np.argmax(add)]
    diff = np.diff(myPoints, axis=1)
    myPointsNew[1] = myPoints[np.argmin(diff)]
    myPointsNew[2] = myPoints[np.argmax(diff)]
    return myPointsNew

def preProcessing(img):
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1)
    imgCanny = cv2.Canny(imgBlur, 200, 200)
    kernel = np.ones((5, 5))
    imgDial = cv2.dilate(imgCanny, kernel, iterations=2)
    imgThres = cv2.erode(imgDial, kernel, iterations=1)
    return imgThres

def doc_scanner():
    cap = cv2.VideoCapture(0)
    cap.set(3, widthImg)
    cap.set(4, heightImg)
    cap.set(10, 150)
    while True:
        success, img = cap.read()
        img = cv2.resize(img, (widthImg, heightImg))
        imgContour = img.copy()
        imgThres = preProcessing(img)
        biggest = getContoursDoc(imgThres, imgContour)
        print(biggest)
        imgWarped = getWarp(img, biggest)
        cv2.imshow("Result", imgWarped)
        if cv2.waitKey(1) & 0xFF == ord(' '):
            break

''' Para executar remova o comentário. Lista de funções: '''
# read_image()
# read_video()
# web_cam()
# basic_functions()
# resize()
# cropped()
# draw()
# warp()
# stack_images()
# detect_color()
# detect_shapes()
# face_detect()
# find_color()
# color_picker()

''' Está função não funcionou corretamente, precisa de correção.'''
# doc_scanner()