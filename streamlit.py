import streamlit as st
import main
# Page Config

# --- UI ---
st.set_page_config(page_title="YouTube Summarizer", page_icon="🎬", layout="wide")
st.title("🎬 YouTube Video Summarizer")
st.caption("Get instant summaries, chapters, and key insights from any YouTube video")

col_main, col_side = st.columns([2, 1])

with col_side:
    with st.container(border=True):
        st.markdown("**How to use:**")
        st.markdown("1. Paste a YouTube URL\n2. Click 'Summarize Video'\n3. Get chapters, insights & takeaways")
        st.markdown("**Best for:**")
        st.markdown("- Long lectures & tutorials\n- Conference talks\n- Podcasts & interviews\n- Educational content")

with col_main:
    url = st.text_input("Enter YouTube URL", placeholder="https://www.youtube.com/watch?v=...")

    if st.button("▶ Summarize Video", type="primary"):
        video_id = main.id_extractor(url)

        if not video_id:
            st.error("Please enter a valid YouTube URL")
        else:
            with st.spinner("Fetching transcript..."):
                try:
                    transcript, word_count = main.get_transcript(video_id)
                    st.success(f"✓ Transcript loaded: {word_count:,} words")
                except Exception as e:
                    st.error(f"Could not fetch transcript: {e}")
                    st.stop()

            with st.spinner("Generating summary..."):
                try:
                    results = main.get_summary(transcript)
                    st.success("✓ Summary complete!")
                except Exception as e:
                    st.error(f"Summary failed: {e}")
                    st.stop()

            st.markdown("---")
            st.header("📊 Summary Results")
            if "summary" in results:
                st.info(results["summary"]["overview"])

            st.subheader("1. CHAPTERS")
            for ch in results.get("chapters", []):
                st.markdown(f'- `{ch["time"]}` **{ch["title"]}** – {ch["description"]}')

            st.subheader("2. KEY INSIGHTS")
            for ins in results.get("keyInsights", []):
                st.markdown(f'- `{ins["time"]}` *"{ins["quote"]}"*')

            st.subheader("3. ACTION ITEMS")
            for i, item in enumerate(results.get("actionItems", []), 1):
                st.markdown(f'{i}. **{item["title"]}**: {item["description"]}')

            st.subheader("4. SUMMARY")
            if "summary" in results:
                st.markdown(f'**Overview**\n\n{results["summary"].get("overview", "N/A")}')
                st.markdown(f'**Strengths and Target Audience**\n\n{results["summary"].get("audience", "N/A")}')

if 'summary' not in st.session_state:
    st.session_state.summary = None
    st.session_state.video_id = None