import streamlit as st
import pickle
import pandas as pd
import requests

# --- 1. SET PAGE CONFIG ---
st.set_page_config(page_title="CineMatch Pro", layout="wide", page_icon="🎬")

# --- 2. CUSTOM CSS (The "Professional" Look) ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #141414;
        color: white;
    }
    /* Button Styling */
    div.stButton > button:first-child {
        background-color: #E50914;
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        font-weight: bold;
    }
    div.stButton > button:hover {
        background-color: #ff0a16;
        border: none;
        color: white;
    }
    /* Image Cards */
    img {
        border-radius: 8px;
        transition: transform .3s;
    }
    img:hover {
        transform: scale(1.05);
        cursor: pointer;
    }
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)


# --- 3. DATA LOADING & FUNCTIONS ---
@st.cache_data
def load_data():
    movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    return movies, similarity


movies, similarity = load_data()


def fetch_movie_data(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=98d38df69b8f66e1b16e9f207c51a8a6&append_to_response=videos"
    return requests.get(url).json()


@st.dialog("Movie Details")
def show_details(movie_id):
    data = fetch_movie_data(movie_id)
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(f"https://image.tmdb.org/t/p/w500/{data.get('poster_path')}")
    with col2:
        st.header(data.get('title'))
        st.write(f"📅 {data.get('release_date')}  |  ⭐ {data.get('vote_average'):.1f}/10")
        st.write(data.get('overview'))

        # Check for trailer
        videos = data.get('videos', {}).get('results', [])
        trailer = next((v for v in videos if v['type'] == 'Trailer'), None)
        if trailer:
            st.video(f"https://www.youtube.com/watch?v={trailer['key']}")


# --- 4. SIDEBAR FILTERS ---
st.sidebar.title("🔍 Search Filters")
min_rating = st.sidebar.slider("Minimum Rating", 0.0, 10.0, 5.0)
year_range = st.sidebar.select_slider("Release Year", options=sorted(movies['release_year'].unique()),
                                      value=(2000, 2024)) if 'release_year' in movies else None

# --- 5. HERO SECTION ---
# Displaying a static "Featured" backdrop (You can make this dynamic later)
st.markdown("### 🔥 Trending Now")
st.image("https://image.tmdb.org/t/p/original/6EL63AnMvYH8fw83Uo3q4pLbC3Z.jpg",
         use_container_width=True)  # Example Backdrop

# --- 6. RECOMMENDATION LOGIC ---
st.markdown("---")
selected_movie = st.selectbox("Search for a movie you liked:", movies['title'].values)

if st.button('Get Recommendations'):
    idx = movies[movies['title'] == selected_movie].index[0]
    distances = sorted(list(enumerate(similarity[idx])), reverse=True, key=lambda x: x[1])[1:11]

    # Filter by rating if available
    rec_movies = []
    for i in distances:
        m_data = movies.iloc[i[0]]
        # Basic check to filter out low-rated movies from the pkl if 'vote_average' is there
        if m_data.get('vote_average', 10) >= min_rating:
            rec_movies.append(m_data)

    st.session_state['recs'] = rec_movies[:5]

# --- 7. DISPLAY GRID ---
if 'recs' in st.session_state:
    cols = st.columns(5)
    for i, movie in enumerate(st.session_state['recs']):
        with cols[i]:
            poster_url = f"https://image.tmdb.org/t/p/w500/{movie.movie_id}"  # Assuming movie_id maps to tmdb_id
            # Fetch real poster path if needed
            st.image(f"https://image.tmdb.org/t/p/w500/{fetch_movie_data(movie.movie_id).get('poster_path')}")
            st.caption(movie.title)
            if st.button("Details", key=f"det_{movie.movie_id}"):
                show_details(movie.movie_id)