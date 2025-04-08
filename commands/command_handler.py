import os
import subprocess
import json
import sys
import importlib
import shutil
from colorama import Fore, Style

# Add the parent directory to sys.path to enable relative imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.installers import install_package, is_python_package_installed
from llm.llm_handler import handle_unknown_command
from config_loader import load_command_mappings, save_command_mappings

# Try importing the FAQ module
try:
    from commands.faq import show_faq
except ImportError:
    def show_faq():
        print(Fore.RED + "FAQ module not found!")

def is_command_installed(command):
    """Check if a command exists in the system path."""
    # First check if it's available directly as a command
    try:
        if shutil.which(command) is not None:
            return True
    except Exception:
        pass
    
    # Then try using system-specific commands
    try:
        return subprocess.call(['where' if os.name == 'nt' else 'which', command],
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL) == 0
    except Exception:
        return False

def is_package_installed(package_name, language="system"):
    """Check if a package is installed based on language."""
    if language == "python":
        return is_python_package_installed(package_name)
    elif language == "javascript":
        # Check if it's a global npm package
        try:
            result = subprocess.run(['npm', 'list', '-g', package_name], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE,
                                   text=True)
            return package_name in result.stdout
        except Exception:
            return False
    elif language == "internal":
        # Internal commands are always "installed"
        return True
    else:
        return is_command_installed(package_name)

def execute_system_command(command):
    """Execute a system command (cmd or PowerShell) and return the result."""
    print(Fore.CYAN + f"[Aegis] Executing system command: {command}" + Style.RESET_ALL)
    
    try:
        # First try with cmd.exe for CMD commands
        if os.name == 'nt':  # For Windows
            # Detect PowerShell commands (they often contain PowerShell-specific syntax)
            powershell_indicators = ['Get-', '-Path', 'ForEach-Object', 'Out-File', 
                                     '|', '$_', '-Filter', 'Select-Object']
                                     
            use_powershell = any(indicator in command for indicator in powershell_indicators)
            
            if use_powershell:
                # Execute with PowerShell
                process = subprocess.Popen(
                    ['powershell', '-Command', command],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            else:
                # Execute with CMD
                process = subprocess.Popen(
                    ['cmd', '/c', command],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
        else:  # For Unix-like systems
            # Use bash
            process = subprocess.Popen(
                ['bash', '-c', command],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            if stdout:
                print(stdout)
            print(Fore.GREEN + f"[Aegis] Command executed successfully ✅" + Style.RESET_ALL)
            return True
        else:
            if stderr:
                print(Fore.RED + stderr + Style.RESET_ALL)
            print(Fore.RED + f"[Aegis] Command execution failed with return code {process.returncode} ❌" + Style.RESET_ALL)
            return False
            
    except Exception as e:
        print(Fore.RED + f"[Aegis] Error executing command: {e}" + Style.RESET_ALL)
        return False

def handle_command(command, mappings, config):
    """Handle the entered command by checking if it exists and offering installation options."""
    print(f"DEBUG: Checking command: '{command}'")
    print(f"DEBUG: Available mappings: {list(mappings.keys())}")
    
    # Extract the base command (first word) for checking mappings
    base_command = command.split()[0] if ' ' in command else command
    
    # Handle internal commands
    if base_command.lower() == "faq":
        show_faq()
        return True
    
    # Special case handlers for common development tools
    if base_command == "mvn" or base_command == "maven":
        print(Fore.YELLOW + "[Aegis] Maven commands detected.")
        if not is_command_installed("mvn"):
            print(Fore.YELLOW + "[Aegis] Maven not found on your system.")
            confirm = input("[Aegis] Would you like to install Maven? [y/N]: ").strip().lower()
            if confirm == "y":
                # Use platform-specific installation
                if os.name == "nt":  # Windows
                    install_package("Apache.Maven", "winget")
                else:  # Unix-like
                    if is_command_installed("apt"):
                        install_package("maven", "apt")
                    elif is_command_installed("brew"):
                        install_package("maven", "brew")
                    else:
                        print(Fore.YELLOW + "[Aegis] Please install Maven manually from https://maven.apache.org/download.cgi")
            return True
    
    # Check if it's in our mappings
    is_in_mappings = base_command in mappings
    if is_in_mappings:
        info = mappings[base_command]
        print(f"DEBUG: Found mapping for '{base_command}': {info}")
        language = info.get("language", "system")
        
        # Special handling for internal commands
        if language == "internal":
            if base_command.lower() == "faq":
                show_faq()
            else:
                print(Fore.YELLOW + f"[Aegis] Internal command '{base_command}' not implemented.")
            return True
        
        # Check if already installed
        if is_package_installed(base_command, language):
            print(Fore.GREEN + f"[Aegis] '{base_command}' is already installed ✅")
            
            # If this is a complete command (not just the package name), execute it
            if base_command != command:
                return execute_system_command(command)
                
            return True
        
        # Handle multi-language packages
        if language == "multi" and "options" in info:
            options = info["options"]
            print(Fore.YELLOW + f"[Aegis] Found multiple options for '{base_command}':")
            for i, (env, cmd) in enumerate(options.items(), 1):
                print(f"{i}. {env.capitalize()} (install with {cmd.split()[0]})")
            
            choice = input("Choose option: ").strip()
            try:
                choice_idx = int(choice) - 1
                chosen_env = list(options.keys())[choice_idx]
                install_cmd = options[chosen_env]
                installer, package = parse_install_command(install_cmd)
                if installer and package:
                    install_package(package, installer)
            except (ValueError, IndexError):
                print(Fore.RED + "[Aegis] Invalid selection.")
            return True
        
        # Handle normal packages
        if "install_cmd" in info:
            install_cmd = info["install_cmd"]
            installer, package = parse_install_command(install_cmd)
            
            print(Fore.YELLOW + f"[Aegis] '{base_command}' not found on your system. Installation command: {install_cmd}")
            confirm = input("Do you want to install it? [y/N]: ").strip().lower()
            if confirm == "y":
                success = install_package(package, installer)
                if success:
                    # If this was a full command (not just package name), execute it after installation
                    if base_command != command:
                        print(Fore.GREEN + "[Aegis] Installation successful. Now executing your original command.")
                        return execute_system_command(command)
            return True
    
    # If command is not in mappings, check if it's installed or try to execute it directly
    if is_command_installed(base_command):
        print(Fore.GREEN + f"[Aegis] Command '{base_command}' exists ✅")
        # Execute the full command directly
        return execute_system_command(command)
    
    # Try executing as a system command anyway (might be a built-in cmd/PowerShell command)
    print(Fore.YELLOW + f"[Aegis] Attempting to run '{command}' as a system command...")
    if execute_system_command(command):
        return True
    
    # Handle special case for apt/apt-get (common confusion on Windows)
    if base_command in ["apt", "apt-get"] and os.name == "nt":
        print(Fore.YELLOW + "[Aegis] 'apt' is a Linux package manager and isn't available on Windows.")
        print(Fore.YELLOW + "[Aegis] On Windows, you can use alternatives like:")
        print("1. winget - Windows Package Manager")
        print("2. chocolatey - A package manager for Windows")
        
        choice = input("[Aegis] Would you like to install one of these? (1/2/N): ").strip().lower()
        if choice == "1":
            print(Fore.YELLOW + "[Aegis] Checking if winget is available...")
            if not is_command_installed("winget"):
                print(Fore.YELLOW + "[Aegis] winget requires Windows 10 1809 or later.")
                print(Fore.YELLOW + "[Aegis] Please update the App Installer from the Microsoft Store.")
            else:
                print(Fore.GREEN + "[Aegis] winget is already installed.")
        elif choice == "2":
            print(Fore.YELLOW + "[Aegis] Installing Chocolatey...")
            # Chocolatey needs PowerShell admin
            print(Fore.YELLOW + "[Aegis] Please run PowerShell as Administrator and execute:")
            print(Fore.WHITE + "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))")
        return True
    
    # Unknown command → AI fallback
    print(Fore.YELLOW + f"[Aegis] Unknown command: '{command}'")
    confirm = input("[Aegis] Would you like me to ask the AI for help? [y/N]: ").strip().lower()
    if confirm != "y":
        return False

    suggestion, install_command = handle_unknown_command(command)

    if suggestion:
        print(Fore.MAGENTA + "[LLM AI Response]:")
        print(Fore.WHITE + suggestion)
        
        if install_command:
            installer, pkg = parse_install_command(install_command)
            if installer and pkg:
                confirm2 = input(Fore.YELLOW + "Do you want to install this? [y/N]: ").strip().lower()
                if confirm2 == "y":
                    success = install_package(pkg, installer)
                    if success:
                        # Update mapping with the new command
                        mappings[base_command] = {
                            "language": "system" if installer != "pip" else "python",
                            "install_cmd": install_command
                        }
                        save_command_mappings(mappings)
                        print(Fore.GREEN + f"[Aegis] Added '{base_command}' to known commands.")
                        
                        # If this was a full command (not just installing), run it now
                        if base_command != command:
                            print(Fore.GREEN + "[Aegis] Now executing your original command.")
                            return execute_system_command(command)
                else:
                    print(Fore.RED + "[Aegis] Could not parse install command.")
        else:
            print(Fore.RED + "[Aegis] Could not determine installation method.")
    else:
        print(Fore.RED + "[Aegis] AI could not help with this command.")
    
    return False

def parse_install_command(command_str):
    """Parses installation commands like 'pip install xyz' or 'npm install abc'"""
    try:
        parts = command_str.strip().split()
        if len(parts) >= 3 and parts[1].lower() in ["install", "add"]:
            return parts[0], parts[2]
        elif len(parts) == 2:  # For formats like "apt python3"
            return parts[0], parts[1]
        return None, None
    except Exception as e:
        print(f"Error parsing install command: {e}")
        return None, None