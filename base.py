# Standard imports
import logging
import os
import random
import time
from concurrent.futures import ThreadPoolExecutor, wait
from time import sleep
import requests

# Third-party imports
import openai
import soundfile as sf
import wave

# Other Imports
import secret

#Settup up logging
logging.basicConfig(filename='test.log', encoding='utf-8', level=logging.DEBUG)

#Setting up the API keys
try:
    uberduck_auth = secret.uberduck_auth
except Exception as e:
    logging.error(f"Uberduck Key not Found: {e}")
    quit()

try:
    openai.api_key = secret.token
except Exception as e:
    logging.error(f"OpenAI Key not Found: {e}")
    quit()

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
    try:
        logging.info("Script Generation Started")
        reply = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": script},
                {"role": "user", "content": content},
            ]
        )

        # Cleanup of the response 
        if 'choices' not in reply:
            logging.error("Script Generation Failed: 'choices' not in reply")
            return None

        response = reply['choices'][0]['message']['content'] # type: ignore
        response = response.replace("\n\n","\n")
        response = response.split("\n")
        logging.info("Script Generation Finished")

        return response
    except Exception as e:
        logging.error(f"Error occurred in chat_gen: {e}")
        return None


#Creates the voice using the Uberduck API
def gen_voice(text, voice, pos):
    try:
        #Creates the request to the API
        logging.info("Voice Request Started")
        
        for _ in range(10):  # Allow up to 10 attempts
            response = requests.post(
                "https://api.uberduck.ai/speak",
                json=dict(speech=text, voicemodel_uuid=voice),
                auth=uberduck_auth,
            )

            response_json = response.json()

            if 'detail' in response_json:  # Rate limit exceeded
                logging.warning("Rate limit exceeded. Sleeping for 15 seconds before retrying...")
                time.sleep(15)  # Wait for rate limit reset
                continue
            
            if 'uuid' in response_json:
                logging.info("Voice Request Finished")
                audio_uuid = response_json["uuid"]
                break
            else:
                logging.error("Voice Request Failed: UUID not found in response")
                logging.debug(f"Voice Request Failed: {response_json}")
                return None, None
        else:
            logging.error("Voice Request Failed after 10 attempts due to rate limiting.")
            return None, None

        #Checks the status of the request and downloads the audio file
        logging.info("Voice Download Started")
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
        logging.error("Voice Download Failed: Unable to download audio after 50 attempts")
    except Exception as e:
        logging.error(f"Error occurred in gen_voice: {e}")
        return None, None
    finally:
        logging.info("Voice Download Finished")

#Creates the script file
def create_script(text, speaker, pos):
    try:
        logging.info("Script Creation Started")
        with open("script.txt", 'a') as f:
            d = sf.SoundFile(f"speech{pos}.wav")
            f.write(f'{speaker}:{text}:{(d.frames / d.samplerate)}\n')
        logging.info("Script Creation Finished")
    except FileNotFoundError:
        logging.error(f"File speech{pos}.wav not found.")
    except Exception as e:
        logging.error(f"An unexpected error occurred while creating script: {e}")

#Merges the audio files  
def merge_wav_files(file_list, output_filename):
    try:
        logging.info("Audio Merge Started")
        # Open first valid file and get details
        params = None
        for filename in file_list:
            try:
                with wave.open(filename, 'rb') as wave_file:
                    params = wave_file.getparams()
                    break
            except wave.Error:
                logging.warning(f"Skipping invalid file: {filename}")
                continue

        if params is None:
            logging.error("Audio Merge Failed: No valid files found in the list")
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
                    logging.warning(f"Skipping invalid file: {filename}")
        logging.info("Audio Merge Finished")

    except Exception as e:
        logging.error(f"An unexpected error occurred in merge_wav_files: {e}")

#Cleans up file that will be made later
def cleanup():
    try:
        logging.info("Cleanup Started")
        for filename in os.listdir(os.getcwd()):
            if filename.startswith(("speech", "output", "script")):
                try:
                    os.remove(filename)
                    logging.info(f"Deleted file: {filename}")
                except Exception as e:
                    logging.error(f"Error deleting file {filename}: {e}")
        logging.info("Cleanup Finished")
    except Exception as e:
        logging.error(f"An unexpected error occurred during cleanup: {e}")

#Main function
def run():
    try:
        logging.info("Program Started")
        #Cleans up the files
        cleanup()

        #Chooses a random topic and creates the script
        rand_prompt = random.choice(prompts)
        script = chat_gen(base_promt,rand_prompt)

        if script is None:
            logging.error("Script generation failed")
            return

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
            if file_path is not None:
                create_script(script[pos].split(":")[1].strip(), script[pos].split(":")[0].strip(), pos)

        #Check if all the speech.wav files are there
        for i in range(len(script)):
            if not os.path.isfile(f"speech{i}.wav"):
                logging.error(f"Audio file speech{i}.wav was not created correctly")
                return

        #Merges the audio files into one
        merge_wav_files([f"speech{i}.wav" for i in range(len(script))], "output.wav")

        #Cleans up the audio files
        for filename in os.listdir(os.getcwd()):
            if filename.startswith("speech"):
                try:
                    os.remove(filename)
                    logging.info(f"Removed file: {filename}")
                except Exception as e:
                    logging.error(f"Failed to remove file {filename}: {e}")

        logging.info("Program Finished")

    except Exception as e:
        logging.error(f"An unexpected error occurred in run: {e}")

x = 1
while True:
    run()
    if 'output.wav' in os.listdir(os.getcwd()):
        print(f"Run {x} is successful. Output.wav is created.")
    else:
        print(f"Run {x} is unsuccessful. Output.wav is not created.")
    x += 1