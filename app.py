import streamlit as st
import pickle
import pandas as pd
import requests


# Load data with caching
@st.cache_data
def load_data():
    # Ensure these files are in the same directory as app.py
    movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    return movies, similarity


movies, similarity = load_data()


def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=98d38df69b8f66e1b16e9f207c51a8a6"
    try:
        data = requests.get(url).json()
        poster_path = data.get('poster_path')
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
    except:
        pass
    return "https://via.placeholder.com/500x750?text=No+Poster"


def get_recommendations(movie_title):
    idx = movies[movies['title'] == movie_title].index[0]
    sim_scores = list(enumerate(similarity[idx]))
    # Get top 20 to allow for re-ranking
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:21]

    recommendation_list = []
    for i in sim_scores:
        movie_idx = i[0]
        content_sim = i[1]
        # Normalize rating (assuming vote_average exists)
        rating = movies.iloc[movie_idx].get('vote_average', 0) / 10
        weighted_score = (content_sim * 0.8) + (rating * 0.2)

        recommendation_list.append({
            'title': movies.iloc[movie_idx].title,
            'tmdb_id': movies.iloc[movie_idx].movie_id,
            'score': weighted_score
        })

    return sorted(recommendation_list, key=lambda x: x['score'], reverse=True)[:5]


# --- UI LOGIC ---
st.title('Movie Recommender System')

selected_movie = st.selectbox("Select a movie:", movies['title'].values)

# Use Session State to keep results on screen
if st.button('Get Recommendations'):
    st.session_state['recommendations'] = get_recommendations(selected_movie)

if 'recommendations' in st.session_state:
    cols = st.columns(5)
    for i, movie in enumerate(st.session_state['recommendations']):
        with cols[i]:
            st.image(fetch_poster(movie['tmdb_id']))
            st.caption(movie['title'])
            # Details button now works because recommendations are in session state
            if st.button("Details", key=f"details_{movie['tmdb_id']}"):
                st.write(f"Showing details for ID: {movie['tmdb_id']}")
                # Call your show_details(movie['tmdb_id']) here