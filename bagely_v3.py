from openai import OpenAI # NOTE!!!: configured for https://console.groq.com api keys!!!!
import json
import sys
import subprocess
import os
import colorama
import re

#import config
dir_path = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(dir_path, "config.json")
with open(config_path, "r", encoding="utf-8") as file:
    config = json.load(file)

# Auto config

if sys.platform.startswith('win'):
    ID_os = "windows"
elif sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
    ID_os = "linux"
else:
    ID_os = "Couldn't be verified."

default = config["default"][0]
api_key = default["api_key"]
model = default["model"]
baseurl = default["baseurl"]

default_reason = config["default_reason"][0]
reason_api_key = default_reason["api_key"]
reason_model = default_reason["model"]
reason_baseurl = default_reason["baseurl"]

groq_alternative = config["groq_alternative"][0]
alternative_api_key = groq_alternative["api_key"]
alternative_model = groq_alternative["model"]
alternative_baseurl = groq_alternative["baseurl"]

apis = [
    ("Default", api_key, baseurl),
    ("Reason", reason_api_key, reason_baseurl),
    ("Alternative", alternative_api_key, alternative_baseurl)
]

# config
memory = ""
colorama.init(autoreset=True)

banner = """ ▄▄▄▄    ▄▄▄        ▄████ ▓█████  ██▓   ▓██   ██▓
▓█████▄ ▒████▄     ██▒ ▀█▒▓█   ▀ ▓██▒    ▒██  ██▒
▒██▒ ▄██▒██  ▀█▄  ▒██░▄▄▄░▒███   ▒██░     ▒██ ██░
▒██░█▀  ░██▄▄▄▄██ ░▓█  ██▓▒▓█  ▄ ▒██░     ░ ▐██▓░
░▓█  ▀█▓ ▓█   ▓██▒░▒▓███▀▒░▒████▒░██████▒ ░ ██▒▓░
░▒▓███▀▒ ▒▒   ▓▒█░ ░▒   ▒ ░░ ▒░ ░░ ▒░▓  ░  ██▒▒▒ 
▒░▒   ░   ▒   ▒▒ ░  ░   ░  ░ ░  ░░ ░ ▒  ░▓██ ░▒░ 
 ░    ░   ▒   ░ ░   ░    ░     ░ ░   ▒ ▒ ░░  
 ░            ░  ░      ░    ░  ░    ░  ░░ ░     
      ░                                  ░ ░ V3
                Espress0 2026
================================================="""

system_message = f"""Hello, your name is Bagely. You are an AI assistant that helps the user with various tasks.
You are running through the OpenAI Python library and your text responses are displayed directly in the user's terminal.
Do NOT use Markdown formatting. Use plain text only.
You have access to the user's integrated terminal through a command system.
To request a terminal command, output ONLY the command in this exact format:
['command-here']
Example:
['ping google.com']
The text inside [' and '] is the command that will be executed by Python's subprocess system.
Only use a terminal command when it is actually necessary to complete the user's request.
Commands are executed one at a time. After a command is executed, its output will be sent back to you.
When you receive command output, analyze it and respond to the user based on the result.
You may request another command after receiving the previous command's output if necessary.
Do not put explanations, comments, or other text on the same line as a command.
When a command is needed, output the command instead of pretending that you executed it yourself.
If no command is needed, respond normally in plain text.
The operating system is: {ID_os}
"""

C_INFO = colorama.Fore.CYAN
C_SUCCESS = colorama.Fore.GREEN
C_WARNING = colorama.Fore.YELLOW
C_ERROR = colorama.Fore.RED
C_COMMAND = colorama.Fore.BLUE
C_REASONING = colorama.Fore.MAGENTA
C_USER = colorama.Fore.LIGHTBLUE_EX
C_ASSISTANT = colorama.Fore.WHITE
C_MUTED = colorama.Fore.LIGHTBLACK_EX
C_RESET = colorama.Style.RESET_ALL

#functions

def clear_terminal():
    if sys.platform.startswith('win'):
        os.system('cls')
    elif sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
        os.system('clear')
    else:
        print(C_ERROR + "[ERROR] Unsupported operating system. Please clear the terminal manually.")

def check_api(api_key, baseurl):
    try:
        client = OpenAI(
            api_key=api_key,
            base_url=baseurl
        )

        client.models.list()
        return True

    except Exception:
        return False

def health_check():
    default_status = False
    reasoning_status = False
    alternative_status = False

    print(C_INFO + "[INFO] Checking API health...")

    for name, api_key, baseurl in apis:
        try:
            client = OpenAI(
                api_key=api_key,
                base_url=baseurl
            )

            client.models.list()
            
            print(C_INFO + f"[INFO] {name} API is healthy.")

            if name == "Default":
                default_status = True
            elif name == "Reason":
                reasoning_status = True
            elif name == "Alternative":
                alternative_status = True

        except Exception as error:
            print(C_ERROR + f"[ERROR] {name} API is not healthy: {error!r}")

    return default_status, reasoning_status, alternative_status

def ask_for_input():
    global banner

    prompt = input(C_USER + "User > " + C_RESET)

    if prompt == "/exit":
        print(C_INFO + "[INFO] Exiting...")
        exit()

    if prompt == "":
        print(C_INFO + "[INFO] Please enter a prompt.")
        return ask_for_input()

    if prompt == "/clear":
        clear_terminal()
        print(C_ERROR + banner)
        return ask_for_input()

    if prompt == "/help":
        print(C_INFO + "Available commands:")
        print(C_INFO + "/exit - Exit the program")
        print(C_INFO + "/clear - Clear the terminal")
        print(C_INFO + "/help - Show this help message")
        print(C_INFO + "/default - Use the default model")
        print(C_INFO + "/reason - Use the reasoning model")
        print(C_INFO + "/alternative - Use the alternative model")
        return ask_for_input()
    
    if prompt.startswith("/default"):
        prompt = prompt.removeprefix("/default").strip()
        UseModelForce = "Default"

    elif prompt.startswith("/reason"):
        prompt = prompt.removeprefix("/reason").strip()
        UseModelForce = "Reasoning"

    elif prompt.startswith("/alternative"):
        prompt = prompt.removeprefix("/alternative").strip()
        UseModelForce = "Alternative"

    else:
        UseModelForce = "Default"
    
    return prompt, UseModelForce

def send_request(prompt, UseModelForce, memory, system_message):
    global default_status,reasoning_status ,alternative_status
    if UseModelForce == "Default":
        api_key = default["api_key"]
        baseurl = default["baseurl"]
        model = default["model"]

    elif UseModelForce == "Reasoning":
        api_key = default_reason["api_key"]
        baseurl = default_reason["baseurl"]
        model = default_reason["model"]

    elif UseModelForce == "Alternative":
        api_key = groq_alternative["api_key"]
        baseurl = groq_alternative["baseurl"]
        model = groq_alternative["model"]

    else:
        api_key = default["api_key"]
        baseurl = default["baseurl"]
        model = default["model"]

    try:
        client = OpenAI(
            api_key=api_key,
            base_url=baseurl
        )

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": "this is your earlier conversation: "+ memory},
                {"role": "user", "content": prompt}
            ]
        )

        memory += f"User>{prompt}"
        memory += f"Bagely>{response.choices[0].message.content}"
        return response, memory

    except Exception as error:
        print(C_ERROR + f"[ERROR] Failed to send request: {error}")
        return None, memory

def parse_command(response, memory):
    try:
        cmd = re.search(r"\['(.*?)'\]", response.choices[0].message.content)
        if not cmd:
            return memory, None, None
        cmd = cmd.group(1)
        print(C_COMMAND + "Command > " + cmd)
        cmd_output = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        memory += f"command output:{cmd_output}"
        return memory, cmd, cmd_output
    except Exception as error:
        print(C_ERROR + f"[ERROR] {error}")
        return memory, None, None

# main loop
print(C_ERROR + banner)

health_check()

while True:
    prompt, UseModelForce = ask_for_input()
    response, memory = send_request(prompt, UseModelForce, memory, system_message)

    if response is None:
        continue

    reasoning_text = getattr(response.choices[0].message, "reasoning", None)

    if reasoning_text:
        print(C_REASONING + reasoning_text + "\n" + C_RESET)

    print(C_ASSISTANT + "Bagely > " + response.choices[0].message.content + C_RESET)

    memory, cmd, cmd_output = parse_command(response, memory)

    if cmd:
        while cmd:
            response, memory = send_request("The command returned this output:\n" + cmd_output.stdout + "\nComment on the result or provide the next command if needed.", UseModelForce, memory, system_message)

            if response is None:
                break

            reasoning_text = getattr(response.choices[0].message, "reasoning", None)

            if reasoning_text:
                print(C_REASONING + reasoning_text + "\n" + C_RESET)

            print(C_ASSISTANT + "Bagely > " + response.choices[0].message.content + C_RESET)

            memory, cmd, cmd_output = parse_command(response, memory)