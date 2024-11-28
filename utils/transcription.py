import whisper
model = whisper.load_model("base")

import whisper
from googletrans import Translator

model = whisper.load_model("base")
translator = Translator()

def transcribe_audio(audio_path, target_language="en"):
    transcription_result = model.transcribe(audio_path, fp16=False) 
    translated_segments = []
    for segment in transcription_result['segments']:
        translated_text = translator.translate(segment['text'], dest=target_language).text
        translated_segments.append({
            "start": segment['start'],
            "end": segment['end'],
            "text": translated_text
        })
    translation_result = {
        "text": ' '.join([segment['text'] for segment in translated_segments]),   
        "segments": translated_segments   
    }
    return translation_result
def export_to_srt(transcription_result, output_path="output.srt"):
    with open(output_path, "w", encoding="utf-8") as srt_file:
        for i, segment in enumerate(transcription_result['segments']):
            start = format_timestamp(segment['start'])
            end = format_timestamp(segment['end'])
            srt_file.write(f"{i + 1}\n{start} --> {end}\n{segment['text']}\n\n")

def format_timestamp(seconds):
      
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"
