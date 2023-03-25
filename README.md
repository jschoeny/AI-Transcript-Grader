# AI-Transcript-Grader
Uses OpenAI's Whisper and ChatGPT APIs to compare student video submissions against a given rubric.

## Setup
- Install requuired dependencies using `pip install -r requirements.txt`. 
- Add your OpenAI API Key to your environment variables

### Dependencies
- openai: `pip install openai`
- moviepy: `pip install moviepy`

## Grading
- Download student video submissions into a single folder.
- Paste rubric into `rubric.txt` file.
- Run `python main.py path/to/video/files`

## Common errors
- If you get an error message about ffmpeg, you may need install ffmpeg with Hombrew using: `brew install ffmpeg`

