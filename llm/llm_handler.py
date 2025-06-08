import requests
from colorama import Fore, Style
import re
import platform
from typing import Tuple, Optional

API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = "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"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

MODEL = "mistralai/mistral-7b-instruct:free"

def get_os_specific_prompt() -> str:
    """Get OS-specific installation instructions"""
    system = platform.system().lower()
    if system == 'windows':
        return (
            "For Windows, provide installation command using one of these formats:\n"
            "- winget install [PackageName]\n"
            "- choco install [PackageName]\n"
            "- scoop install [PackageName]\n"
            "- pip install [PackageName]\n"
            "- npm install -g [PackageName]\n"
        )
    elif system == 'linux':
        return (
            "For Linux, provide installation command using one of these formats:\n"
            "- apt install [PackageName]\n"
            "- yum install [PackageName]\n"
            "- dnf install [PackageName]\n"
            "- pip install [PackageName]\n"
            "- npm install -g [PackageName]\n"
        )
    elif system == 'darwin':
        return (
            "For macOS, provide installation command using one of these formats:\n"
            "- brew install [PackageName]\n"
            "- pip install [PackageName]\n"
            "- npm install -g [PackageName]\n"
        )
    return "Provide the appropriate installation command for your system."

def handle_unknown_command(command: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Ask the LLM about an unknown command and return both the explanation
    and an extracted installation command if available.
    """
    print(Fore.YELLOW + f"[Aegis AI] Thinking about: '{command}'..." + Style.RESET_ALL)

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    f"You are an AI inside a developer CLI shell on {platform.system()}. "
                    "A user typed an unknown command. Your task is to analyze what it might be and provide an installation command. "
                    "IMPORTANT: You MUST respond in this EXACT format:\n\n"
                    "EXPLANATION: [brief explanation of what the command is for]\n"
                    "INSTALL: [exact installation command using the appropriate package manager for the user's OS]\n\n"
                    f"{get_os_specific_prompt()}\n\n"
                    "Example responses for Windows:\n"
                    "EXPLANATION: Maven is a build automation tool for Java projects\n"
                    "INSTALL: choco install maven\n\n"
                    "EXPLANATION: Ruby is a dynamic programming language\n"
                    "INSTALL: winget install RubyInstallerTeam.RubyWithDevKit\n\n"
                    "EXPLANATION: Composer is a dependency manager for PHP\n"
                    "INSTALL: scoop install composer\n\n"
                    "DO NOT add anything else, just respond with these two lines."
                )
            },
            {
                "role": "user",
                "content": f"The user typed: '{command}'"
            }
        ]
    }
    
    try:
        print(Fore.BLUE + f"[Aegis Debug] Sending request to API with model: {MODEL}" + Style.RESET_ALL)
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        
        if response.status_code == 200:
            reply = response.json()["choices"][0]["message"]["content"].strip()
            print(Fore.CYAN + f"[LLM AI Response]:\n{reply}" + Style.RESET_ALL)
            
            # Extract explanation and install command
            explanation = None
            install_cmd = None
            
            for line in reply.split('\n'):
                if line.startswith('EXPLANATION:'):
                    explanation = line.replace('EXPLANATION:', '').strip()
                elif line.startswith('INSTALL:'):
                    install_cmd = line.replace('INSTALL:', '').strip()
            
            if not install_cmd:
                print(Fore.RED + "[Aegis] No installation command provided" + Style.RESET_ALL)
                return explanation, None
                
            return explanation, install_cmd
        else:
            print(Fore.RED + f"[Aegis] LLM failed: {response.status_code} {response.reason}" + Style.RESET_ALL)
            print(Fore.RED + f"Response: {response.text}" + Style.RESET_ALL)
            return None, None
            
    except Exception as e:
        print(Fore.RED + f"[Aegis] LLM Error: {e}" + Style.RESET_ALL)
        return None, None