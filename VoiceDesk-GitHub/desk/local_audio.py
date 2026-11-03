from threading import Lock
from django.conf import settings
_model=None
_lock=Lock()
def transcribe_audio(audio):
    global _model
    with _lock:
        if _model is None:
            from faster_whisper import WhisperModel
            _model=WhisperModel(str(settings.BASE_DIR/'models'/'whisper-base'),device='cpu',compute_type='int8',local_files_only=True)
        segments,_=_model.transcribe(audio,beam_size=3,vad_filter=True)
        return ' '.join(s.text.strip() for s in segments)
