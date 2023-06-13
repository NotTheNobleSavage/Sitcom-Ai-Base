#Importing the libraries
import secret
import openai
import requests
from time import sleep
import os
import wave
import random
import soundfile as sf
from concurrent.futures import ThreadPoolExecutor
import concurrent
from concurrent.futures import wait


#Setting up the API keys
uberduck_auth = secret.uberduck_auth
openai.api_key = secret.token

#Setting up the Voice Models
Voice_Models = {
    "Spongebob": "2231cbd3-15a5-4571-9299-b58f36062c45",
    "Patrick": "3b2755d1-11e2-4112-b75b-01c47560fb9c",
    "Homer": "f8c7d125-a240-47e3-94be-18bb58179a2a",
    "Bart": "c924eb5e-d5b1-4916-96ea-ac6948cdbe86"
}

#Setting up the base promt
base_promt = """
    You are to create scripts. 
    You will be giving the topic and who to act like. 
    Make sure you are in character.
    You are the act like the person you are given. 
    You dont need actions just what they say.
    Dont do any actions.
    Make sure the script is over 10 lines long, but under 15.
    Format is: person: "what they say" 
    Keep everything dumb and stupid.
"""

#Setting up the topics
prompts = [
    "Spongebob, Patrick, Spongebob says undertale is gay",
    "Spongebob, Patrick, Talking about having a massive orgy",
    "Spongebob, Patrick, Talking about the heat deth of the universe",
    "Spongebob, Patrick, Secret Krabby patty ingredient is Monosodium glutamate also known as E621",
    "Spongebob, Patrick, Spongebob is a furry",
    "Spongebob, Patrick, Spongebob is a brony",
    "Spongebob, Patrick, Spongebob is a weeb",
    "Spongebob, Patrick, Spongebob hates black lives matters and Patrick says the world will end in October 2nd 2025",
]

#Creates the script using the OpenAI API
def chat_gen(script, content):
    reply = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
            {"role": "system", "content": script},
            {"role": "user", "content": content},
        ]
    )

    #Cleanup of the responce 
    responce = reply['choices'][0]['message']['content'] # type: ignore
    responce = responce.replace("\n\n","\n")
    responce = responce.split("\n")
    return responce

#Creates the voice using the Uberduck API
def gen_voice(text, voice, pos):
    audio_uuid = requests.post(
        "https://api.uberduck.ai/speak",
        json=dict(speech=text, voicemodel_uuid=voice),
        auth=uberduck_auth,
    ).json()["uuid"]

    for t in range(50):
        sleep(1)
        output = requests.get(
            "https://api.uberduck.ai/speak-status",
            params=dict(uuid=audio_uuid),
            auth=uberduck_auth,
        ).json()
        if output['path'] != None:
            r = requests.get(output["path"], allow_redirects=True)
            file_path = f"speech{pos}.wav"
            with open(file_path, "wb") as f:
                f.write(r.content)
            return pos, file_path

#Creates the script file
def create_script(text, speeker, pos):
    with open("script.txt", 'a') as f:
        d = sf.SoundFile(f"speech{pos}.wav")
        f.write(f'{speeker}:{text}:{(d.frames / d.samplerate)}\n')

#Merges the audio files  
def merge_wav_files(file_list, output_filename):
    # Open first valid file and get details
    params = None
    for filename in file_list:
        try:
            with wave.open(filename, 'rb') as wave_file:
                params = wave_file.getparams()
                break
        except wave.Error:
            continue

    if params is None:
        print("No valid input files.")
        return

    # Open output file with same details
    with wave.open(output_filename, 'wb') as output_wav:
        output_wav.setparams(params)

        # Go through input files and add each to output file
        for filename in file_list:
            try:
                with wave.open(filename, 'rb') as wave_file:
                    output_wav.writeframes(wave_file.readframes(wave_file.getnframes()))
            except wave.Error:
                print(f"Skipping invalid file: {filename}")

#Cleans up file that will be made later
def cleanup():
    for filename in os.listdir(os.getcwd()):
        if filename.startswith(("speech", "output", "script")):
            os.remove(filename)

#Main function
def run():
    #Cleans up the files
    cleanup()

    #Chooses a random topic and creates the script
    rand_prompt = random.choice(prompts)
    script = chat_gen(base_promt,rand_prompt)

    futures = []
    with ThreadPoolExecutor() as executor:
        for line in script:
            if line.split(":")[0] in Voice_Models.keys():
                voice_id = Voice_Models[line.split(":")[0]].strip()
                text = line.split(":")[1].strip()
                speaker = line.split(":")[0].strip()
                pos = script.index(line)

                futures.append(executor.submit(gen_voice, text, voice_id, pos))

    wait(futures)

    for future in futures:
        pos, file_path = future.result()
        create_script(script[pos].split(":")[1].strip(), script[pos].split(":")[0].strip(), pos)

    #Check if all the speech.wav files are there
    for i in range(len(script)):
        if not os.path.isfile(f"speech{i}.wav"):
            print("Something went wrong, please try again")
            return

    #Merges the audio files into one
    merge_wav_files([f"speech{i}.wav" for i in range(len(script))], "output.wav")

    #Cleans up the audio files
    for filename in os.listdir(os.getcwd()):
        if filename.startswith("speech"):
            os.remove(filename)