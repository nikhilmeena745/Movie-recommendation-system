import streamlit as st
import pickle
import pandas as pd
import requests

# --- 1. PAGE CONFIG (Must be the very first Streamlit command) ---
st.set_page_config(page_title="CineMatch Pro", layout="wide", page_icon="🎬")


# --- 2. DATA LOADING & CACHING ---
@st.cache_data
def load_data():
    movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    return movies, similarity

try:
    movies, similarity = load_data()
except FileNotFoundError as e:
    st.error(f"❌ Data files not found: {e}. Make sure 'movie_dict.pkl' and 'similarity.pkl' are in the project directory.")
    st.stop()


# --- 3. HELPER FUNCTIONS ---
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=98d38df69b8f66e1b16e9f207c51a8a6"
    try:
        data = requests.get(url, timeout=5).json()
        path = data.get('poster_path')
        if path:
            return "https://image.tmdb.org/t/p/w500/" + path
    except Exception:
        pass
    return "https://via.placeholder.com/500x750?text=No+Poster+Available"


def fetch_movie_data(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=98d38df69b8f66e1b16e9f207c51a8a6&append_to_response=videos"
    try:
        return requests.get(url, timeout=5).json()
    except Exception:
        return {}


def get_recommendations(movie_title, min_rating=0):
    # BUG FIX: Guard against movie not found in dataset
    matches = movies[movies['title'] == movie_title]
    if matches.empty:
        return []

    idx = matches.index[0]
    distances = sorted(
        list(enumerate(similarity[idx])),
        reverse=True,
        key=lambda x: x[1]
    )[1:21]  # Fetch extra to account for rating filter

    recommendation_list = []
    for i in distances:
        movie_row = movies.iloc[i[0]]
        # BUG FIX: Use dict-style access for pandas Series, not attribute access
        if movie_row.get('vote_average', 0) >= min_rating:
            recommendation_list.append(movie_row)

    return recommendation_list[:5]


@st.dialog("Movie Details")
def show_details(movie_id):
    data = fetch_movie_data(movie_id)
    if not data:
        st.error("Could not load movie details.")
        return

    col1, col2 = st.columns([1, 2])
    with col1:
        poster_path = data.get('poster_path')
        if poster_path:
            st.image(f"https://image.tmdb.org/t/p/w500/{poster_path}")
        else:
            st.image("https://via.placeholder.com/500x750?text=No+Poster")
    with col2:
        st.header(data.get('title', 'Unknown Title'))
        release = data.get('release_date', 'N/A')
        rating = data.get('vote_average', 0)
        runtime = data.get('runtime', 'N/A')
        st.write(f"📅 {release}  |  ⭐ {rating:.1f}/10  |  🕐 {runtime} min")

        genres = data.get('genres', [])
        if genres:
            genre_tags = " ".join([f"`{g['name']}`" for g in genres])
            st.markdown(genre_tags)

        st.write(data.get('overview', 'No overview available.'))

        videos = data.get('videos', {}).get('results', [])
        trailer = next((v for v in videos if v.get('type') == 'Trailer' and v.get('site') == 'YouTube'), None)
        if trailer:
            st.video(f"https://www.youtube.com/watch?v={trailer['key']}")
        else:
            st.info("No trailer available.")


# --- 4. CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #141414; color: white; }
    div.stButton > button:first-child {
        background-color: #E50914; color: white; border: none;
        font-weight: bold; width: 100%; border-radius: 4px;
    }
    div.stButton > button:hover { background-color: #ff0a16; color: white; border: none; }
    img { border-radius: 8px; transition: transform .3s; }
    img:hover { transform: scale(1.05); }
    .stSelectbox label { color: #aaa; }
    .stSlider label { color: #aaa; }
    </style>
    """, unsafe_allow_html=True)


# --- 5. HEADER & FILTERS ---
st.title('🎬 CineMatch Pro')
st.markdown("*Your personal AI-powered movie recommendation engine*")
st.markdown("---")

col_search, col_filter = st.columns([3, 1])

with col_search:
    selected_movie_name = st.selectbox(
        "🔍 Search for a movie you liked:",
        movies['title'].values,
        key="main_search"
    )

with col_filter:
    # BUG FIX: min_rating was used in section 6 but never defined — now defined here
    min_rating = st.slider(
        "⭐ Min Rating",
        min_value=0.0,
        max_value=10.0,
        value=0.0,
        step=0.5,
        key="rating_filter"
    )

# --- 6. SEARCH & RECOMMENDATIONS ---
if st.button('🎯 Get Recommendations', use_container_width=False):
    with st.spinner('Finding your perfect matches...'):
        recs = get_recommendations(selected_movie_name, min_rating=min_rating)
        st.session_state['recs'] = recs

        if not recs:
            st.warning(f"No recommendations found with a rating ≥ {min_rating}. Try lowering the minimum rating.")

# --- 7. DISPLAY RECOMMENDATIONS ---
if st.session_state.get('recs'):
    st.markdown("### 🎯 Top Picks for You")
    cols = st.columns(5)
    for i, movie in enumerate(st.session_state['recs']):
        with cols[i]:
            # BUG FIX: Use movie['movie_id'] not movie.movie_id for pandas Series
            movie_id = movie['movie_id']
            st.image(fetch_poster(movie_id))
            with st.container(height=70, border=False):
                st.markdown(f"**{movie['title']}**")
            vote = movie.get('vote_average', 0)
            st.caption(f"⭐ {vote:.1f}/10")
            if st.button("Details", key=f"rec_{movie_id}"):
                show_details(movie_id)

st.markdown("---")

# --- 8. TRENDING SECTION ---
st.markdown("### 🔥 Trending This Week")
try:
    trending_url = "https://api.themoviedb.org/3/trending/movie/week?api_key=98d38df69b8f66e1b16e9f207c51a8a6"
    response = requests.get(trending_url, timeout=5)
    trending_data = response.json().get('results', [])

    if trending_data:
        t_tab1, t_tab2 = st.tabs(["🏆 Trending 1–5", "📈 Trending 6–10"])

        with t_tab1:
            t_cols = st.columns(5)
            for idx in range(min(5, len(trending_data))):
                m = trending_data[idx]
                with t_cols[idx]:
                    poster = m.get('poster_path')
                    if poster:
                        st.image(f"https://image.tmdb.org/t/p/w500/{poster}")
                    title = m.get('title') or m.get('name', 'Unknown')
                    st.caption(title[:25])
                    if st.button("Details", key=f"trend_{m.get('id')}_{idx}"):
                        show_details(m.get('id'))

        with t_tab2:
            t_cols2 = st.columns(5)
            for idx in range(5, min(10, len(trending_data))):
                m = trending_data[idx]
                with t_cols2[idx - 5]:
                    poster = m.get('poster_path')
                    if poster:
                        st.image(f"https://image.tmdb.org/t/p/w500/{poster}")
                    title = m.get('title') or m.get('name', 'Unknown')
                    st.caption(title[:25])
                    if st.button("Details", key=f"trend_{m.get('id')}_{idx}"):
                        show_details(m.get('id'))
    else:
        st.info("No trending data available right now.")

except requests.exceptions.Timeout:
    st.error("⏱️ Trending section timed out. Please refresh.")
except Exception as e:
    st.error(f"⚠️ Trending section failed to load: {e}")