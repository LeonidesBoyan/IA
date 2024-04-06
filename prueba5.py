import cv2
import cvzone
from cvzone.FaceMeshModule import FaceMeshDetector
from cvzone.PlotModule import LivePlot
import time
import pygame.mixer
import threading  # Importar el módulo threading

pygame.mixer.init()
alarma_audio = pygame.mixer.Sound("Alarma.mp3")

# Parámetros y constantes
ARCHIVO_VIDEO = 'Video.mp4'  # 0 - 'Video.mp4'
PUNTOS_ROSTRO = [22, 23, 24, 26, 110, 157, 158, 159, 160, 161, 130, 243]
UMBRAL_MICROSUEÑO = 33
INTERVALO_PARPADEO = 0.5
DURACION_MICROSUEÑO = 2
DURACION_ALARMA = 3

cap = cv2.VideoCapture(ARCHIVO_VIDEO)
detector = FaceMeshDetector(maxFaces=1)
plotY = LivePlot(640, 360, [20, 50], invert=True)

# Obtener la duración de un fotograma en segundos
fps = cap.get(cv2.CAP_PROP_FPS)
tiempo_fotograma = 1.0 / fps if fps > 0 else 0


def detectar_rostro():
    success, img = cap.read()
    img, faces = detector.findFaceMesh(img, draw=True)
    return img, faces


def calcular_ratio_promedio(face):
    lista_ratios = []
    for id in PUNTOS_ROSTRO:
        lista_ratios.append(
            int(detector.findDistance(face[159], face[23])[0] / detector.findDistance(face[130], face[243])[0] * 100))
    return sum(lista_ratios[-3:]) / min(len(lista_ratios), 3)


def mostrar_texto(img, contador_parpadeo, contador_microsueño, color_parpadeo):
    color_microsueno1 = (255, 0, 0)  # (255,0,0)
    color_microsueno2 = (0, 0, 255)  #
    cvzone.putTextRect(img, f'Cont. Blink: {contador_parpadeo}', (70, 100), colorR=color_parpadeo)
    if contador_microsueño == 0:
        cvzone.putTextRect(img, f'Cont. MicroBlink: {contador_microsueño}', (70, 160), colorR=color_microsueno1)
    else:
        cvzone.putTextRect(img, f'Cont. MicroBlink: {contador_microsueño}', (70, 160), colorR=color_microsueno2)


def reproducir_alarma():
    alarma_audio.play()
    tiempo_inicio = time.time()
    while time.time() - tiempo_inicio < DURACION_ALARMA:
        if time.time() - tiempo_inicio > DURACION_ALARMA:
            alarma_audio.stop()


def main():
    microsueño_inicio = 0
    ultimo_tiempo_parpadeo = time.time()
    contador_parpadeo = 0
    contador_microsueño = 0

    # color = (255, 0, 255)  # Asignar valor inicial a color
    color_parpadeo = (255, 0, 255)
    color_microsueno = (255, 0, 255)
    while True:
        if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        img, faces = detectar_rostro()
        if faces:
            face = faces[0]
            for id in PUNTOS_ROSTRO:
                cv2.circle(img, face[id], 5, (255, 0, 255), cv2.FILLED)

            ratio_promedio = calcular_ratio_promedio(face)

            if ratio_promedio < UMBRAL_MICROSUEÑO:
                tiempo_actual = time.time()
                if microsueño_inicio == 0:
                    microsueño_inicio = tiempo_actual
                elif tiempo_actual - microsueño_inicio >= DURACION_MICROSUEÑO:
                    contador_microsueño += 1
                    microsueño_inicio = tiempo_actual
                elif tiempo_actual - ultimo_tiempo_parpadeo > INTERVALO_PARPADEO:
                    contador_parpadeo += 1
                    color_parpadeo = (0, 200, 0)
                    ultimo_tiempo_parpadeo = tiempo_actual
            else:
                microsueño_inicio = 0

            mostrar_texto(img, contador_parpadeo, contador_microsueño, color_parpadeo)

            if contador_microsueño == 2:
                # Ejecutar la función reproducir_alarma en un hilo separado
                threading.Thread(target=reproducir_alarma).start()
                contador_microsueño = 0

            imgPlot = plotY.update(ratio_promedio, color_parpadeo)
            img = cv2.resize(img, (648, 360))
            imgStack = cvzone.stackImages([img, imgPlot], 2, 1)
        else:
            img = cv2.resize(img, (648, 360))
            imgStack = cvzone.stackImages([img, img], 2, 1)

        # Calcular el tiempo de espera para mantener la velocidad real del video
        tiempo_espera = int(tiempo_fotograma * 1000)  # Convertir a milisegundos
        cv2.imshow("Image", imgStack)
        cv2.waitKey(tiempo_espera)


if __name__ == "__main__":
    main()
