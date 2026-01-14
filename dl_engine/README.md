# Fake News Detection - Model Training & Usage Guide

## 📋 Overview

This guide explains how to train the LSTM model and save all necessary files (model, tokenizer, and max_seq_len) for your fake news detection application.

## ✅ What I Fixed

Your Jupyter notebook was missing code to save:

- ❌ `tokenizer.pickle` - The fitted tokenizer
- ❌ `max_seq_len.txt` - The maximum sequence length

I've created a complete training script that saves all required files.

## 🚀 Quick Start

### Step 1: Train the Model

Run the training script (requires `Fake.csv` and `True.csv` in the same directory):

```bash
python train_and_save_model.py
```

This will generate:

- ✅ `fake_news_lstm.h5` - The trained model
- ✅ `tokenizer.pickle` - The tokenizer
- ✅ `max_seq_len.txt` - Maximum sequence length
- ✅ `training_history.png` - Training plots

**Note:** Training takes time (approximately 10 epochs). On CPU, this could take several hours.

### Step 2: Test Predictions

Once training is complete, test the model:

```bash
python predict_example.py
```

This will:

1. Load the saved model and tokenizer
2. Run example predictions
3. Enter interactive mode for testing your own text

### Step 3: Use in Your Application

Your `main.py` is already configured to load these files correctly!

```python
model = tf.keras.models.load_model('fake_news_lstm.h5')
with open('tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)
with open('max_seq_len.txt', 'r') as f:
    max_seq_len = int(f.read())
```

## 📁 Files Overview

| File                      | Purpose                         |
| ------------------------- | ------------------------------- |
| `train_and_save_model.py` | Complete training script        |
| `predict_example.py`      | Example prediction script       |
| `main.py`                 | Your main application           |
| `fake_news_lstm.h5`       | Trained model (generated)       |
| `tokenizer.pickle`        | Fitted tokenizer (generated)    |
| `max_seq_len.txt`         | Max sequence length (generated) |

## 🔧 Alternative: Update Jupyter Notebook

If you prefer to use your Jupyter notebook, add this code:

**1. Add import to first cell:**

```python
import pickle
```

**2. Add save code after training:**

```python
# Save the model
model.save('fake_news_lstm.h5')

# Save the tokenizer
with open('tokenizer.pickle', 'wb') as handle:
    pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)

# Save max_seq_len
with open('max_seq_len.txt', 'w') as f:
    f.write(str(max_seq_len))
```

## ⚠️ Requirements

Make sure you have all dependencies installed:

```bash
pip install tensorflow numpy pandas scikit-learn matplotlib
```

## 💡 Tips

- The model achieves ~99.92% accuracy as shown in your notebook name
- Training is compute-intensive; consider using GPU if available
- The model file will be ~200MB in size
- Keep `tokenizer.pickle` and `max_seq_len.txt` with the model - they're required for predictions

## 🎯 Next Steps

1. Run `train_and_save_model.py` to generate the files
2. Test with `predict_example.py`
3. Use in your application via `main.py`
