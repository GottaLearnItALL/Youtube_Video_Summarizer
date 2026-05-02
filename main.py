from youtube_transcript_api import YouTubeTranscriptApi
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from urllib.parse import urlparse, parse_qs, urlsplit
import os
from dotenv import load_dotenv
import json

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

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
    

def get_transcript(parsed_url):
    """ Fetches the video transcript from the provided id """
    try:
        ytt_api = YouTubeTranscriptApi()
        transcripts = ytt_api.fetch(video_id=parsed_url, languages=['en'])
        

        full_text = " ".join(f"{format_timestamp(entry.start)} {entry.text}" for entry in transcripts.snippets)

        return full_text, len(full_text.split())
    except Exception as e:
        print(f"Error could not fetch transcript - {e}")
        print("  Note: This video may not have English captions available.")
        return None, 0



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
    
    text = response.content.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    return json.loads(text)


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


    
