using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;
using UnityEngine.Networking;

public class AudioScriptManager : MonoBehaviour
{
    public AudioSource audioSource;
    public string serverURL = "http://localhost:5000"; // replace with your server's URL

    void Start()
    {
        StartCoroutine(GetDataFromServer());
    }

    IEnumerator GetDataFromServer()
    {
        yield return StartCoroutine(GetAudioClip());
        yield return StartCoroutine(GetScript());
        audioSource.Play();
        StartCoroutine(ProcessScript());
    }

    IEnumerator GetAudioClip()
    {
        using (UnityWebRequest www = UnityWebRequestMultimedia.GetAudioClip(serverURL + "/audio", AudioType.WAV))
        {
            yield return www.SendWebRequest();

            if (www.result == UnityWebRequest.Result.ConnectionError)
            {
                Debug.Log(www.error);
            }
            else
            {
                AudioClip audioClip = DownloadHandlerAudioClip.GetContent(www);
                audioSource.clip = audioClip;
            }
        }
    }

    IEnumerator GetScript()
    {
        using (UnityWebRequest www = UnityWebRequest.Get(serverURL + "/script"))
        {
            yield return www.SendWebRequest();

            if (www.result == UnityWebRequest.Result.ConnectionError)
            {
                Debug.Log(www.error);
            }
            else
            {
                string script = www.downloadHandler.text;
                File.WriteAllText("Assets/script.txt", script);
            }
        }
    }

    IEnumerator ProcessScript()
    {
        string[] scriptLines = File.ReadAllLines("Assets/script.txt");

        foreach (string line in scriptLines)
        {
            string[] parts = line.Split(':');
            string speaker = parts[0].Trim();
            float duration = float.Parse(parts[2].Trim());

            GameObject speakerObject = GameObject.Find(speaker);

            Vector3 lookAtPosition = speakerObject.transform.position;
            lookAtPosition.y += 1.0f;  // Add vertical offset here. Adjust the value as needed.

            Camera.main.transform.LookAt(lookAtPosition);

            yield return new WaitForSeconds(duration);
        }
    }
}