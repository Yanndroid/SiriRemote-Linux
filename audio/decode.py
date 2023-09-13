import wave
import opuslib

sample_rate = 16000
channels = 1
bytes_per_sample = 2

if __name__ == '__main__':

    wave_write = wave.open("siri.wav", "wb")
    wave_write.setnchannels(channels)
    wave_write.setframerate(sample_rate)
    wave_write.setsampwidth(bytes_per_sample)

    opus_decoder = opuslib.Decoder(sample_rate, channels)

    with open("../test/frames.txt") as f:
        for i, line in enumerate(f):
            raw = bytes.fromhex(line)

            print(i, raw.hex())

            header = raw[0]
            audio_data = raw[1:header + 1]
            print(header, audio_data.hex())

            decoded_pcm = opus_decoder.decode(audio_data, 1920)

            wave_write.writeframes(decoded_pcm)
