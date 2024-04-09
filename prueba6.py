# Bibliotecas estándar
import time
import threading

# Bibliotecas de terceros
import cv2
from cvzone.FaceMeshModule import FaceMeshDetector
from cvzone.PlotModule import LivePlot
import pygame.mixer

# Alias cortos para las bibliotecas
import cvzone as cvz
import pygame.mixer as mixer

# Inicialización de la biblioteca de audio
mixer.init()
alarma_audio = mixer.Sound("Alarma.mp3")

ARCHIVO_VIDEO = 'Video.mp4'
PUNTOS_ROSTRO = [22, 23, 24, 26, 110, 157, 158, 159, 160, 161, 130, 243]
UMBRAL_MICROSUEÑO = 33
INTERVALO_PARPADEO = 0.5
DURACION_MICROSUEÑO = 2
DURACION_ALARMA = 3

# Inicialización de la captura de video, detector de rostros y gráfica en vivo
cap = cv2.VideoCapture(ARCHIVO_VIDEO)
detector = FaceMeshDetector(maxFaces=1)
plotY = LivePlot(640, 360, [20, 50], invert=True)

fps = cap.get(cv2.CAP_PROP_FPS)
tiempo_fotograma = 1.0 / fps if fps > 0 else 0

alarma_cargada = False

def cargar_alarma():
    global alarma_audio, alarma_cargada
    alarma_audio = mixer.Sound("Alarma.mp3")
    alarma_cargada = True

def detectar_rostro():
    success, img = cap.read()
    img, faces = detector.findFaceMesh(img, draw=False)
    return img, faces

def calcular_ratio_promedio(face):
    lista_ratios = []
    for id in PUNTOS_ROSTRO:
        lista_ratios.append(int(detector.findDistance(face[159], face[23])[0] / detector.findDistance(face[130], face[243])[0] * 100))
    return sum(lista_ratios[-3:]) / min(len(lista_ratios), 3)

def mostrar_texto(img, contador_parpadeo, contador_microsueño, color_parpadeo):
    color_microsueno1 = (255, 0, 0)
    color_microsueno2 = (0, 0, 255)
    cvz.putTextRect(img, f'Cont. Blink: {contador_parpadeo}', (70, 100), colorR=color_parpadeo)
    if contador_microsueño == 0:
        cvz.putTextRect(img, f'Cont. MicroBlink: {contador_microsueño}', (70, 160), colorR=color_microsueno1)
    else:
        cvz.putTextRect(img, f'Cont. MicroBlink: {contador_microsueño}', (70, 160), colorR=color_microsueno2)

def reproducir_alarma():
    global alarma_audio
    if not alarma_cargada:
        cargar_alarma()
    alarma_audio.play()
    tiempo_inicio = time.time()
    while time.time() - tiempo_inicio < DURACION_ALARMA:
        pass  # Esperar a que termine la alarma
    alarma_audio.stop()

def main():
    microsueño_inicio = 0
    ultimo_tiempo_parpadeo = time.time()
    contador_parpadeo = 0
    contador_microsueño = 0
    color_parpadeo = (255, 0, 255)

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
                threading.Thread(target=reproducir_alarma).start()
                contador_microsueño = 0

            imgPlot = plotY.update(ratio_promedio, color_parpadeo)
            img = cv2.resize(img, (648, 360))
            imgStack = cvz.stackImages([img, imgPlot], 2, 1)
        else:
            img = cv2.resize(img, (648, 360))
            imgStack = cvz.stackImages([img, img], 2, 1)

        tiempo_espera = int(tiempo_fotograma * 1000)
        cv2.imshow("Image", imgStack)
        cv2.waitKey(tiempo_espera)

if __name__ == "__main__":
    main()
