from flask import Flask, request, jsonify, render_template, redirect, url_for
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from collections import Counter

app=Flask(__name__)

# Load the dataset
data = pd.read_csv("IMDB Dataset.csv")

# Data preprocessing: Split words, filter stopwords, and remove 'br'
def preprocess_text(text):
    # Replace '<br />' with a space
    text = text.replace('<br />', ' ')

    # Count occurrences of each word
    word_counts = Counter(text.split())

    # Filter out stopwords and other common words that do not contribute much to sentiment
    stopwords = set(STOPWORDS)
    additional_stopwords = set(['movie', 'film'])  # Custom stopwords
    filtered_words = [word for word in word_counts if word.lower() not in stopwords and word.lower() not in additional_stopwords]

    return " ".join(filtered_words)

data['review'] = data['review'].apply(preprocess_text)

# Check class distribution
sentiment_counts = data['sentiment'].value_counts()
print(sentiment_counts)

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(data['review'], data['sentiment'], test_size=0.2, random_state=42)

# Initialize TfidfVectorizer to convert text into numerical features
vectorizer = TfidfVectorizer()

# Fit the vectorizer on the training data and transform both training and testing data
X_train_features = vectorizer.fit_transform(X_train)
X_test_features = vectorizer.transform(X_test)

# Initialize and train a logistic regression model with increased max_iter and regularization
model = LogisticRegression(max_iter=2000, solver='liblinear', penalty='l2')
model.fit(X_train_features, y_train)

# Make predictions on the testing data
y_pred = model.predict(X_test_features)

# Calculate accuracy on the testing data
accuracy = accuracy_score(y_test, y_pred)

# Sentiment Analysis Loop
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST','GET'])
def predict():
    if request.method=='POST':
        user_input=request.form['review']
        cleaned_input = preprocess_text(user_input)
        input_features = vectorizer.transform([cleaned_input])
        global sentiment
        sentiment = model.predict(input_features)[0]
        if sentiment:
            return redirect(url_for('result'))
        
    return render_template('predict.html')
@app.route('/result', methods=['POST','GET'])
def result():
    if sentiment=='positive':
        out="positive"
    else:
        out="negative"
    return render_template('output.html',output=out,out2=accuracy)

@app.route('/thankyou')
def thankyou():
    return render_template("redirect.html")
if __name__ == '__main__':
    app.run(debug=True)