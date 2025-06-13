from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable
)
import urllib.parse

app = Flask(__name__)

def extract_video_id(url):
    parsed = urllib.parse.urlparse(url)
    if "youtube.com" in parsed.netloc:
        query = urllib.parse.parse_qs(parsed.query)
        return query.get("v", [None])[0]
    elif "youtu.be" in parsed.netloc:
        return parsed.path.strip("/")
    return None

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})

@app.route('/api/transcript', methods=['POST'])
def get_transcript():
    data = request.get_json()
    url = data.get('url')
    video_id = extract_video_id(url)

    if not video_id:
        return jsonify({'error': 'Invalid YouTube URL'}), 400

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = " ".join([entry['text'] for entry in transcript])
        return jsonify({'transcript': full_text})

    except NoTranscriptFound:
        return jsonify({'error': 'No transcript found for this video'}), 404
    except TranscriptsDisabled:
        return jsonify({'error': 'Transcripts are disabled for this video'}), 403
    except VideoUnavailable:
        return jsonify({'error': 'Video is unavailable'}), 404
    except Exception as e:
        print(f"[ERRO INTERNO] {str(e)}")
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run()
