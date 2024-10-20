
import streamlit as st
from yt_dlp import YoutubeDL
from pydub import AudioSegment
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

def fetch_and_convert_videos(query, count):
    options = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    downloaded_files = []
    with YoutubeDL(options) as ydl:
        search_info = ydl.extract_info(f"ytsearch{count}:{query}", download=False)

        for entry in search_info['entries']:
            st.write(f"Downloading: {entry['title']}")
            ydl.download([entry['webpage_url']])
            mp3_filename = f"{entry['title']}.mp3"
            downloaded_files.append(mp3_filename)
            if not os.path.exists(mp3_filename):
                st.error(f"Error: {mp3_filename} was not created.")
            else:
                st.success(f"Downloaded and converted {mp3_filename}")

    return downloaded_files

def assemble_mashup(directory=".", output_name="mashup.mp3", segment_duration=30 * 1000):
    audio_files = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith(".mp3")]

    if not audio_files:
        st.warning("No .mp3 audio files found in the directory.")
        return

    mashup_segment = AudioSegment.silent(duration=0)

    for audio_file in audio_files:
        try:
            track = AudioSegment.from_file(audio_file)
            snippet = track[:segment_duration]
            mashup_segment += snippet
            st.write(f"Added {segment_duration / 1000} seconds of {audio_file} to the mashup")
        except Exception as err:
            st.error(f"Failed to process {audio_file}: {err}")

    if len(mashup_segment) > 0:
        mashup_segment.export(output_name, format="mp3")
        st.success(f"Mashup created: {output_name}")
    else:
        st.warning("No valid audio clips to create a mashup.")

def send_email(recipient_email, filename):
    sender_email = "spajjoint@gmail.com" 
    sender_password = "cprpxwcoicelmyad"  

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = "Your Audio Mashup"

    with open(filename, 'rb') as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(filename)}')
        msg.attach(part)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
            st.success(f"Email sent to {recipient_email} with the mashup attached.")
    except Exception as err:
        st.error(f"Failed to send email: {err}")


def run_app():
    st.title("YouTube Video Audio Mashup Creator")

    video_topic = st.text_input("Enter the name or topic of the videos you want to download:")
    video_count = st.number_input("Enter the number of videos to download:", min_value=1, value=5)
    segment_length = st.number_input("Enter the number of seconds to cut from the start of each audio:", min_value=1, value=30)
    recipient_email = st.text_input("Enter the recipient's email address:")

    if st.button("Create Mashup"):
        if video_topic and recipient_email:
            audio_files = fetch_and_convert_videos(video_topic, video_count)
            if audio_files:
                assemble_mashup(output_name="mashup.mp3", segment_duration=segment_length * 1000)
                send_email(recipient_email, "mashup.mp3")
        else:
            st.error("Please fill in all fields.")


if __name__ == "__main__":
    run_app()
