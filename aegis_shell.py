import os
import sys
# Ensure current directory is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from commands.command_handler import handle_command
from config_loader import load_command_mappings, load_config
from utils.permissions import check_admin_rights
from colorama import Fore, Style, init
init(convert=True)
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style as PromptStyle

# Import the FAQ module
try:
    from commands.faq import show_faq
except ImportError:
    def show_faq():
        print(Fore.RED + "FAQ module not found!")

init(autoreset=True)

def display_ascii_art():
    """Display ASCII art from the resource file"""
    try:
        art_path = os.path.join(os.path.dirname(__file__), "resources", "ascii_art.txt")
        if os.path.exists(art_path):
            with open(art_path, "r") as f:
                art = f.read()
            print(Fore.CYAN + art + Style.RESET_ALL)
        else:
            print(Fore.RED + "ASCII art file not found at:", art_path)
    except Exception as e:
        print(Fore.RED + f"Error displaying ASCII art: {e}")

def main():
    os.system("cls" if os.name == "nt" else "clear")
    
    # Display ASCII art
    display_ascii_art()
    
    print(Fore.CYAN + Style.BRIGHT + "Welcome to the ultimate AI-powered terminal shell.")
    print(Fore.MAGENTA + "Made with ❤️  by Tanish, Nidhi & Nishant")
    print(Fore.YELLOW + "Type 'exit' to quit. Type 'faq' for help.\n")

    try:
        mappings = load_command_mappings()
        print(f"DEBUG: Loaded {len(mappings)} command mappings")
    except Exception as e:
        print(f"Error loading mappings: {e}")
        mappings = {}
    
    config = load_config()
    
    # Add FAQ command to mappings
    if "faq" not in mappings:
        mappings["faq"] = {
            "language": "internal",
            "description": "Show frequently asked questions"
        }
    
    # Setup advanced autocomplete using prompt_toolkit
    command_completer = WordCompleter(list(mappings.keys()), ignore_case=True)
    
    # Custom prompt style
    prompt_style = PromptStyle.from_dict({
        'prompt': 'ansicyan bold',
    })
    
    session = PromptSession(
        message=lambda: Fore.CYAN + Style.BRIGHT + "$ aegis-shell " + Style.RESET_ALL,
        completer=command_completer,
        style=prompt_style
    )

    while True:
        try:
            cmd = session.prompt().strip()
            if cmd.lower() == "exit":
                print(Fore.CYAN + "[Aegis] Goodbye, warrior! 🛡️")
                break
            if cmd == "":
                continue
                
            # Special handling for FAQ command
            if cmd.lower() == "faq":
                show_faq()
                continue
                
            handle_command(cmd, mappings, config)
        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        except Exception as e:
            print(Fore.RED + f"[Aegis] Error: {e}")

if __name__ == "__main__":
    if not check_admin_rights():
        print(Fore.RED + "[Aegis] Warning: Admin rights not detected. Some operations may fail.")
    main()