import speech_recognition as sr
try:
    print("Testing Microphone...")
    with sr.Microphone() as source:
        print("Microphone found!")
        print(f"Device name: {source.list_microphone_names()}")
except Exception as e:
    print(f"Error: {e}")
