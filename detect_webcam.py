from ultralytics import YOLO
import cv2

# Charger le modèle pré-entraîné
model = YOLO("yolov8s.pt")

# Liste des classes de fruits (par ID COCO)
FRUIT_CLASSES = [46, 47, 49]  # banana, apple,  orange

# Ouvrir la webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Erreur: webcam non trouvée")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Erreur: impossible de lire l'image de la webcam")
        break

    # Prédiction
    results = model(frame, stream=True)

    # Parcourir les détections
    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])  # identifiant de la classe
            conf = float(box.conf[0]) # confiance
            name = model.names[cls_id]

            # ✅ Afficher uniquement les fruits
            if cls_id in FRUIT_CLASSES and conf > 0.5:
                # Dessiner la boîte et le label
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{name} {conf:.2f}",
                            (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    cv2.imshow("🍌 Détection Fruits uniquement 🍎", frame)

    # Quitter avec 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
