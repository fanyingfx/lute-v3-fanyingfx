import azure.cognitiveservices.speech as speechsdk
import pygame

voice_dict = {
    "ja": {"language": "", "voice_name": ""},
    "en": {"language": "en-US", "voice_name": "en-US-JennyNeural"},
}


class AzureTTS:
    def __init__(self, config):
        self._speech_key = config["speech_key"]
        self._speech_region = config["speech_region"]
        self.speech_config = speechsdk.SpeechConfig(
            subscription=self._speech_key, region=self._speech_region
        )
        # self.speech_config.set_speech_synthesis_output_format(
        #     speechsdk.SpeechSynthesisOutputFormat.Audio48Khz96KBitRateMonoMp3
        # )

    def synthesize_and_save(self, text: str, voice: dict, filename) -> bool:
        audio_config = speechsdk.audio.AudioOutputConfig(filename=filename)
        # self.speech_config.speech_recognition_language = voice.get("language")
        # self.speech_config.speech_synthesis_voice_name = voice.get("voice_name")
        speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=self.speech_config, audio_config=audio_config
        )
        res = speech_synthesizer.speak_text_async(text).get()
        print("1")
        # while not(res.reason == speechsdk.ResultReason.SynthesizingAudioCompleted):
        #     return True
        # return False


if __name__ == "__main__":
    config = {
        # 'speech_key': 'b254d8c633)5744fa991275d066caa074',
        "speech_key": "ba319db1e27741cb9430def068ccee32",
        "speech_region": "eastasia",
    }
    tts = AzureTTS(config)
    tts.synthesize_and_save(
        "I'm excited to try text to speech", voice_dict["en"], "test1.wav"
    )
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load("test1.wav")
    pygame.mixer.music.play()
