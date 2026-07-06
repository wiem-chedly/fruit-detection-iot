from ultralytics import YOLO   # Importe la bibliothèque YOLO d'Ultralytics pour la détection d'objets
import yaml                     # Importe PyYAML pour lire et manipuler les fichiers YAML
import os                       # Importe le module os pour interagir avec le système de fichiers

# Charger le fichier data.yaml
data_path = "/content/drive/MyDrive/Fruits_YOLO/data.yaml"  # Définit le chemin vers le fichier data.yaml
with open(data_path, 'r') as f:           # Ouvre le fichier en mode lecture ('r') et l'assigne à la variable f
    data = yaml.safe_load(f)                # Lit le contenu YAML et le convertit en dictionnaire Python

# Vérifier les chemins
print("✅ Chemins :")
print("Train:", data['train'])  # Affiche le chemin du dossier des images d'entraînement
print("Val:", data['val'])      # Affiche le chemin du dossier des images de validation

# Vérifier les classes
print("\n✅ Classes :")
for k, v in data['names'].items():  # Parcourt le dictionnaire des classes (clé = ID, valeur = nom)
    print(f"{k}: {v}")              # Affiche chaque ID et le nom de la classe

# Vérifier si les dossiers existent et contiennent des images
for split in ['train', 'val']:         # Boucle sur les deux splits : train et val
    folder = data[split]              # Récupère le chemin du dossier correspondant
    if os.path.exists(folder):       # Vérifie si le dossier existe sur le disque
        print(f"\n✅ {split} contient {len(os.listdir(folder))} fichiers")  
        # Si oui, compte le nombre de fichiers dans le dossier et l'affiche
    else:
        print(f"\n❌ Dossier {folder} non trouvé !")  
        # Si non, affiche un message d'erreur indiquant que le dossier est introuvable
