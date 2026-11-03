from pathlib import Path
from huggingface_hub import snapshot_download
if __name__ == '__main__':
    target = Path(__file__).resolve().parent.parent / 'models' / 'whisper-base'
    snapshot_download('Systran/faster-whisper-base', local_dir=str(target))
    print('Speech model ready:', target)
