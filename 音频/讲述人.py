import clr,ctypes
clr.AddReference("System.Speech")
from System.Speech.Synthesis import *

speak = SpeechSynthesizer()
speak.SelectVoice('Microsoft Zira Desktop')
#speak.SetOutputToWaveFile("输出.wav")
speak.Speak("Hello world")
speak.SelectVoice('Microsoft Huihui Desktop')
speak.Speak("中文")
#speak.SetOutputToDefaultAudioDevice()