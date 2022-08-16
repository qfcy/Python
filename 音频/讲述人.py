import clr,ctypes
clr.AddReference("System.Speech")
from System.Speech.Synthesis import *

speak = SpeechSynthesizer()
speak.SpeakAsync("Hello world")
speak.Speak("中文")