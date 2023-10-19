import os

import moviepy.editor as mp

import openai
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

from sys import argv
from os.path import exists, dirname, splitext

# tkinter for GUI
import tkinter as tk

# CanvasAPI for accessing Canvas
from canvasapi import Canvas
CANVAS_API_URL = os.getenv('CANVAS_API_URL')
CANVAS_API_KEY = os.getenv('CANVAS_API_KEY')
canvas = Canvas(CANVAS_API_URL, CANVAS_API_KEY)

INCLUDED_EXTENSIONS = ['.mov', '.mp4', '.mkv', '.m4v', '.webm']


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        w = 600
        h = 300
        self.geometry("%dx%d+%d+%d" % (w, h, self.winfo_screenwidth() / 2 - (w/2), self.winfo_screenheight() / 2 - (h/2)))
        self.title("AI Grader")
        self.resizable(False, False)

        # Initialize global variables
        self.directory = ""
        self.rubric = ""
        self.file_names = []
        self.system_message = ""
        self.rubric_response = ""

        self.setup_grading()
        self.process_grades()

    def setup_grading(self):
        # Get video files from selected directory
        self.file_names = [fn for fn in os.listdir(dirname(argv[1])) if any(fn.lower().endswith(ext) for ext in INCLUDED_EXTENSIONS)]

        # Use custom rubric file if given
        rubric_fname = "rubric.txt"
        if len(argv) == 3:
            rubric_fname = argv[2]

        # Setup ChatGPT messages for grading
        self.system_message = open("system_message.txt").read()  # Tells the AI how to behave
        self.rubric = "Here is the rubric:\n" + open(rubric_fname).read() + "\n\nDo you understand the requirements?"
        self.rubric_response = "Yes, I understand the requirements."

        # Setup directories for storing outputs
        os.makedirs(self.directory + "/transcripts", exist_ok=True)
        os.makedirs(self.directory + "/grades", exist_ok=True)
        os.makedirs(self.directory + "/audio", exist_ok=True)

    def process_grades(self):
        # Loop through all found video files
        for fname in self.file_names:
            # Create strings for filenames
            file = self.directory + "/" + fname
            audio_fname = self.directory + "/audio/" + splitext(fname)[0] + ".mp3"
            transcript_fname = self.directory + "/transcripts/" + splitext(fname)[0] + ".txt"
            response_fname = self.directory + "/grades/" + splitext(fname)[0] + ".txt"

            # Skip already graded videos
            if exists(response_fname):
                continue

            print("Processing " + fname + "...")

            try:
                # Extract audio and save as mp3
                if exists(audio_fname):
                    print("Using existing audio file: " + audio_fname)
                else:
                    clip = mp.VideoFileClip(file)
                    clip.audio.write_audiofile(audio_fname)

                # Generate transcript using Whisper API
                if exists(transcript_fname):
                    print("Reusing old transcript...")
                    transcript = open(transcript_fname).read()
                else:
                    audio_file = open(audio_fname, "rb")
                    print("Transcribing audio...")
                    transcript = openai.Audio.transcribe("whisper-1", audio_file)["text"]
                    with open(transcript_fname, "w") as f:
                        f.write(transcript)

                # Compare transcript to rubric using ChatGPT API
                print("Checking against rubric...")
                completion = openai.ChatCompletion.create(
                  model="gpt-3.5-turbo",
                  messages=[
                    {"role": "system", "content": self.system_message},
                    {"role": "user", "content": self.rubric},
                    {"role": "assistant", "content": self.rubric_response},
                    {"role": "user", "content": "Here is the student's transcript:\n" + transcript},
                  ]
                )

                # Write response to file
                grade = completion['choices'][0]['message']['content']
                with open(response_fname, "w") as f:
                    f.write(grade)
                print("Response saved.\t", grade.count("Yes"), "Yes.\t", grade.count("No"), "No.\t",
                      grade.count("Partial"), "Partial.")
                print()
            except BaseException as e:
                print("Error encountered processing this student's submission")
                print(e)
        print("Done.")




if __name__ == "__main__":
    app = App()
    app.mainloop()
