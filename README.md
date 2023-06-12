## Sitcome-Ai-Base
# Base.py:
This is the core script of your project. It uses OpenAI's GPT-3 model to generate a script and Uberduck to generate voice clips from the script. Afterward, it generates a text file "script.txt" with information about who is talking, what they say, and how long it lasts. It also merges all audio clips into one single file "output.wav".

# Server.py:
This script acts as a bridge between the Base.py script and Unity. It uses the Flask library to expose two endpoints that Unity can call. When Unity makes a GET request, Server.py triggers Base.py to generate a new script and corresponding audio, and then sends the generated audio and script to Unity.

# Main.cs:
This script, written in C#, handles Unity's interactions with Server.py. It includes functions for sending GET requests to Server.py, processing the received script and audio, and moving the camera in the Unity scene according to the script.

# How to Use:
1) Download the project from Git and ensure all files are in the same folder.
2) Import Main.cs into Unity.
3) Run server.py.
4) Set up the environment in Unity and make sure the models are named the same as in base.py, e.g., Spongebob = Spongebob.
5) Attach the script to a Unity object that has an AudioSource Component and point the script to it through the Unity UI.
6) Build and run the project in Unity.

Feel Free to spam me with issues or just fork and build ya own I dont care.