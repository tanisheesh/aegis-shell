import os
import sys
import json
import platform
from pathlib import Path
from colorama import init, Fore, Style
from cryptography.fernet import Fernet
from prompt_toolkit import PromptSession
import requests

# Initialize colorama
init()

from utils.system_monitor import SystemMonitor
from utils.command_executor import CommandExecutor
from utils.security_manager import SecurityManager
from llm.llm_handler import handle_unknown_command
from features.documentation import DocumentationManager

class AegisShell:
    def __init__(self):
        self.config_dir = Path.home() / '.aegis'
        self.config_file = self.config_dir / 'config.json'
        self.encryption_key = None
        self.model = None
        self.api_key = None
        self.setup_config()
        self.system_monitor = SystemMonitor()
        self.command_executor = CommandExecutor()
        self.security_manager = SecurityManager()
        self.session = None
        self.doc_manager = DocumentationManager()
        self.setup_prompt()
        
    def setup_config(self):
        """Set up configuration and handle first-time setup"""
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up encryption
        self.setup_encryption()
        
        # Load or create configuration
        if not self.config_file.exists():
            self.first_time_setup()
        else:
            self.load_config()
            
    def setup_encryption(self):
        """Set up encryption for API key storage"""
        key_file = self.config_dir / '.key'
        if not key_file.exists():
            key = Fernet.generate_key()
            key_file.parent.mkdir(parents=True, exist_ok=True)
            with open(key_file, 'wb') as f:
                f.write(key)
        else:
            with open(key_file, 'rb') as f:
                key = f.read()
        self.encryption_key = Fernet(key)
        
    def encrypt_api_key(self, api_key):
        """Encrypt API key for storage"""
        return self.encryption_key.encrypt(api_key.encode()).decode()
        
    def decrypt_api_key(self, encrypted_key):
        """Decrypt stored API key"""
        return self.encryption_key.decrypt(encrypted_key.encode()).decode()
        
    def get_openrouter_models(self):
        """Get list of available models from OpenRouter"""
        try:
            response = requests.get('https://openrouter.ai/api/v1/models')
            if response.status_code == 200:
                return response.json().get('data', [])
            return []
        except Exception:
            return []
            
    def first_time_setup(self):
        """Handle first-time setup and API key configuration"""
        print(f"\n{Fore.YELLOW}Welcome to Aegis Shell!{Style.RESET_ALL}")
        print("Let's set up your configuration...")
        
        # Get available models
        models = self.get_openrouter_models()
        if not models:
            print(f"{Fore.RED}Error: Could not fetch available models{Style.RESET_ALL}")
            sys.exit(1)
            
        # Show model selection
        print(f"\n{Fore.CYAN}Available OpenRouter Models:{Style.RESET_ALL}")
        for i, model in enumerate(models, 1):
            print(f"{i}. {model['name']} - {model['description']}")
            
        # Get model selection
        while True:
            try:
                choice = int(input(f"\n{Fore.GREEN}Select a model (enter number): {Style.RESET_ALL}"))
                if 1 <= choice <= len(models):
                    self.model = models[choice - 1]['name']
                    break
                print(f"{Fore.RED}Invalid selection{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}Please enter a number{Style.RESET_ALL}")
                
        # Get API key
        while True:
            self.api_key = input(f"\n{Fore.GREEN}Enter your OpenRouter API key: {Style.RESET_ALL}")
            if self.api_key:
                break
            print(f"{Fore.RED}API key cannot be empty{Style.RESET_ALL}")
            
        # Save configuration
        config = {
            'model': self.model,
            'api_key': self.encrypt_api_key(self.api_key),
            'first_run': False
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
            print(f"\n{Fore.GREEN}Configuration saved successfully!{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error: Failed to save configuration: {e}{Style.RESET_ALL}")
            sys.exit(1)
            
    def load_config(self):
        """Load configuration from file"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                
            self.model = config['model']
            self.api_key = self.decrypt_api_key(config['api_key'])
        except Exception as e:
            print(f"{Fore.RED}Error: Failed to load configuration: {e}{Style.RESET_ALL}")
            sys.exit(1)
            
    def setup_prompt(self):
        """Set up the interactive prompt"""
        # Create a simple style without colors
        prompt_style = prompt_style.from_dict({})
        
        self.session = PromptSession(
            message="$ aegis-shell ",
            style=prompt_style
        )
        
    def display_welcome(self):
        """Display welcome message"""
        print(f"\n{Fore.CYAN}Welcome to the ultimate AI-powered terminal shell.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Made with ❤️  by Tanish, Nidhi & Nishant{Style.RESET_ALL}\n")
        print(f"{Fore.GREEN}Quick Commands:{Style.RESET_ALL}")
        print(f"  • Type 'docs' to view comprehensive documentation")
        print(f"  • Type 'exit' to quit\n")
        
    def start(self):
        """Start the shell"""
        self.display_welcome()
        
        while True:
            try:
                # Get command from user
                command = input(f"{Fore.GREEN}aegis-shell>{Style.RESET_ALL} ").strip()
                
                # Handle exit command
                if command.lower() == 'exit':
                    print(f"\n{Fore.YELLOW}Goodbye!{Style.RESET_ALL}")
                    break
                    
                # Handle docs command
                if command.lower() == 'docs':
                    self.show_documentation()
                    continue
                    
                # Handle other commands
                self.handle_command(command)
                
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Use 'exit' to quit{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
                
    def handle_command(self, command):
        """Handle shell commands"""
        # Add your command handling logic here
        pass
        
    def show_documentation(self):
        """Show documentation"""
        # Add your documentation display logic here
        pass
        
def main():
    shell = AegisShell()
    shell.start()
    
if __name__ == "__main__":
    main()