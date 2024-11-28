import streamlit as st
from streamlit_option_menu import option_menu
import subprocess
import speech_recognition as sr
from gtts import gTTS
from deep_translator import GoogleTranslator
import PyPDF2   
from io import BytesIO
from reportlab.pdfgen import canvas  
import streamlit as st
from utils.audio_processing import extract_audio
from utils.transcription import transcribe_audio, export_to_srt
from utils.translation import translate_text
import tempfile
import os

def recognize_audio_from_file(audio_file):
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio, language=[k for k, v in language_options.items() if v == source_lang][0])
            st.write(f"Recognized Text in {source_lang}: {text}")
            return text
        except sr.UnknownValueError:
            st.write("Sorry, could not recognize the speech.")
        except sr.RequestError:
            st.write("Error with the recognition service.")
    return None


def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ''
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

 
def create_translated_pdf(translated_text):
    buffer = BytesIO()
    pdf_canvas = canvas.Canvas(buffer)
    
    pdf_canvas.drawString(100, 750, "Translated PDF Content:")
    
    y = 730
    for line in translated_text.split('\n'):
        pdf_canvas.drawString(100, y, line)
        y -= 15
        if y < 100:   
            pdf_canvas.showPage()
            y = 750
    
    pdf_canvas.save()
    buffer.seek(0)
    
    return buffer
 

def recognize_audio_from_microphone(audio_data):
    try:
        text = recognizer.recognize_google(audio_data, language=[k for k, v in language_options.items() if v == source_lang][0])
        st.write(f"Recognized Text in {source_lang}: {text}")
        return text
    except sr.UnknownValueError:
        st.write("Sorry, could not recognize the speech.")
    except sr.RequestError:
        st.write("Error with the recognition service.")
    return None

# 1. as sidebar menu
with st.sidebar:
    selected = option_menu("Multilingual Translation and Content Generation system", ["Real-time voice translation",'Text Translation','PDF translation','Video Scripting'], 
        icons=['mic', 'card-text','file-earmark','play-btn'], menu_icon="cast", default_index=0)
    selected


if selected == "Text Translation":
    st.title("Text Translation")
    language_options = {
        "en": "English",
        "fr": "French",
        "es": "Spanish",
        "de": "German",
        "hi": "Hindi",
        "ja": "Japanese",
        "zh-CN": "Chinese",
    }
    source_lang = st.selectbox("Select Source Language", list(language_options.values()))
    target_lang = st.selectbox("Select Target Language", list(language_options.values()))
    input_text = st.text_area("Enter text to translate:")
    if st.button("Translate"):
        if input_text.strip():
            source_lang_code = [k for k, v in language_options.items() if v == source_lang][0]
            target_lang_code = [k for k, v in language_options.items() if v == target_lang][0]
            translated_text = GoogleTranslator(source=source_lang_code, target=target_lang_code).translate(input_text)
            st.subheader("Translated Text")
            st.write(translated_text)
        else:
            st.warning("Please enter text to translate.")
if selected == "Real-time voice translation":
    language_options = {
    'en': 'English',
    'fr': 'French',
    'es': 'Spanish',
    'de': 'German',
    'hi': 'Hindi',
    'ja': 'Japanese',
    'zh': 'Chinese'
    }
    st.title("Real-Time Voice Translator")
    source_lang = st.selectbox("Select Source Language", list(language_options.values()))
    target_lang = st.selectbox("Select Target Language", list(language_options.values()))
    st.subheader("Step 1: Record or Upload Audio")
    upload_option = st.radio("Choose an option", ('Record Audio', 'Upload Audio'))
    recognizer = sr.Recognizer()
    text = None  

    if upload_option == 'Record Audio':
        if st.button("Start Recording"):
            with sr.Microphone() as source:
                st.write("Recording...")
                try:
                    audio = recognizer.listen(source, timeout=60)
                    st.write("Recording complete!")
                    text = recognize_audio_from_microphone(audio)
                    if text is not None:
                        st.subheader("Step 2: Translate the Text")
                        translation = GoogleTranslator(source=[k for k, v in language_options.items() if v == source_lang][0],target=[k for k, v in language_options.items() if v == target_lang][0]).translate(text)
                        st.write(f"Translated Text ({target_lang}): {translation}")
                        st.subheader("Step 3: Convert Translated Text to Speech")
                        tts = gTTS(text=translation, lang=[k for k, v in language_options.items() if v == target_lang][0])
                        tts.save("translated_audio.mp3")
                        st.audio("translated_audio.mp3", format="audio/mp3")
                except sr.WaitTimeoutError:
                    st.error("Listening timed out. Please try speaking again.")
    else:
        uploaded_file = st.file_uploader("Upload Audio File", type=["wav", "mp3"])
        if uploaded_file is not None:
            text = recognize_audio_from_file(uploaded_file)
            if text is not None:
                st.subheader("Step 2: Translate the Text")
                orignal_text = text
                translation = GoogleTranslator(source=[k for k, v in language_options.items() if v == source_lang][0],target=[k for k, v in language_options.items() if v == target_lang][0]).translate(text)
                st.write(f"Input text ({source_lang}): {orignal_text}")
                st.write(f"Translated Text ({target_lang}): {translation}")
                st.subheader("Step 3: Convert Translated Text to Speech")
                tts = gTTS(text=translation, lang=[k for k, v in language_options.items() if v == target_lang][0])
                tts.save("translated_audio.mp3")
                st.audio("translated_audio.mp3", format="audio/mp3")
            else:
                st.write('Failed to extract text from the audio file. Please try again')

elif selected == "PDF translation":
    language_options = {
        'en': 'English',
        'fr': 'French',
        'es': 'Spanish',
        'de': 'German',
        'hi': 'Hindi',
        'ja': 'Japanese',
        'zh-CN': 'Chinese'
    }

    st.subheader("PDF Translation")
 
    source_lang = st.selectbox("Select Source Language", list(language_options.values()))
    target_lang = st.selectbox("Select Target Language", list(language_options.values()))

    recognizer = sr.Recognizer()

    source_lang_pdf=[k for k, v in language_options.items() if v == source_lang][0]
    target_lang_pd=[k for k, v in language_options.items() if v == target_lang][0]
    uploaded_pdf = st.file_uploader("Upload PDF File", type="pdf")
    
    if uploaded_pdf is not None:
         
        pdf_text = extract_text_from_pdf(uploaded_pdf)
        st.write("Original PDF Text:")
        st.write(pdf_text)

        if pdf_text:
            st.subheader("Step 2: Translate the PDF Text")
            translation = GoogleTranslator(source=[k for k, v in language_options.items() if v == source_lang][0],
                                           target=[k for k, v in language_options.items() if v == target_lang][0]).translate(pdf_text)
            st.write(f"Translated Text ({target_lang}): {translation}")
            translated_pdf = create_translated_pdf(translation)
            st.subheader("Step 3: Download Translated PDF")
            st.download_button(
                label="Download Translated PDF",
                data=translated_pdf,
                file_name="translated_document.pdf",
                mime="application/pdf"
            )

elif selected == "Video Scripting":
    st.title("Multilingual Video Transcription and Translation")
    uploaded_video = st.file_uploader("Upload a Video File", type=["mp4", "mov", "avi"])
    video_path = None
    if uploaded_video is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_video:
            tmp_video.write(uploaded_video.read())
            video_path = tmp_video.name
        audio_path = extract_audio(video_path)
        transcription_result = transcribe_audio(audio_path)
        original_text = transcription_result['text']
        st.write("Original Transcript:", original_text)
        target_language = st.selectbox("Select Target Language", ["en", "es", "fr", "de", "zh", "hi", "ar"])
        translated_text = translate_text(original_text, target_language)
        st.write("Translated Transcript:", translated_text)
    
     
        srt_path = "output.srt"
        export_to_srt(transcription_result, srt_path)
        with open(srt_path, "r") as file:
            srt_content = file.read()
        st.download_button("Download SRT File", srt_content, file_name="translated_transcript.srt")
    
        os.remove(video_path)
        os.remove(audio_path)
        os.remove(srt_path)

# # 2. horizontal menu
# selected2 = option_menu(None, ["Home", "Upload", "Tasks", 'Settings'], 
#     icons=['house', 'cloud-upload', "list-task", 'gear'], 
#     menu_icon="cast", default_index=0, orientation="horizontal")
# selected2

# # 3. CSS style definitions
# selected3 = option_menu(None, ["Home", "Upload",  "Tasks", 'Settings'], 
#     icons=['house', 'cloud-upload', "list-task", 'gear'], 
#     menu_icon="cast", default_index=0, orientation="horizontal",
#     styles={
#         "container": {"padding": "0!important", "background-color": "#fafafa"},
#         "icon": {"color": "orange", "font-size": "25px"}, 
#         "nav-link": {"font-size": "25px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
#         "nav-link-selected": {"background-color": "green"},
#     }
# )

# # 4. Manual item selection
# if st.session_state.get('switch_button', False):
#     st.session_state['menu_option'] = (st.session_state.get('menu_option', 0) + 1) % 4
#     manual_select = st.session_state['menu_option']
# else:
#     manual_select = None
    
# selected4 = option_menu(None, ["Home", "Upload", "Tasks", 'Settings'], 
#     icons=['house', 'cloud-upload', "list-task", 'gear'], 
#     orientation="horizontal", manual_select=manual_select, key='menu_4')
# st.button(f"Move to Next {st.session_state.get('menu_option', 1)}", key='switch_button')
# selected4

# # 5. Add on_change callback
# def on_change(key):
#     selection = st.session_state[key]
#     st.write(f"Selection changed to {selection}")
    
# selected5 = option_menu(None, ["Home", "Upload", "Tasks", 'Settings'],
#                         icons=['house', 'cloud-upload', "list-task", 'gear'],
#                         on_change=on_change, key='menu_5', orientation="horizontal")
# selected5