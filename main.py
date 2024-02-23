import os
import threading

import moviepy.editor as mp
import openai
from sys import argv
from os.path import exists, dirname, splitext

if len(argv) < 2 or argv[1] == "":
    print("Usage: py " + argv[0] + " file [rubric]")
    exit(1)

# Get video files from selected directory
directory = argv[1]
if os.path.isfile(directory):
    directory = dirname(directory)
included_extensions = ['.mov', '.mp4', '.mkv', '.m4v', '.webm']
file_names = [fn for fn in os.listdir(dirname(argv[1])) if any(fn.lower().endswith(ext) for ext in included_extensions)]

# Use custom rubric file if given
rubric_fname = "rubric.txt"
if len(argv) == 3:
    rubric_fname = argv[2]

# Setup ChatGPT messages for grading
openai.api_key = os.getenv('OPENAI_API_KEY')  # Your OpenAI API Key
system_message = open("system_message.txt").read()  # Tells the AI how to behave
rubric = "Here is the rubric:\n" + open(rubric_fname).read() + "\n\nDo you understand the requirements?"
rubric_response = "Yes, I understand the requirements."

# Setup directories for storing outputs
os.makedirs(directory + "/transcripts", exist_ok=True)
os.makedirs(directory + "/grades", exist_ok=True)
os.makedirs(directory + "/audio", exist_ok=True)


def process_video(fname):
    # Create strings for filenames
    file = directory + "/" + fname
    student_name = fname.split("_")[0]
    audio_fname = directory + "/audio/" + splitext(fname)[0] + ".mp3"
    transcript_fname = directory + "/transcripts/" + splitext(fname)[0] + ".txt"
    response_fname = directory + "/grades/" + splitext(fname)[0] + ".txt"

    # Skip already graded videos
    if exists(response_fname):
        return

    print("Processing " + fname + "...")

    try:
        # Extract audio and save as mp3
        if exists(audio_fname):
            print(f"[{student_name}] Using existing audio file: " + audio_fname)
        else:
            print(f"[{student_name}] Extracting audio...")
            clip = mp.VideoFileClip(file)
            clip.audio.write_audiofile(audio_fname, ffmpeg_params=['-ac', '1'], logger=None)

        # Generate transcript using Whisper API
        if exists(transcript_fname):
            print(f"[{student_name}] Reusing old transcript...")
            transcript = open(transcript_fname).read()
        else:
            audio_file = open(audio_fname, "rb")
            print(f"[{student_name}] Transcribing audio...")
            transcript = openai.Audio.transcribe("whisper-1", audio_file)["text"]
            with open(transcript_fname, "w") as f:
                f.write(transcript)

        # Compare transcript to rubric using ChatGPT API
        print(f"[{student_name}] Checking against rubric...")
        completion = openai.ChatCompletion.create(
          model="gpt-4-turbo-preview",
          messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": rubric},
            {"role": "assistant", "content": rubric_response},
            {"role": "user", "content": "Here is the student's transcript:\n" + transcript},
          ]
        )

        # Write response to file
        grade = completion['choices'][0]['message']['content']
        with open(response_fname, "w") as f:
            f.write(grade)
        print(f"[{student_name}] Response saved.\t", grade.count("Yes"), "Yes.\t", grade.count("No"), "No.\t",
              grade.count("Partial"), "Partial.")
        print()
    except BaseException as e:
        print(f"Error encountered processing {student_name}'s submission")
        print(e)


# Start threads for all found videos
threads = []
for f in file_names:
    t = threading.Thread(target=process_video, args=(f,))
    threads.append(t)

for t in threads:
    t.start()

for t in threads:
    t.join()

print("Done.")
