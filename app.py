from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
import re
import urllib.parse
app = Flask(__name__)

def extract_video_id(url):
    # Tenta extrair de URLs normais ou encurtadas
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
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run()
