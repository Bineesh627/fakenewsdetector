import numpy as np
import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Embedding
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Data Loading
print("Loading data...")
df_fake = pd.read_csv('dataset/Fake.csv')
df_true = pd.read_csv('dataset/True.csv')

# Data Preparation
print("Preparing data...")
df_true['labels'] = 1
df_fake['labels'] = 0

df = pd.concat([df_true, df_fake], ignore_index=True)
df.drop(columns=['title', 'subject', 'date'], inplace=True)

# Remove duplicates
df = df.drop_duplicates()
print(f"Data shape after cleaning: {df.shape}")

# Split labels
y = df['labels']

# Tokenization
print("Tokenizing text...")
tokenizer = Tokenizer()
tokenizer.fit_on_texts(df['text'])

# Convert texts to sequences
sequences = tokenizer.texts_to_sequences(df['text'])

# Padding
max_seq_len = max(len(seq) for seq in sequences)
X = pad_sequences(sequences, maxlen=max_seq_len)

# Train-test split
print("Splitting data...")
X_train, X_dummy, y_train, y_dummy = train_test_split(X, y, test_size=0.2, random_state=42)
X_valid, X_test, y_valid, y_test = train_test_split(X_dummy, y_dummy, test_size=0.5, random_state=42)

# Model Building
print("Building model...")
word_counts = len(tokenizer.word_index) + 1

model = Sequential([
    Embedding(word_counts, 300, input_length=max_seq_len),
    LSTM(256, return_sequences=True),
    LSTM(128, return_sequences=True),
    LSTM(64, return_sequences=False),
    Dense(1, activation='sigmoid')
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Model Training
print("Training model...")
history = model.fit(
    X_train, y_train,
    validation_data=(X_valid, y_valid),
    epochs=10,
)

# Evaluate on test set
print("\nEvaluating on test set...")
test_loss, test_acc = model.evaluate(X_test, y_test)
print(f"Test Accuracy: {test_acc:.4f}")

# Save the model
print("\nSaving model to fake_news_lstm.h5...")
model.save('model/fake_news_lstm.h5')
print("✓ Model saved successfully!")

# Save the tokenizer
print("Saving tokenizer to tokenizer.pickle...")
with open('model/tokenizer.pickle', 'wb') as handle:
    pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)
print("✓ Tokenizer saved successfully!")

# Save max_seq_len for later use in predictions
print("Saving max_seq_len to max_seq_len.txt...")
with open('model/max_seq_len.txt', 'w') as f:
    f.write(str(max_seq_len))
print("✓ Max sequence length saved successfully!")

# Plot training history
print("\nPlotting training history...")
tr_acc = history.history['accuracy']
tr_loss = history.history['loss']
val_acc = history.history['val_accuracy']
val_loss = history.history['val_loss']
index_loss = np.argmin(val_loss)
val_lowest = val_loss[index_loss]
index_acc = np.argmax(val_acc)
acc_highest = val_acc[index_acc]

Epochs = [i+1 for i in range(len(tr_acc))]
loss_label = f'best epoch= {str(index_loss + 1)}'
acc_label = f'best epoch= {str(index_acc + 1)}'

plt.figure(figsize=(20, 8))
plt.style.use('fivethirtyeight')

plt.subplot(1, 2, 1)
plt.plot(Epochs, tr_loss, 'r', label='Training loss')
plt.plot(Epochs, val_loss, 'g', label='Validation loss')
plt.scatter(index_loss + 1, val_lowest, s=150, c='blue', label=loss_label)
plt.title('Training and Validation Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(Epochs, tr_acc, 'r', label='Training Accuracy')
plt.plot(Epochs, val_acc, 'g', label='Validation Accuracy')
plt.scatter(index_acc + 1, acc_highest, s=150, c='blue', label=acc_label)
plt.title('Training and Validation Accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()

plt.tight_layout()
plt.savefig('training_history.png')
print("✓ Training history plot saved as training_history.png")
plt.show()

print("\n" + "="*60)
print("TRAINING COMPLETE!")
print("="*60)
print("Generated files:")
print("  - fake_news_lstm.h5 (trained model)")
print("  - tokenizer.pickle (tokenizer)")
print("  - max_seq_len.txt (max sequence length)")
print("  - training_history.png (training plots)")
print("="*60)
