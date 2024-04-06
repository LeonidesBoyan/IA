import cv2
import cvzone
from cvzone.FaceMeshModule import FaceMeshDetector
from cvzone.PlotModule import LivePlot
import time

cap = cv2.VideoCapture('Video.mp4')  # capture from video/0/'Video.mp4'
detector = FaceMeshDetector(maxFaces=1)
plotY = LivePlot(640, 360, [20, 50], invert=True)  # invert=True, invierte la tendencia plot

idList = [22, 23, 24, 26, 110, 157, 158, 159, 160, 161, 130, 243]  # nro. puntos (los que estan: COLOR ROSA)
ratioList = []

#impresion de colores
color = (255, 0, 255)

#varible for Micro_Sleep
microsleepStart = 0
endMicrosleep = 0
microsleepDuration = 0
microsleepCounter = 0

#variable for blink counter
last_blink_time = time.time()
blinkCounter = 0

while True:

    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    success, img = cap.read()
    img, faces = detector.findFaceMesh(img, draw=False)  # draw=False desactiva el dibujo de mascara

    if faces:
        face = faces[0]
        for id in idList:
            cv2.circle(img, face[id], 5, color, cv2.FILLED)

        leftUp = face[159]
        leftDown = face[23]
        leftLeft = face[130]
        leftRight = face[243]
        lenghtVer, _ = detector.findDistance(leftUp, leftDown)  # mide la longitud vertical
        lenghtHor, _ = detector.findDistance(leftLeft, leftRight)  # mide la longitud horizontal

        cv2.line(img, leftUp, leftDown, (0, 200, 0), 3)  # impresion de linea verde Lenght - 3 es el valor: ancho
        cv2.line(img, leftLeft, leftRight, (0, 200, 0), 3)  # impresion de linea verde Lenght - 3 es el valor: ancho

        ratio = int((
            lenghtVer / lenghtHor) * 100)  # impresion de valores longitud por terminal - int convierte el valor en entero
        ratioList.append(ratio)
        if len(ratioList) > 3:  # dimensiona el lenght tendencia, a mayor nro. menor detalle
            ratioList.pop(0)
        ratioAvg = sum(ratioList) / len(ratioList)





        if ratioAvg < 33 and microsleepStart == 0:  # inicio de microsueño
            microsleepStart = time.time()
        elif ratioAvg >= 33 and microsleepStart != 0:  # fin de microsueño
            endMicrosleep = time.time() #inicializacion de varible endMicrosleep
            microsleepDuration = round(endMicrosleep - microsleepStart, 2) #redondeo 2 decimales
            if microsleepDuration >= 1:  # considera microsueño si dura al menos 1 segundo
                microsleepCounter += 1

                microsleepStart = time.time()  # reinicia el tiempo de inicio sin modificar el contador
            else:
                microsleepStart = 0  # reinicia el tiempo de inicio si no se cumple la duración
                microsleepDuration = 0  # reinicia la duración si no se cumple la duración




        # Lógica para contar parpadeos basados en el tiempo
        if ratioAvg < 33:
            current_time = time.time() #se crea la variable current_time - tiempo actual

            if current_time - last_blink_time > 0.5:  # Si han pasado más de 0.5 segundo desde el último parpadeo
                blinkCounter += 1
                color = (0, 200, 0)  # Color verde
                last_blink_time = current_time  # Actualizar el tiempo del último parpadeo






        cvzone.putTextRect(img, f'Blink Contador: {blinkCounter}', (70, 100),
                           colorR=color)  # imprime el nro de blink "conteo" por pantalla (blink counter)
        cvzone.putTextRect(img, f'MicroSleep : {microsleepCounter}', (70, 160))  # imprime el nro de microsueños por pantalla

        imgPlot = plotY.update(ratioAvg, color)
        img = cv2.resize(img, (648, 360))  # este comando dimensiona la imagen del video
        imgStack = cvzone.stackImages([img, imgPlot], 2, 1)  # imagePlot : tendencia
    else:
        img = cv2.resize(img, (648, 360))  # este comando dimensiona la imagen del video
        imgStack = cvzone.stackImages([img, img], 2, 1)  # imagePlot : tendencia

    cv2.imshow("Image", imgStack)
    cv2.waitKey(25)  # reproduccion del tiempo
