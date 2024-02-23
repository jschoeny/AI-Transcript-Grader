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
- Paste rubric into `rubric.txt` file (or include your rubric txt file as an argument).
- Run `python main.py path/to/video/files [path/to/rubric]`

## Common errors
- If you get an error message about ffmpeg, you may need install ffmpeg with Homebrew using: `brew install ffmpeg`

