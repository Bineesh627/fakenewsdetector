import os
import django
import pandas as pd
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
import joblib

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fakenewsdetector.settings')
django.setup()

from detector.models import Prediction

def retrain():
    print("Starting retraining process...")
    
    # Load original data if available
    try:
        df_true = pd.read_csv('True.csv')
        df_fake = pd.read_csv('Fake.csv')
        df_true['labels'] = 1
        df_fake['labels'] = 0
        df = pd.concat([df_true, df_fake], ignore_index=True)
        df['text'] = df['title'] + ' ' + df['text']
        df['text'] = df['text'].apply(lambda t: str(t).lower())
        print(f"Loaded {len(df)} records from CSVs.")
    except Exception as e:
        print(f"Could not load CSVs ({e}). Using empty DataFrame for base.")
        df = pd.DataFrame(columns=['text', 'labels'])

    # Add DB data (approved corrections as new labels)
    new_data = Prediction.objects.filter(approved=True)
    new_records = []
    for p in new_data:
        # If corrected, use corrected label. If not corrected but approved (e.g. validated as correct prediction), use prediction.
        # Logic: If approved and corrected_label exists, use it. If approved and no corrected_label, assume original prediction was verified?
        # Let's assume approved means "good for training".
        if p.corrected_label:
             label = 1 if p.corrected_label == 'Real' else 0
        else:
             label = 1 if p.prediction == 'Real' else 0
        
        new_records.append({'text': p.text.lower(), 'labels': label})
    
    if new_records:
        df_new = pd.DataFrame(new_records)
        df = pd.concat([df, df_new], ignore_index=True)
        print(f"Added {len(df_new)} records from database.")
    
    if df.empty:
        print("No data to train on. Exiting.")
        return

    # Tokenize and pad
    print("Tokenizing...")
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(df['text'])
    sequences = tokenizer.texts_to_sequences(df['text'])
    max_seq_len = max(len(seq) for seq in sequences) if sequences else 300
    
    # Cap max_seq_len to avoid explosion? Let's keep it reasonable or use dynamic.
    # User's script used dynamic.
    
    X = pad_sequences(sequences, maxlen=max_seq_len)
    y = df['labels']

    # Split and fine-tune
    print("Fitting model...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    
    try:
        model = tf.keras.models.load_model('fake_news_lstm.h5')
        print("Loaded existing model.")
    except:
        print("No existing model found. Creating new one.")
        model = tf.keras.models.Sequential([
            tf.keras.layers.Embedding(len(tokenizer.word_index) + 1, 128, input_length=max_seq_len),
            tf.keras.layers.LSTM(64),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])
        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

    model.fit(X_train, y_train, epochs=3, validation_data=(X_test, y_test))
    model.save('fake_news_lstm.h5') # Overwrite or save as new
    print("Model saved to fake_news_lstm.h5")

    # Update tokenizer and max_seq_len
    joblib.dump(tokenizer, 'tokenizer.pickle')
    with open('max_seq_len.txt', 'w') as f:
        f.write(str(max_seq_len))
    print("Tokenizer and max_seq_len updated.")

if __name__ == '__main__':
    retrain()
