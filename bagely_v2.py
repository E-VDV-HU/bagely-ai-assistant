from openai import OpenAI
import requests
import json
import os
import sys

# variables

api_health= "http://127.0.0.1:8787/health"
api_endpoint = "http://127.0.0.1:8787/v1"
api_key = "sk-arena-local"
user_model = "arena-agent"
skip_health_check = "False"

start_prompt = """Hello, your name is Bagely, you will assist this user in doing various tasks.
This message that has been send is autonomous and does not yet have anything to do with the task the user will give you next.
You are an api endpoint functioning trough the openai library of openai.
While you can make files in your own environment, you will not be able to send them to the user, you will only be able to send text messages.
Those text messages will be sent to the user trough the terminal, so you can use tricks like \\n to make the text more readable.
To confirm you comply with this, please answer with "Bagely mobilized" and stop.
"""


banner = """
 ▄▄▄▄    ▄▄▄        ▄████ ▓█████  ██▓   ▓██   ██▓
▓█████▄ ▒████▄     ██▒ ▀█▒▓█   ▀ ▓██▒    ▒██  ██▒
▒██▒ ▄██▒██  ▀█▄  ▒██░▄▄▄░▒███   ▒██░     ▒██ ██░
▒██░█▀  ░██▄▄▄▄██ ░▓█  ██▓▒▓█  ▄ ▒██░     ░ ▐██▓░
░▓█  ▀█▓ ▓█   ▓██▒░▒▓███▀▒░▒████▒░██████▒ ░ ██▒▓░
░▒▓███▀▒ ▒▒   ▓▒█░ ░▒   ▒ ░░ ▒░ ░░ ▒░▓  ░  ██▒▒▒ 
▒░▒   ░   ▒   ▒▒ ░  ░   ░  ░ ░  ░░ ░ ▒  ░▓██ ░▒░ 
 ░    ░   ░   ▒   ░ ░   ░    ░     ░ ░   ▒ ▒ ░░  
 ░            ░  ░      ░    ░  ░    ░  ░░ ░     
      ░                                  ░ ░     
"""

# config

client = OpenAI(
    base_url=api_endpoint,
    api_key=api_key
)

# functions
def clear_terminal():
    if sys.platform.startswith('win'):
        os.system('cls')
    elif sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
        os.system('clear')
    else:
        print("[ERROR] Unsupported operating system. Please clear the terminal manually.")

def health_check_arena():
    try:
        web_health = requests.get(api_health)
        web_health_data = web_health.json()
    except requests.exceptions.HTTPError as errh:
        print("[ERROR] HTTP error occurred:", errh)
        print("[INFO] Exiting...")
        exit()
    except requests.exceptions.ConnectionError as errc:
        print("[ERROR] Connection error occurred:", errc)
        print("[INFO] Exiting...")
        exit()
    except requests.exceptions.Timeout as errt:
        print("[ERROR] Timeout error occurred:", errt)
        print("[INFO] Exiting...")
        exit()
    
    if web_health_data["ok"] == False:
        print("[ERROR] API is not healthy. Please check the API.")
        exit()
    if web_health_data["bridge"] == False:
        print("[ERROR] Bridge is not healthy. Please check the bridge.")
        exit()

def ask_for_input(prompt):
    prompt = input("User > ")
    if prompt == "exit":
        print("[INFO] Exiting...")
        exit()
    if prompt == "":
        print("[INFO] Please enter a prompt.")
        return ask_for_input(prompt)
    if prompt == "clear":
        clear_terminal()
        print(banner)
        return ask_for_input(prompt)
    return prompt

def send_request(prompt):
    response = client.chat.completions.create(
        model=user_model,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    print("Bagely > ", response.choices[0].message.content)
    print("[INFO] VERBOSE INFO ===")
    print(response)

# main loop
def main():
    clear_terminal()
    print(banner)

    if skip_health_check == "False":
        print("[INFO] Doing health check...")
        health_check_arena()
    else:
        print("[INFO] Skipping health check...")
    
    print("[INFO] Starting Bagely...")
    prompt = start_prompt
    send_request(prompt)
    while True:
        prompt = ask_for_input(prompt)
        send_request(prompt)

main()