# Movie-recommendation-system
# 🎬 Movie Recommendation System

A machine learning-based web application that recommends movies based on user preferences. This project uses a content-based filtering approach to analyze movie metadata and suggest similar films to the user.

## 📺 Project Demo

Click the image below to watch a full video demonstration of the project in action:

[![Watch the Demo](https://img.youtube.com/vi/kwGb5y-7UQQ/maxresdefault.jpg)](https://www.youtube.com/watch?v=kwGb5y-7UQQ)


## ✨ Features
* **Personalized Recommendations:** Suggests the top 5 most similar movies based on the user's selection.
* **Interactive Web Interface:** A clean, user-friendly frontend to browse and search for movies.
* **Fast Similarity Search:** Utilizes pre-computed pickle (`.pkl`) files for lightning-fast real-time recommendations.

## 📁 Repository Structure
* `Movie recommender system.ipynb`: The core Jupyter Notebook containing the data exploration, preprocessing, and machine learning model training (Similarity Matrix generation).
* `app.py` / `main.py`: The main application scripts used to run the web interface. 
* `movies.pkl` & `movie_dict.pkl`: Serialized Python objects containing the processed movie dataset and similarity scores, imported directly into the web app to save computation time.
* `requirements.txt`: A list of all Python dependencies required to run this project.
* `Procfile`: Configuration file for deploying the application to cloud platforms (like Heroku).
* *Bonus:* `Customer churn prediction using ANN.ipynb`: An additional notebook containing an Artificial Neural Network model for churn prediction.

## 🚀 How to Run Locally

If you want to run this project on your own machine, follow these steps:

**1. Clone the repository**
```bash
git clone [https://github.com/nikhilmeena745/Movie-recommendation-system.git](https://github.com/nikhilmeena745/Movie-recommendation-system.git)
cd Movie-recommendation-system
