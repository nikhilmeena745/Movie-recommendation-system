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


@st.dialog("Movie Overview")
def show_movie_details(movie_id):
    # Fetch Basic Info
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=98d38df69b8f66e1b16e9f207c51a8a6"
    response = requests.get(url).json()

    # Fetch Video/Trailer Info
    video_url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key=98d38df69b8f66e1b16e9f207c51a8a6"
    video_response = requests.get(video_url).json()

    # Find the official YouTube trailer from the results
    trailer_key = None
    if 'results' in video_response:
        for video in video_response['results']:
            if video['type'] == 'Trailer' and video['site'] == 'YouTube':
                trailer_key = video['key']
                break

    # --- UI Layout inside Dialog ---
    col1, col2 = st.columns([1, 2])

    with col1:
        st.image(f"https://image.tmdb.org/t/p/w500/{response.get('poster_path')}")
        st.write(f"⭐ **{response.get('vote_average', 0):.1f}/10**")

    with col2:
        st.subheader(response.get('title'))
        st.caption(f"Released: {response.get('release_date')}")
        st.write(response.get('overview'))
    st.link_button("View on TMDB", f"https://www.themoviedb.org/movie/{movie_id}")

    # --- Add the Trailer below the description ---
    if trailer_key:
        st.write("---")
        st.write("### 🎬 Watch Trailer")
        st.video(f"https://www.youtube.com/watch?v={trailer_key}")
    else:
        st.info("Trailer not available for this movie.")



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

# Check if recommendations exist in session state
if 'recommendations' in st.session_state:
    cols = st.columns(5)
    for i, movie in enumerate(st.session_state['recommendations']):
        with cols[i]:
            st.image(fetch_poster(movie['tmdb_id']))
            st.caption(movie['title'])

            # Use the unique tmdb_id for the button key
            if st.button("Details", key=f"details_{movie['tmdb_id']}"):
                show_movie_details(movie['tmdb_id'])