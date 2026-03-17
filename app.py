import streamlit as st
import pickle
import pandas as pd
import requests

# --- 1. PAGE CONFIG (Must be the very first Streamlit command) ---
st.set_page_config(page_title="CineMatch Pro", layout="wide", page_icon="🎬")


# --- 2. DATA LOADING & CACHING ---
@st.cache_data
def load_data():
    # Ensure these files are in your GitHub repository
    movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    return movies, similarity


movies, similarity = load_data()


# --- 3. HELPER FUNCTIONS ---
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=98d38df69b8f66e1b16e9f207c51a8a6"
    try:
        data = requests.get(url).json()
        path = data.get('poster_path')
        if path:
            return "https://image.tmdb.org/t/p/w500/" + path
    except:
        pass
    return "https://via.placeholder.com/500x750?text=No+Poster+Available"


def fetch_movie_data(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=98d38df69b8f66e1b16e9f207c51a8a6&append_to_response=videos"
    return requests.get(url).json()


def get_recommendations(movie_title):
    idx = movies[movies['title'] == movie_title].index[0]
    distances = sorted(list(enumerate(similarity[idx])), reverse=True, key=lambda x: x[1])[1:11]

    recommendation_list = []
    for i in distances:
        movie_idx = i[0]
        recommendation_list.append(movies.iloc[movie_idx])
    return recommendation_list


@st.dialog("Movie Details")
def show_details(movie_id):
    data = fetch_movie_data(movie_id)
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(f"https://image.tmdb.org/t/p/w500/{data.get('poster_path')}")
    with col2:
        st.header(data.get('title'))
        st.write(f"📅 {data.get('release_date')}  |  ⭐ {data.get('vote_average', 0):.1f}/10")
        st.write(data.get('overview'))

        videos = data.get('videos', {}).get('results', [])
        trailer = next((v for v in videos if v['type'] == 'Trailer'), None)
        if trailer:
            st.video(f"https://www.youtube.com/watch?v={trailer['key']}")


# --- 4. CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #141414; color: white; }
    div.stButton > button:first-child {
        background-color: #E50914; color: white; border: none; font-weight: bold; width: 100%;
    }
    div.stButton > button:hover { background-color: #ff0a16; color: white; border: none; }
    img { border-radius: 8px; transition: transform .3s; }
    img:hover { transform: scale(1.05); }
    </style>
    """, unsafe_allow_html=True)

# --- 5. SIDEBAR ---
st.sidebar.title("🔍 Filters")
min_rating = st.sidebar.slider("Minimum Rating", 0.0, 10.0, 5.0)

# --- 6. HEADER & SEARCH ---
st.title('CineMatch Pro')
selected_movie_name = st.selectbox(
    "Search for a movie you liked:",
    movies['title'].values,
    key="main_search"
)

if st.button('Get Recommendations'):
    with st.spinner('Finding matches...'):
        recs = get_recommendations(selected_movie_name)
        # Apply rating filter
        filtered_recs = [m for m in recs if m.get('vote_average', 0) >= min_rating]
        st.session_state['recs'] = filtered_recs[:5]

# --- 7. DISPLAY RECOMMENDATIONS ---
if 'recs' in st.session_state:
    st.markdown("### 🎯 Top Picks for You")
    cols = st.columns(5)
    for i, movie in enumerate(st.session_state['recs']):
        with cols[i]:
            st.image(fetch_poster(movie.movie_id))
            with st.container(height=70, border=False):
                st.markdown(f"**{movie.title}**")
            if st.button("Details", key=f"rec_{movie.movie_id}"):
                show_details(movie.movie_id)

st.markdown("---")

# --- 8. TRENDING SECTION ---
st.markdown("### 🔥 Trending This Week")
try:
    trending_url = "https://api.themoviedb.org/3/trending/movie/week?api_key=98d38df69b8f66e1b16e9f207c51a8a6"
    trending_data = requests.get(trending_url).json().get('results', [])

    if trending_data:
        t_tab1, t_tab2 = st.tabs(["Trending 1-5", "Trending 6-10"])

        with t_tab1:
            t_cols = st.columns(5)
            for idx in range(5):
                m = trending_data[idx]
                with t_cols[idx]:
                    st.image(f"https://image.tmdb.org/t/p/w500/{m.get('poster_path')}")
                    st.caption(m.get('title')[:25])
                    if st.button("Details", key=f"trend_{m.get('id')}"):
                        show_details(m.get('id'))

        with t_tab2:
            t_cols2 = st.columns(5)
            for idx in range(5, 10):
                m = trending_data[idx]
                with t_cols2[idx - 5]:
                    st.image(f"https://image.tmdb.org/t/p/w500/{m.get('poster_path')}")
                    st.caption(m.get('title')[:25])
                    if st.button("Details", key=f"trend_{m.get('id')}"):
                        show_details(m.get('id'))
except:
    st.error("Trending section failed to load.")