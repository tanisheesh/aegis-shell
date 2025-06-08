import os
import sys
import shutil
import subprocess
import json
import platform
from pathlib import Path
import winreg
import getpass
import base64
from cryptography.fernet import Fernet
import requests

class AegisInstaller:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        self.install_dir = Path(os.environ.get('PROGRAMFILES', 'C:\\Program Files')) / 'AegisShell'
        self.config_dir = Path.home() / '.aegis'
        self.requirements_file = self.base_dir / 'requirements.txt'
        self.encryption_key = None
        
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
        
    def check_python(self):
        """Check if Python is installed and has correct version"""
        if sys.version_info < (3, 8):
            print("Error: Python 3.8 or higher is required")
            return False
        return True
        
    def install_dependencies(self):
        """Install required Python packages"""
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', str(self.requirements_file)])
            return True
        except subprocess.CalledProcessError:
            print("Error: Failed to install dependencies")
            return False
            
    def copy_files(self):
        """Copy shell files to installation directory"""
        try:
            # Create installation directory
            self.install_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy all Python files and directories
            for item in self.base_dir.glob('*'):
                if item.name not in ['installer.py', 'build', 'dist', '__pycache__']:
                    if item.is_file():
                        shutil.copy2(item, self.install_dir)
                    elif item.is_dir():
                        shutil.copytree(item, self.install_dir / item.name, dirs_exist_ok=True)
                        
            return True
        except Exception as e:
            print(f"Error: Failed to copy files: {e}")
            return False
            
    def add_to_path(self):
        """Add installation directory to system PATH"""
        if platform.system() == 'Windows':
            try:
                # Get current PATH
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment', 0, winreg.KEY_ALL_ACCESS) as key:
                    path_value, _ = winreg.QueryValueEx(key, 'Path')
                    paths = path_value.split(';')
                    
                    # Add installation directory if not in PATH
                    if str(self.install_dir) not in paths:
                        paths.append(str(self.install_dir))
                        new_path = ';'.join(paths)
                        winreg.SetValueEx(key, 'Path', 0, winreg.REG_EXPAND_SZ, new_path)
                        
                # Notify system of PATH change
                subprocess.run(['setx', 'PATH', f'%PATH%;{self.install_dir}'], shell=True)
                return True
            except Exception as e:
                print(f"Error: Failed to add to PATH: {e}")
                return False
        else:
            # For Linux/Mac
            try:
                shell = os.environ.get('SHELL', '')
                if 'bash' in shell:
                    rc_file = Path.home() / '.bashrc'
                elif 'zsh' in shell:
                    rc_file = Path.home() / '.zshrc'
                else:
                    return False
                    
                with open(rc_file, 'a') as f:
                    f.write(f'\nexport PATH="$PATH:{self.install_dir}"\n')
                return True
            except Exception as e:
                print(f"Error: Failed to add to PATH: {e}")
                return False
                
    def get_openrouter_models(self):
        """Get list of available models from OpenRouter"""
        try:
            response = requests.get('https://openrouter.ai/api/v1/models')
            if response.status_code == 200:
                return response.json().get('data', [])
            return []
        except Exception:
            return []
            
    def setup_first_time(self):
        """Handle first-time setup and API key configuration"""
        # Create config directory
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up encryption
        self.setup_encryption()
        
        # Get available models
        models = self.get_openrouter_models()
        if not models:
            print("Error: Could not fetch available models")
            return False
            
        # Show model selection
        print("\nAvailable OpenRouter Models:")
        for i, model in enumerate(models, 1):
            print(f"{i}. {model['name']} - {model['description']}")
            
        # Get model selection
        while True:
            try:
                choice = int(input("\nSelect a model (enter number): "))
                if 1 <= choice <= len(models):
                    selected_model = models[choice - 1]
                    break
                print("Invalid selection")
            except ValueError:
                print("Please enter a number")
                
        # Get API key
        while True:
            api_key = getpass.getpass("\nEnter your OpenRouter API key: ")
            if api_key:
                break
            print("API key cannot be empty")
            
        # Save configuration
        config = {
            'model': selected_model['name'],
            'api_key': self.encrypt_api_key(api_key),
            'first_run': False
        }
        
        try:
            with open(self.config_dir / 'config.json', 'w') as f:
                json.dump(config, f, indent=4)
            return True
        except Exception as e:
            print(f"Error: Failed to save configuration: {e}")
            return False
            
    def create_shortcuts(self):
        """Create desktop and start menu shortcuts"""
        if platform.system() == 'Windows':
            try:
                import winshell
                from win32com.client import Dispatch
                
                # Desktop shortcut
                desktop = winshell.desktop()
                path = os.path.join(desktop, "Aegis Shell.lnk")
                
                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortCut(path)
                shortcut.Targetpath = str(self.install_dir / 'aegis_shell.py')
                shortcut.WorkingDirectory = str(self.install_dir)
                shortcut.save()
                
                # Start menu shortcut
                start_menu = winshell.start_menu()
                path = os.path.join(start_menu, "Programs", "Aegis Shell.lnk")
                
                shortcut = shell.CreateShortCut(path)
                shortcut.Targetpath = str(self.install_dir / 'aegis_shell.py')
                shortcut.WorkingDirectory = str(self.install_dir)
                shortcut.save()
                
                return True
            except Exception as e:
                print(f"Error: Failed to create shortcuts: {e}")
                return False
        return True
        
    def install(self):
        """Run the complete installation process"""
        print("Starting Aegis Shell installation...")
        
        # Check Python version
        if not self.check_python():
            return False
            
        # Install dependencies
        print("\nInstalling dependencies...")
        if not self.install_dependencies():
            return False
            
        # Copy files
        print("\nCopying files...")
        if not self.copy_files():
            return False
            
        # Add to PATH
        print("\nAdding to system PATH...")
        if not self.add_to_path():
            return False
            
        # Create shortcuts
        print("\nCreating shortcuts...")
        if not self.create_shortcuts():
            return False
            
        # First-time setup
        print("\nSetting up configuration...")
        if not self.setup_first_time():
            return False
            
        print("\nInstallation completed successfully!")
        print(f"Aegis Shell has been installed to: {self.install_dir}")
        print("You can now run 'aegis-shell' from any terminal")
        return True
        
def main():
    installer = AegisInstaller()
    installer.install()
    
if __name__ == "__main__":
    main() 