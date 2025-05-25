# Image Classification Nordstrom & Myntra Clothes Image Data

## 📝 Project Description

This project aims to classify images of clothing items sourced from the Nordstrom and Myntra e-commerce platforms. The model is built using TensorFlow and provided in multiple formats for deployment.

## 📁 Directory Structure

```
├── notebook.ipynb
├── proyek_akhir_fundamental_deeplearning.py
├── requirements.txt
├── saved_model.zip        # TensorFlow SavedModel (compressed)
├── tfjs_model.zip         # Model for TensorFlow.js (compressed)
└── tflite/                # Directory with .tflite files for mobile/edge
```

## ⚙️ Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/muhammadelfikry/Image-Classification-Nordstrom-Myntra-Clothes-Image-Data.git
   cd Image-Classification-Nordstrom-Myntra-Clothes-Image-Data
   ```

2. **Create a virtual environment** (recommended):

   ```bash
   python -m venv venv
   # Windows
   venv\\Scripts\\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

## ▶️ Running the Project

* **Using Jupyter Notebook:**

  ```bash
  jupyter notebook notebook.ipynb
  ```

  Follow the notebook steps for training, evaluation, and experiments.

* **Using Python script:**

  ```bash
  python proyek_akhir_fundamental_deeplearning.py
  ```

## 🧠 Model Formats

* **SavedModel**: Standard TensorFlow format for server deployment.
* **TensorFlow Lite (TFLite)**: For mobile or edge devices. `.tflite` files are in the `tflite/` folder.
* **TensorFlow\.js**: For web applications. Extract `tfjs_model.zip` and integrate it in your frontend.

## 📊 Dataset

The dataset contains images of clothing from Nordstrom and Myntra, labeled for classification tasks.
[kaggle](https://www.kaggle.com/datasets/lygitdata/garmentiq-classification-set-nordstrom-and-myntra)

## 📈 Model Evaluation

The main metric is **accuracy** on the validation data. Detailed evaluation results and plots can be found in `notebook.ipynb`.
