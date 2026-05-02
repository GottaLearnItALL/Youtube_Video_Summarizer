from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from urllib.parse import urlparse, parse_qs, urlsplit

import os
from dotenv import load_dotenv
import json
import streamlit as st
import re
import yt_dlp
load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY") or st.secrets.get("ANTHROPIC_API_KEY")

def id_extractor(url):
    """ Extract video ID from youtube url """
    
    if 'youtu.be' in url:
        return url.split('/')[-1].split('?')[0]
    
    elif 'youtube.com' in url:
        parsed = urlparse(url)
        video_id = parse_qs(parsed.query).get('v', [None])[0]
        return video_id
    return None

def format_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"[{minutes:02d}:{secs:02d}]"
    

PROXY_HOST = os.getenv("PROXY_HOST") or st.secrets.get("PROXY_HOST")
PROXY_PORT = os.getenv("PROXY_PORT") or st.secrets.get("PROXY_PORT")
PROXY_USER = os.getenv("PROXY_USER") or st.secrets.get("PROXY_USER")
PROXY_PASS = os.getenv("PROXY_PASS") or st.secrets.get("PROXY_PASS")

import yt_dlp

def get_transcript(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        ydl_opts = {
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en'],
            'skip_download': True,
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            subtitles = info.get('subtitles') or info.get('automatic_captions', {})
            en_subs = subtitles.get('en', [])
            if not en_subs:
                raise Exception("No English captions found")
            
            # Get the transcript text
            transcript_url = en_subs[0]['url']
            import requests
            response = requests.get(transcript_url)
            text = response.text
            
            # Clean up XML tags
            import re
            clean = re.sub(r'<[^>]+>', '', text)
            clean = re.sub(r'\s+', ' ', clean).strip()
            
            return clean, len(clean.split())
    except Exception as e:
        raise Exception(f"Transcript error: {e}")

def get_summary(transcript_with_times):
    """ Creates and Returns a neat formatted summary of the transcript.
    
        params:
            transcripts: str
        
        Return:
            response: Text
    """
    system = """You are a YouTube video summarizer. Return ONLY valid JSON, no markdown, no explanation:
    {
        "chapters": [{"time": "MM:SS", "title": "string", "description": "string"}],
        "keyInsights": [{"time": "MM:SS", "quote": "string"}],
        "actionItems": [{"title": "string", "description": "string"}],
        "summary": {"overview": "string", "audience": "string"}
    }
    Provide 4-5 chapters, 5 key insights as quotes with timestamps, 5-6 action items, and a 2-3 sentence overview."""

    messages = [
        SystemMessage(content=system),
        HumanMessage(content=f"Summarize this transcripts:\n\n{transcript_with_times}")
]
    #Initializer Claude
    llm = ChatAnthropic(
        model="claude-haiku-4-5",
        api_key=ANTHROPIC_API_KEY)

    # Get a Response
    
    response = llm.invoke(messages)
    text = response.content.strip()
    
    # Extract JSON more robustly
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if not match:
        raise ValueError("No JSON found in response")

    parsed = json.loads(match.group())
    print("Keys returned:", parsed.keys()) 
    
    return json.loads(match.group())


def main():
    print("Youtube Video Summarizer")
    print("========================\n")

    input_url = input("Enter a url to summarize: ")

    # Extract id
    video_id = id_extractor(input_url)

    if not video_id:
        print("X Error: Invalid Youtube URL")
        return 
    
    print("\nFetching video information...")

    transcript_text, word_count = get_transcript(video_id)

    if not transcript_text:
        return
    
    print(f"Video ID: {video_id}")
    print(f"Word Count: {video_id}")

    print("\nGenerating summary...")
    
    summary = get_summary(transcript_text)
    
    # Display summary
    print("\n" + "="*60)
    print("📺 VIDEO SUMMARY")
    print("="*60 + "\n")
    print(summary)
    print("\n" + "="*60)
    print("✓ Summary complete!")

if __name__ == "__main__":
    main()


    
