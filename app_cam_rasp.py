import cv2
import requests
# Define a ROI (retângulo)
thickness_box = 2

color_box = (0, 255, 0)  # verde

boundryBoxesMontagem = {       
    "right1":  {"coord": [(481, 167, 620, 291)]},
    "right2":  {"coord": [(648, 168, 784, 295)]},
    "right3":  {"coord": [(476, 343, 612, 470)]},
    "right4":  {"coord": [(643, 348, 777, 471)]},
    "left1": {"coord": [(87, 158, 226, 290)]},
    "left2": {"coord": [(251, 163, 391, 291)]},
    "left3": {"coord": [(79, 341, 221, 473)]},
    "left4": {"coord": [(243, 340, 388, 468)]},      }


POST_URL = "http://172.16.10.175:81/visao"  # seu endpoint

# Função para identificar forma geométrica pelo contorno
def identificar_forma(contorno):
    peri = cv2.arcLength(contorno, True)
    approx = cv2.approxPolyDP(contorno, 0.06 * peri, True)
    vertices = len(approx)
    if vertices == 3:
        return "triangulo"
    elif vertices == 4:
        return "quadrado"
    elif vertices == 5:
        return "pentagono"
    elif vertices == 6:
        return "hexagono"
    elif vertices == 10:
        return "decagono"
    else:
        return "circulo"
# Tenta abrir a câmera padrão (0)
cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

cap.set(cv2.CAP_PROP_AUTOFOCUS, 0) 

# Set a specific focus value (e.g., 200)
# The range of values depends on the camera
cap.set(cv2.CAP_PROP_FOCUS, 200)
if not cap.isOpened():
    print("❌ Erro ao abrir a câmera.")
    exit()

last_detections ={}

while True:
    ret, frame = cap.read()

    if not ret:
        print("❌ Falha ao capturar frame.")
        break

# Inverte a imagem (se necessário)
    frame = cv2.flip(frame, -1)

    # Escurece um pouco (para evitar estouro de luz)
    frame = cv2.convertScaleAbs(frame, alpha=1.0, beta=-60)

    # Converte para escala de cinza e aplica filtro
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)

    # Threshold adaptativo (inverte: figuras pretas → brancas)
    thresh = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 5
    )

    # Converte imagem binária para BGR antes de desenhar o retângulo colorido
    thresh_bgr = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

    # Desenha o retângulo verde


        # Primeiro, desenha todas as bounding boxes fixas
    for classe, dados in boundryBoxesMontagem.items():
        for bbox in dados["coord"]:
            x0, y0, x1, y1 = bbox
            cv2.rectangle(thresh_bgr, (x0, y0), (x1, y1), color_box, thickness_box)
            cv2.putText(thresh_bgr, classe, (x0, y0-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_box, 2)
            frame = cv2.cvtColor(thresh_bgr, cv2.COLOR_BGR2RGB)

    detections = {}
    #cv2.rectangle(thresh_bgr, (x0, y0), (x1, y1), color, thickness)
    for classe, dados in boundryBoxesMontagem.items():
        for bbox in dados["coord"]:
            x0, y0, x1, y1 = bbox
            roi = thresh[y0:y1, x0:x1]
            
            #contornos, _ = cv2.findContours(roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contornos, _ = cv2.findContours(roi, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            forma = None
            for c in contornos:
                if cv2.contourArea(c) > 200:
                    forma = identificar_forma(c)
                    # Escreve a forma detectada na ROI
                    cv2.putText(frame, forma, (x0, y0-30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)
            detections[classe] = forma

    if last_detections != detections:
        try:
            response = requests.post(POST_URL, json=detections, timeout=2)
            print("POST enviado:", response.status_code, detections)
        except Exception as e:
            print("Erro ao enviar POST:", e)
        last_detections = detections.copy()
    # Mostra o frame
    
    #cv2.imshow("Inspeção Live", frame)

    # Exibe o frame em uma janela
    cv2.imshow("Camera - Teste", frame)

    # Sai se apertar a tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libera a câmera e fecha as janelas
cap.release()
cv2.destroyAllWindows()
