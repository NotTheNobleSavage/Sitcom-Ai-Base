## Sitcome-Ai-Base
# Base.py:
The main guts of the program this is in charge of getting the response back from chatgpt and then using Uberduck to create the voice clips, after that is done we create a "script.txt" file that contains who is talking what is said and how long its said for, we also merge all the audio files into 1 "output.wav". Right now, no error checking like this thing crashses if it doesnt all go perfect.

# Server.py:
So turns out Unity doesnt like python, so we need a middleman to act between C and Python, thank god flask exists. We have 2 endpoint 1 to grab the audio and 1 to grab the script pretty simple, we got a GET request ok generate a random prompt send over the audio and script.

# Main.cs:
Now I have no clue whats going on here (thanks stack overflow), we got some functions GetAudioClip (Gets the audio of cause), and GetScript (Gets the script) with the last function ProcessScript dealing with parsing the "script.txt" moving the camera. This is all ran on start using the GetDataFromServer fucntion that gets the audio, script, plays the audio and then starts moving the camera.

# How to Use:
1) Make sure you know you git download and everything is in the same folder
2) you are gonna want to import Main.cs into Unity
3) Run server.py
4) Make sure you got your enviroment setup you are going to want to name your models the same as whats in base.py eg Spongebob = Spongebob
5) Of cause attack the script to somthing make sure its got an AudioSource Component and point the script to it (DO it in the UI)
6) And you know build and run or somthing

Feel Free to spam me with issues or just fork and build ya own I dont care.
test