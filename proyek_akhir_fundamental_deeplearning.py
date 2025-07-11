# -*- coding: utf-8 -*-
"""Copy of proyek akhir fundamental deeplearning.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Tb63O5fJaOLYHnmeHxAeJes7s4FRWeci

# Proyek Klasifikasi Gambar: Nordstrom & Myntra Clothes Image Data - GarmentIQ
- **Nama:** Muhammad Elfikry
- **Email:** melfikry@gmail.com
- **ID Dicoding:** muhammadelfikry

## Import Semua Packages/Library yang Digunakan
"""

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Conv2D, MaxPooling2D, Flatten, Dropout, BatchNormalization
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from PIL import Image
from skimage import io
from skimage.transform import resize
from skimage.transform import rotate, AffineTransform, warp
from skimage import img_as_ubyte
from skimage.exposure import adjust_gamma
from skimage.util import random_noise
from google.colab import files
from re import sub
import random
import skimage
import cv2
import tensorflow as tf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import shutil

"""## Data Preparation

### Data Loading
"""

files.upload()

! mkdir -p ~/.kaggle
! cp kaggle.json ~/.kaggle/
! chmod 600 ~/.kaggle/kaggle.json
! kaggle datasets download -d lygitdata/garmentiq-classification-set-nordstrom-and-myntra

metadata = pd.read_csv("metadata.csv")
metadata.head()

category_name = metadata["garment"].unique()
category_name

for category in category_name:
  os.makedirs("dataset/images/" + category, exist_ok=True)

file_category = metadata.groupby(by="garment")["filename"]

for category, files_name in file_category:
  for file in files_name:
    shutil.copyfile("images/" + file, "dataset/images/" + category + "/" + file)

  print(category + " done")

fig, axs = plt.subplots(len(os.listdir("dataset/images/")), 5, figsize=(15, 15))
for i, category in enumerate(os.listdir("dataset/images/")):
  files = os.listdir("dataset/images/" + category)
  for j in range(5):
    img = plt.imread("dataset/images/" + category + "/" + files[np.random.randint(0, len(files))])
    axs[i, j].imshow(img)
    axs[i, j].set_title(category)
    axs[i, j].axis("off")
plt.show()

fig, axs = plt.subplots(1, 2, figsize=(15, 5))

category_counts = {}
for category in os.listdir("dataset/images/"):
  category_counts[category] = len(os.listdir("dataset/images/" + category))

axs[0].bar(category_counts.keys(), category_counts.values())
axs[0].set_title("Distribution of Garment")
axs[0].set_xticks(range(len(category_counts.keys())))
axs[0].set_xticklabels(category_counts.keys(), rotation=90)

axs[1].pie(category_counts.values(), labels=category_counts.keys(), autopct="%1.1f%%")
axs[1].set_title("Percentage of Garment")

plt.tight_layout()
plt.show()

def print_image_resolution(directory):
  unique_sizes = set()
  total_images = 0

  for subdir in os.listdir(directory):
    subdir_path = os.path.join(directory, subdir)
    image_files = os.listdir(subdir_path)
    num_images = len(image_files)
    print(f"{subdir}: {num_images}")
    total_images += num_images

    for img_file in image_files:
      img_path = os.path.join(subdir_path, img_file)
      with Image.open(img_path) as img:
        unique_sizes.add(img.size)

    for size in unique_sizes:
      print(f"- {size}")
    print("---------------")

  print(f"\nTotal: {total_images}")

print_image_resolution("dataset/images/")

"""### Data Preprocessing

#### Split Dataset
"""

dataset_path = "dataset/images/"

file_name = []
labels = []
full_path = []

for path, subdirs, files_image in os.walk(dataset_path):
  for name in files_image:
    file_name.append(name)
    labels.append(path.split("/")[-1])
    full_path.append(os.path.join(path, name))

df = pd.DataFrame({"path": full_path, "file_name": file_name, "label": labels})
df.groupby(["label"]).size()

X = df["path"]
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
X_test, X_val, y_test, y_val = train_test_split(X_test, y_test, test_size=0.5, random_state=42)

df_tr = pd.DataFrame({"path": X_train, "label": y_train, "set": "train"})
df_te = pd.DataFrame({"path": X_test, "label": y_test, "set": "test"})
df_va = pd.DataFrame({"path": X_val, "label": y_val, "set": "validation"})

df_all = pd.concat([df_tr, df_te, df_va], ignore_index=True)
df_all.groupby(["label", "set"]).size()

df_all.sample(5)

for _, row in df_all.iterrows():
  source_path = row["path"]
  dest_dir = os.path.join("dataset", "final_dataset", row["set"], row["label"])
  os.makedirs(dest_dir, exist_ok=True)

  filename = os.path.basename(source_path)
  dest_path = os.path.join(dest_dir, filename)

  try:
    shutil.copyfile(source_path, dest_path)
  except Exception as e:
    print(f"Error copying {source_path} to {dest_path}: {e}")

"""#### Data Augmentation"""

train_dir = "dataset/final_dataset/train/"

fig, axs = plt.subplots(1, 2, figsize=(15, 5))

category_counts = {}
for category in os.listdir(train_dir):
  category_counts[category] = len(os.listdir(train_dir + category))

plt.suptitle("Train Dataset (before augmentation)", fontsize=16)

axs[0].bar(category_counts.keys(), category_counts.values())
axs[0].set_title("Distribution of Garment")
axs[0].set_xticks(range(len(category_counts.keys())))
axs[0].set_xticklabels(category_counts.keys(), rotation=90)

axs[1].pie(category_counts.values(), labels=category_counts.keys(), autopct="%1.1f%%")
axs[1].set_title("Percentage of Garment")

plt.tight_layout()
plt.show()

def anticlockwise_rotation(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (224,224))
    sudut = random.randint(5, 20)
    return rotate(img, sudut)

def clockwise_rotation(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (224,224))
    sudut = random.randint(5, 20)
    return rotate(img, -sudut)

def sheared(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (224,224))
    transform = AffineTransform(shear=0.2)
    shear_image = warp(img, transform, mode="wrap")
    return shear_image

transformation = {
    "anticlockwise_rotation": anticlockwise_rotation,
    "clockwise_rotation": clockwise_rotation,
    "sheared": sheared,
}

category_to_augment = ['skirt', 'vest','long sleeve dress',
                       'short sleeve dress', 'trousers']

images_path = "dataset/final_dataset/train/"
augmented_path = "dataset/augmented"
os.makedirs(augmented_path, exist_ok=True)

for category in category_to_augment:
  os.makedirs(augmented_path + "/" + category, exist_ok=True)

images_to_generate = {
    "skirt": 1000,
    "vest": 1000,
    "trousers": 500,
    "short sleeve dress": 300,
    "long sleeve dress": 500
}
i = 1

for category in category_to_augment:
  print(f"Augmenting category: {category}")
  images = []

  for im in os.listdir(images_path + category):
    images.append(images_path + category + "/" + im)

  while i <= images_to_generate[category]:
    image = random.choice(images)
    original_image = io.imread(image)
    transformed_image = None
    n = 0
    transformation_count = random.randint(1, len(transformation))

    while n < transformation_count:
      key = random.choice(list(transformation))
      transformed_image = transformation[key](original_image)
      n += 1

    new_file_path = "%s/augmented_image_%s.jpg" % (augmented_path + "/" + category, i)
    transformed_image = img_as_ubyte(transformed_image)
    cv2.imwrite(new_file_path, transformed_image)

    i += 1
  i = 1
  print(f"Augmented category: {category} done")

# # delete final folder
# shutil.rmtree("dataset/final_dataset")

fig, axs = plt.subplots(len(os.listdir("dataset/augmented/")), 5, figsize=(15, 15))
for i, category in enumerate(os.listdir("dataset/augmented/")):
  files = os.listdir("dataset/augmented/" + category)
  for j in range(5):
    img = plt.imread("dataset/augmented/" + category + "/" + files[np.random.randint(0, len(files))])
    axs[i, j].imshow(img)
    axs[i, j].set_title(category)
    axs[i, j].axis("off")
plt.show()

final_path = "dataset/final_dataset/train_with_augmentation/"
os.makedirs(final_path, exist_ok=True)

for category in category_name:
  os.makedirs(final_path + category, exist_ok=True)
  for im in os.listdir(images_path + category):
    shutil.copyfile(images_path + category + "/" + im, final_path + category + "/" + im)
  print(f"{category} done")

for category in category_to_augment:
  os.makedirs(final_path + category, exist_ok=True)
  for im in os.listdir(augmented_path + "/" + category):
    shutil.copyfile(augmented_path + "/" + category + "/" + im, final_path + category + "/" + im)
  print(f"{category} (augmented) done")

shutil.rmtree("dataset/final_dataset/train")
print("remove train folder")

print("All done")

train_with_augmentation_dir = "dataset/final_dataset/train_with_augmentation/"

fig, axs = plt.subplots(1, 2, figsize=(15, 5))

category_counts = {}
for category in os.listdir(train_with_augmentation_dir):
  category_counts[category] = len(os.listdir(train_with_augmentation_dir + category))

plt.suptitle("Train Dataset (after augmentation)", fontsize=16)

axs[0].bar(category_counts.keys(), category_counts.values())
axs[0].set_title("Distribution of Garment")
axs[0].set_xticks(range(len(category_counts.keys())))
axs[0].set_xticklabels(category_counts.keys(), rotation=90)

axs[1].pie(category_counts.values(), labels=category_counts.keys(), autopct="%1.1f%%")
axs[1].set_title("Percentage of Garment")

plt.tight_layout()
plt.show()

TRAIN_DIR = "dataset/final_dataset/train_with_augmentation/"
VAL_DIR = "dataset/final_dataset/validation/"
TEST_DIR = "dataset/final_dataset/test/"

train_datagen = ImageDataGenerator(rescale=1 / 255.,
                                   horizontal_flip=True)

val_datagen = ImageDataGenerator(rescale=1 / 255.)

test_datagen = ImageDataGenerator(rescale=1 / 255.)

train_generator = train_datagen.flow_from_directory(TRAIN_DIR,
                                              batch_size=32,
                                              target_size=(150,150),
                                              color_mode="grayscale",
                                              class_mode='categorical',
                                              shuffle=True)

validation_generator = val_datagen.flow_from_directory(VAL_DIR,
                                                       batch_size=32,
                                                       target_size=(150,150),
                                                       color_mode="grayscale",
                                                       class_mode='categorical',
                                                       shuffle=False)

test_generator = test_datagen.flow_from_directory(TEST_DIR,
                                                  batch_size=1,
                                                  target_size=(150,150),
                                                  color_mode="grayscale",
                                                  class_mode='categorical',
                                                  shuffle=False)

"""## Modelling"""

class MyCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if (logs.get("accuracy") > 0.95) and (logs.get("val_accuracy") > 0.95):
      print("\nReached 95% accuracy so cancelling")
      self.model.stop_training = True

callbacks = MyCallback()
early_stopping = tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=20, restore_best_weights=True)

model = Sequential([
    Conv2D(32, (3, 3), padding="same", activation="relu", input_shape=(150, 150, 1)),
    MaxPooling2D(2, 2),
    Conv2D(64, (3, 3), padding="same", activation="relu"),
    MaxPooling2D(2, 2),
    Flatten(),
    Dense(128, activation="relu"),
    Dropout(0.5),
    Dense(64, activation="relu"),
    Dropout(0.3),
    Dense(len(os.listdir(TRAIN_DIR)), activation="softmax")
])

model.compile(optimizer=tf.keras.optimizers.Adam(),
                 loss="categorical_crossentropy",
                 metrics=["accuracy"])

print(model.summary())

history = model.fit(train_generator,
                    epochs=50,
                    steps_per_epoch=685,
                    validation_data=validation_generator,
                    validation_steps=729,
                    callbacks=[callbacks, early_stopping])

"""## Evaluasi dan Visualisasi"""

acc_model = history.history["accuracy"]
val_acc_model = history.history["val_accuracy"]
loss_model= history.history["loss"]
val_loss_model = history.history["val_loss"]

epochs = range(len(acc_model))

fig, axs = plt.subplots(1, 2, figsize=(15,6))
axs[0].plot(epochs, acc_model, label="Training Accuracy")
axs[0].plot(epochs, val_acc_model, label="Validation Accuracy")
axs[0].set_title("Training and Validation Accuracy")
axs[0].legend()

axs[1].plot(epochs, loss_model, label="Training Loss")
axs[1].plot(epochs, val_loss_model, label="Validation Loss")
axs[1].set_title("Training and Validation Loss")
axs[1].legend()

plt.tight_layout()
plt.show()

y_pred = model.predict(test_generator)
y_pred = np.argmax(y_pred, axis=1)
y_true = test_generator.classes

class_name = list(test_generator.class_indices.keys())

report = classification_report(y_true, y_pred, target_names=class_name)
print(report)

cm = confusion_matrix(y_true, y_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=class_name, yticklabels=class_name)
plt.xlabel("Predicted Labels")
plt.ylabel("True Labels")
plt.title("Confusion Matrix")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

"""## Konversi Model

### Saved model to SavedModel format
"""

save_path_model = "saved_model/"
tf.saved_model.save(model, save_path_model)

"""### Converted model to Tensorflow.js"""

!tensorflowjs_converter \
    --input_format tf_saved_model \
    /content/saved_model/ \
    /content/tfjs_model

"""### Converted model to Tensorflow Lite"""

converter = tf.lite.TFLiteConverter.from_saved_model("/content/saved_model/")
tflite_model = converter.convert()

with tf.io.gfile.GFile("model.tflite", "wb") as f:
  f.write(tflite_model)

"""## Inference"""

model_path = "/content/saved_model/"
loaded_model = tf.saved_model.load(model_path)
infer = loaded_model.signatures["serving_default"]

img_path = "/content/dataset/final_dataset/test/skirt/skirt_1233.jpg"

img = tf.keras.preprocessing.image.load_img(
    img_path, target_size=(150, 150),
    color_mode='grayscale'
)

plt.imshow(img, cmap='gray')
plt.title("Input Image (skirt)")
plt.axis('off')
plt.show()

img_array = image.img_to_array(img)
img_array /= 255.0
img_array = np.expand_dims(img_array, axis=0)

img_tensor = tf.convert_to_tensor(img_array, dtype=tf.float32)

y_pred = infer(inputs=img_tensor)

prediction = y_pred["output_0"].numpy()
print("Prediction result: ", prediction)
print("Prediction class: ", np.argmax(prediction))
print("Prediction class name: ", class_name[np.argmax(prediction)])