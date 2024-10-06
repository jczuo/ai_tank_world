import os
import wave
import struct

def create_empty_wav(filename, duration=1.0, sample_rate=44100):
    """创建一个空的WAV文件"""
    num_channels = 1  # 单声道
    sample_width = 2  # 16位

    num_frames = int(duration * sample_rate)
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(num_channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        
        # 写入静音数据
        for _ in range(num_frames):
            wav_file.writeframes(struct.pack('h', 0))

def main():
    # 确保目录存在
    os.makedirs(os.path.join("assets", "sounds"), exist_ok=True)
    
    # 创建所需的音频文件
    audio_files = [
        "shoot.ogg",
        "hit_brick.mp3",
        "hit_tank.mp3",
        "tank_explosion.mp3"
    ]
    
    for file in audio_files:
        path = os.path.join("assets", "sounds", file)
        # 由于我们不能直接创建 .ogg 和 .mp3 文件，我们创建 .wav 文件作为替代
        wav_path = os.path.splitext(path)[0] + ".wav"
        create_empty_wav(wav_path)
        print(f"创建了空的音频文件: {wav_path}")

if __name__ == "__main__":
    main()