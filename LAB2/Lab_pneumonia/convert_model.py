"""
Script de conversion du modèle Keras 3.x vers un format compatible
"""
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

print("🔄 Conversion du modèle en cours...")

# Installer temporairement tensorflow 2.20 pour charger le modèle Keras 3
import subprocess
import sys

print("📦 Installation TensorFlow 2.20 temporaire...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "tensorflow==2.20.0"])

print("📥 Chargement du modèle avec Keras 3...")
import tensorflow as tf

model_path = "streamlit/model/pneumonia_classifier.h5"
model = tf.keras.models.load_model(model_path)

print(f"✅ Modèle chargé: {model.name}")
print(f"📊 Input shape: {model.input_shape}")
print(f"📊 Output shape: {model.output_shape}")

# Sauvegarder en format SavedModel (compatible toutes versions)
output_path = "streamlit/model/pneumonia_model_saved"
print(f"💾 Sauvegarde en SavedModel format: {output_path}")
model.save(output_path, save_format='tf')

print("✅ Conversion terminée!")
print(f"📁 Nouveau modèle: {output_path}")
print("\n🔄 Restauration de TensorFlow 2.15...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "tensorflow-macos==2.15.0", "keras==2.15.0"])

print("\n✨ Tout est prêt! Le modèle est maintenant compatible.")
