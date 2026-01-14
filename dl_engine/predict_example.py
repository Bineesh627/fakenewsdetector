"""
Example script showing how to load the saved model and tokenizer
and make predictions on new text
"""

import pickle
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Load the saved model
print("Loading model...")
model = load_model('model/fake_news_lstm.h5')
print("✓ Model loaded successfully")

# Load the saved tokenizer
print("Loading tokenizer...")
with open('model/tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)
print("✓ Tokenizer loaded successfully")

# Get max sequence length (you need to save this or calculate it)
# For now, we'll use a default value - you should save this in your training script
# You can find it from the model's input shape
max_seq_len = model.input_shape[1]
print(f"Max sequence length: {max_seq_len}")

def predict_news(text):
    """
    Predict whether a news article is fake or real
    
    Args:
        text (str): The news article text
        
    Returns:
        tuple: (prediction, confidence)
            - prediction: "REAL" or "FAKE"
            - confidence: probability score
    """
    # Convert text to sequence
    sequence = tokenizer.texts_to_sequences([text])
    
    # Pad sequence
    padded = pad_sequences(sequence, maxlen=max_seq_len)
    
    # Make prediction
    pred = model.predict(padded, verbose=0)[0][0]
    
    # Interpret result
    if pred >= 0.5:
        return "REAL", float(pred)
    else:
        return "FAKE", float(1 - pred)

# Example usage
if __name__ == "__main__":
    # Example 1: Real news (Reuters style)
    real_news = """
    WASHINGTON (Reuters) - The head of a conservative Republican faction in the U.S. 
    Congress, who voted this month for a huge expansion of the national debt to pay for 
    tax cuts, called himself a "fiscal conservative" on Sunday.
    """
    
    # Example 2: Fake news (sensational style)
    fake_news = """
    Donald Trump just couldn't wish all Americans a Happy New Year and leave it at that. 
    Instead, he had to give a shout out to his enemies, haters and the fake news media.
    """
    
    print("\n" + "="*70)
    print("PREDICTION EXAMPLES")
    print("="*70)
    
    # Predict real news
    prediction, confidence = predict_news(real_news)
    print(f"\nExample 1 (Real News):")
    print(f"Prediction: {prediction}")
    print(f"Confidence: {confidence:.2%}")
    
    # Predict fake news
    prediction, confidence = predict_news(fake_news)
    print(f"\nExample 2 (Fake News):")
    print(f"Prediction: {prediction}")
    print(f"Confidence: {confidence:.2%}")
    
    print("\n" + "="*70)
    
    # Interactive mode
    print("\nYou can now test your own news articles!")
    print("Enter 'quit' to exit.\n")
    
    while True:
        user_input = input("Enter news text (or 'quit'): ").strip()
        
        if user_input.lower() == 'quit':
            print("Goodbye!")
            break
            
        if not user_input:
            print("Please enter some text.")
            continue
            
        prediction, confidence = predict_news(user_input)
        print(f"→ Prediction: {prediction} (Confidence: {confidence:.2%})\n")
