import os
import logging
logging.basicConfig(handlers=[logging.FileHandler('output.log', 'w',
                                                  'utf-8')],
                    format='%(name)s - %(levelname)s - %(message)s')
logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'texttospeechproject.json'
from google.cloud import texttospeech as tts

from pydub import AudioSegment
from pydub.playback import play

class TextToSpeech():
    def __init__(self):
        self.language_code = 'sr-rs'
        self.client = tts.TextToSpeechClient()

    def text_to_wav(self, text):
        creds = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        if creds:
            logging.info("Time to say the generated text")
            text_input = tts.SynthesisInput(text=text)
            voice_params = tts.VoiceSelectionParams(
                language_code=self.language_code,
            )
            audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.LINEAR16)
    
            response = self.client.synthesize_speech(
                input=text_input, voice=voice_params, audio_config=audio_config
            )
            filename = f"{self.language_code}.wav"
    
            with open(filename, "wb") as out:
                out.write(response.audio_content)
                logging.info("Generated speech saved to {}".format(filename))
    
            song = AudioSegment.from_wav(filename)
            play(song)
            logging.info("Generated text has been spoken")
        else:
            logging.warning("Could not find google credentials environment variable; skipping voice generation")