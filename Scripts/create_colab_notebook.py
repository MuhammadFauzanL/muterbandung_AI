import nbformat
import os

def create_colab_notebook():
    notebook_path = 'MuterBandung_Colab_Package/Train_IndoBERT_MuterBandung.ipynb'
    os.makedirs('MuterBandung_Colab_Package', exist_ok=True)
    
    nb = nbformat.v4.new_notebook()
    
    cells = [
        nbformat.v4.new_markdown_cell("# 🚀 MuterBandung: IndoBERT Fine-Tuning untuk Analisis Sentimen Ulasan Wisata\n\nNotebook ini dirancang KHUSUS untuk dieksekusi di **Google Colab** dengan menggunakan akselerator GPU. Model ini akan melatih arsitektur **Deep Learning (Transformers)** dari dasar (indobenchmark/indobert-base-p1) menggunakan 34.000 ulasan dari proyek MuterBandung.\n\n### Persiapan Awal:\n1. Pastikan Anda mengaktifkan GPU: Buka menu `Runtime` > `Change runtime type` > Pilih `T4 GPU` atau GPU lainnya.\n2. Upload file `MASTER_REVIEWS_ENRICHED.csv` Anda ke menu Files (ikon folder di sebelah kiri)."),
        
        nbformat.v4.new_code_cell("!pip install transformers[torch] accelerate scikit-learn pandas numpy\n!nvidia-smi"),
        
        nbformat.v4.new_markdown_cell("## 1. Load & Siapkan Dataset"),
        
        nbformat.v4.new_code_cell("""import pandas as pd
import numpy as np
import re
from sklearn.model_selection import train_test_split

print("Memuat dataset ulasan wisata...")
# Pastikan file MASTER_REVIEWS_ENRICHED.csv sudah di-upload ke Colab
df = pd.read_csv('MASTER_REVIEWS_ENRICHED.csv', low_memory=False)

def clean_text(text):
    if pd.isna(text): return ""
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9\\s]', ' ', text)
    return re.sub(r'\\s+', ' ', text).strip()

def label_sentimen(rating):
    if rating >= 4: return 2 # Positif
    elif rating == 3: return 1 # Netral
    else: return 0 # Negatif

df['review_nlp'] = df['review_text'].apply(clean_text)
df = df[df['review_nlp'] != '']
df['label'] = df['rating'].apply(label_sentimen)

print(f"Total data bersih: {len(df)} baris.")
print("Distribusi Kelas:")
print(df['label'].value_counts())

# Split Data (80% Train, 20% Test)
train_texts, val_texts, train_labels, val_labels = train_test_split(
    df['review_nlp'].tolist(), 
    df['label'].tolist(), 
    test_size=0.2, 
    random_state=42, 
    stratify=df['label'].tolist()
)
print(f"Train size: {len(train_texts)}, Validation size: {len(val_texts)}")"""),
        
        nbformat.v4.new_markdown_cell("## 2. Inisialisasi IndoBERT & Tokenisasi"),
        
        nbformat.v4.new_code_cell("""import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

model_name = "indobenchmark/indobert-base-p1"
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Karena dataset kita asimetris (sangat banyak positif), IndoBERT akan tetap belajar dengan baik asalkan max_length diatur pas
train_encodings = tokenizer(train_texts, truncation=True, padding=True, max_length=128)
val_encodings = tokenizer(val_texts, truncation=True, padding=True, max_length=128)

class MuterBandungDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

train_dataset = MuterBandungDataset(train_encodings, train_labels)
val_dataset = MuterBandungDataset(val_encodings, val_labels)

# Inisialisasi Model dengan 3 label klasifikasi
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=3)
device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
model.to(device)
print(f"Model berhasil di-load di device: {device}")"""),
        
        nbformat.v4.new_markdown_cell("## 3. Konfigurasi Pelatihan (Fine-Tuning)"),
        
        nbformat.v4.new_code_cell("""from transformers import Trainer, TrainingArguments
from sklearn.metrics import accuracy_score, f1_score

def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    acc = accuracy_score(labels, preds)
    f1 = f1_score(labels, preds, average='weighted')
    return {'accuracy': acc, 'f1': f1}

training_args = TrainingArguments(
    output_dir='./results',          
    num_train_epochs=3,              # 3 Epochs sudah cukup kuat untuk dataset 34k
    per_device_train_batch_size=16,  
    per_device_eval_batch_size=64,   
    warmup_steps=500,                
    weight_decay=0.01,               
    logging_dir='./logs',            
    logging_steps=100,
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True
)

trainer = Trainer(
    model=model,                         
    args=training_args,                  
    train_dataset=train_dataset,         
    eval_dataset=val_dataset,            
    compute_metrics=compute_metrics,
)

print("Memulai Pelatihan Model (Tunggu sekitar 15-30 Menit)...")
trainer.train()"""),
        
        nbformat.v4.new_markdown_cell("## 4. Evaluasi & Simpan Model Akhir"),
        
        nbformat.v4.new_code_cell("""print("Mengevaluasi model terbaik...")
eval_result = trainer.evaluate()
print(f"Akurasi Akhir: {eval_result['eval_accuracy'] * 100:.2f}%")
print(f"F1-Score Akhir: {eval_result['eval_f1'] * 100:.2f}%")

model_save_path = "MuterBandung-IndoBERT-Sentiment"
trainer.save_model(model_save_path)
tokenizer.save_pretrained(model_save_path)

print(f"✅ Model berhasil disimpan di folder: {model_save_path}")
print("Silakan klik kanan folder tersebut di sidebar Colab, lalu pilih 'Download' untuk menyimpannya ke komputer Anda (Bisa juga zip terlebih dahulu).")

# Opsional: Zip folder untuk mempermudah download
!zip -r MuterBandung-IndoBERT-Sentiment.zip MuterBandung-IndoBERT-Sentiment""")
    ]
    
    nb.cells.extend(cells)
    
    with open(notebook_path, 'w', encoding='utf-8') as f:
        nbformat.write(nb, f)
    print(f"File Colab Notebook berhasil dibuat di: {notebook_path}")

if __name__ == "__main__":
    create_colab_notebook()
