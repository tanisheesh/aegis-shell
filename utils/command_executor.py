import subprocess
import os
import sys
import platform
import shlex
import time
import json
import winreg
from typing import Tuple, Optional, Dict, List
import psutil
from colorama import Fore, Style
from .system_monitor import SystemMonitor
from .security_manager import SecurityManager
from llm.llm_handler import handle_unknown_command

class CommandExecutor:
    def __init__(self):
        self.system_monitor = SystemMonitor()
        self.security_manager = SecurityManager()
        self.command_history = []
        self.success_count = 0
        self.total_count = 0
        self._detect_package_managers()
        self.execution_history: Dict[str, Dict] = {}
        self.install_commands = {
            'maven': {
                'winget': 'winget install Apache.Maven',
                'choco': 'choco install maven',
                'scoop': 'scoop install maven'
            },
            'ruby': {
                'winget': 'winget install RubyInstallerTeam.RubyWithDevKit',
                'choco': 'choco install ruby',
                'scoop': 'scoop install ruby'
            },
            'go': {
                'winget': 'winget install GoLang.Go',
                'choco': 'choco install golang',
                'scoop': 'scoop install go'
            },
            'composer': {
                'winget': 'winget install Composer.Composer',
                'choco': 'choco install composer',
                'scoop': 'scoop install composer'
            },
            'node': {
                'winget': 'winget install OpenJS.NodeJS',
                'choco': 'choco install nodejs',
                'scoop': 'scoop install nodejs'
            }
        }
        
    def _detect_package_managers(self):
        """Detect available package managers on the system"""
        self.package_managers = []
        
        # Windows package managers
        if platform.system().lower() == 'windows':
            if self._check_command('winget'):
                self.package_managers.append('winget')
            if self._check_command('choco'):
                self.package_managers.append('choco')
            if self._check_command('scoop'):
                self.package_managers.append('scoop')
        # Linux package managers
        elif platform.system().lower() == 'linux':
            if self._check_command('apt'):
                self.package_managers.append('apt')
            if self._check_command('yum'):
                self.package_managers.append('yum')
            if self._check_command('dnf'):
                self.package_managers.append('dnf')
        # macOS package managers
        elif platform.system().lower() == 'darwin':
            if self._check_command('brew'):
                self.package_managers.append('brew')
                
        # Universal package managers
        if self._check_command('pip'):
            self.package_managers.append('pip')
        if self._check_command('npm'):
            self.package_managers.append('npm')
            
        print(Fore.CYAN + f"[Aegis] Detected package managers: {', '.join(self.package_managers)}" + Style.RESET_ALL)

    def _check_command(self, command: str) -> bool:
        """Check if a command is available"""
        try:
            subprocess.run(
                [command, '--version'] if command != 'winget' else [command, '--version'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            return True
        except FileNotFoundError:
            return False

    def _install_package(self, install_cmd: str) -> bool:
        """Install a package using the provided command"""
        if not install_cmd:
            return False
            
        # Extract package manager and package name
        parts = install_cmd.split()
        if len(parts) < 3:
            print(Fore.RED + f"[Aegis] Invalid installation command format: {install_cmd}" + Style.RESET_ALL)
            return False
            
        package_manager = parts[0]
        if package_manager not in self.package_managers:
            print(Fore.RED + f"[Aegis] Package manager {package_manager} not available" + Style.RESET_ALL)
            return False
            
        try:
            print(Fore.YELLOW + f"[Aegis] Installing package using: {install_cmd}" + Style.RESET_ALL)
            result = subprocess.run(
                install_cmd.split(),
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                print(Fore.GREEN + "[Aegis] Package installed successfully" + Style.RESET_ALL)
                return True
            else:
                print(Fore.RED + f"[Aegis] Installation failed: {result.stderr}" + Style.RESET_ALL)
                return False
                
        except Exception as e:
            print(Fore.RED + f"[Aegis] Installation error: {e}" + Style.RESET_ALL)
            return False

    def execute_command(self, command: str) -> Tuple[bool, str]:
        """Execute a command with enhanced error handling and installation support"""
        if not command.strip():
            return True, ""

        # Add to history
        self.command_history.append(command)
        self.total_count += 1

        # Security check
        if not self.security_manager.validate_command(command):
            return False, "Command blocked by security policy"

        # Try direct execution first
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                self.success_count += 1
                return True, result.stdout
                
            # If command not found, try to install it
            if "not recognized" in result.stderr or "not found" in result.stderr:
                print(Fore.YELLOW + f"[Aegis] Command not found: {command}" + Style.RESET_ALL)
                
                # Get installation command from AI
                explanation, install_cmd = handle_unknown_command(command)
                
                if explanation and install_cmd:
                    print(Fore.CYAN + f"[Aegis] {explanation}" + Style.RESET_ALL)
                    print(Fore.CYAN + f"[Aegis] Suggested installation command: {install_cmd}" + Style.RESET_ALL)
                    
                    # Ask user for confirmation
                    response = input(Fore.YELLOW + "[Aegis] Would you like to install this package? (y/n): " + Style.RESET_ALL)
                    if response.lower() == 'y':
                        if self._install_package(install_cmd):
                            # Try the original command again
                            return self.execute_command(command)
                        else:
                            return False, "Package installation failed"
                    else:
                        return False, "Installation declined by user"
                else:
                    return False, "Could not determine how to install the package"
            
            return False, result.stderr
            
        except Exception as e:
            return False, str(e)

    def get_success_rate(self) -> float:
        """Get the success rate of executed commands"""
        if self.total_count == 0:
            return 0.0
        return (self.success_count / self.total_count) * 100

    def _get_available_package_manager(self) -> Optional[str]:
        """Get the first available package manager"""
        package_managers = ['winget', 'choco', 'scoop']
        for manager in package_managers:
            try:
                subprocess.run([manager, '--version'], capture_output=True, check=True)
                return manager
            except (subprocess.SubprocessError, FileNotFoundError):
                continue
        return None
        
    def _update_path_environment(self):
        """Update PATH environment variable"""
        try:
            # Get current PATH
            current_path = os.environ['PATH']
            
            # Common installation directories
            new_paths = [
                os.path.join(os.environ['ProgramFiles'], 'Java', 'jdk-*', 'bin'),
                os.path.join(os.environ['ProgramFiles'], 'Go', 'bin'),
                os.path.join(os.environ['ProgramFiles'], 'nodejs'),
                os.path.join(os.environ['ProgramFiles'], 'Ruby*', 'bin'),
                os.path.join(os.environ['ProgramFiles'], 'Maven', 'bin'),
                os.path.join(os.environ['ProgramFiles'], 'ComposerSetup', 'bin'),
                os.path.join(os.environ['LOCALAPPDATA'], 'Programs', 'Ruby*', 'bin'),
                os.path.join(os.environ['LOCALAPPDATA'], 'Programs', 'Go', 'bin'),
                os.path.join(os.environ['LOCALAPPDATA'], 'Programs', 'nodejs'),
                os.path.join(os.environ['LOCALAPPDATA'], 'Programs', 'Maven', 'bin'),
                os.path.join(os.environ['LOCALAPPDATA'], 'Programs', 'ComposerSetup', 'bin')
            ]
            
            # Add new paths to PATH
            for path in new_paths:
                if os.path.exists(path):
                    if path not in current_path:
                        os.environ['PATH'] = f"{path};{current_path}"
                        
        except Exception as e:
            print(f"Warning: Failed to update PATH: {e}")
            
    def _try_direct_execution(self, command: str, base_command: str, args: list) -> Tuple[bool, str]:
        """Try direct execution of the command"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return True, result.stdout
            return False, result.stderr
        except Exception as e:
            return False, str(e)
            
    def _try_windows_command(self, command: str, base_command: str, args: list) -> Tuple[bool, str]:
        """Try executing as a Windows command"""
        try:
            result = subprocess.run(['where', base_command], capture_output=True, text=True)
            if result.returncode == 0:
                return self._try_direct_execution(command, base_command, args)
            return False, ""
        except Exception:
            return False, ""
            
    def _try_powershell_command(self, command: str, base_command: str, args: list) -> Tuple[bool, str]:
        """Try executing as a PowerShell command"""
        try:
            result = subprocess.run(['powershell', '-Command', f'Get-Command {base_command}'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return self._try_direct_execution(f"powershell -Command {command}", base_command, args)
            return False, ""
        except Exception:
            return False, ""
            
    def _try_package_manager(self, command: str, base_command: str, args: list) -> Tuple[bool, str]:
        """Try executing through a package manager"""
        package_manager = self.system_monitor.get_package_manager(base_command)
        if package_manager:
            try:
                if package_manager == 'winget':
                    result = subprocess.run(['winget', 'list', base_command], 
                                          capture_output=True, text=True)
                    if result.returncode == 0 and base_command in result.stdout:
                        return self._try_direct_execution(command, base_command, args)
                elif package_manager == 'pip':
                    result = subprocess.run(['pip', 'show', base_command], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        return self._try_direct_execution(command, base_command, args)
                elif package_manager == 'npm':
                    result = subprocess.run(['npm', 'list', '-g', base_command], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        return self._try_direct_execution(command, base_command, args)
            except Exception:
                pass
        return False, ""
        
    def _try_environment_command(self, command: str, base_command: str, args: list) -> Tuple[bool, str]:
        """Try executing in different environments"""
        # Check Python virtual environments
        if base_command.endswith('.py'):
            try:
                result = subprocess.run(['python', command], capture_output=True, text=True)
                if result.returncode == 0:
                    return True, result.stdout
            except Exception:
                pass
                
        # Check Node.js environment
        if base_command.endswith('.js'):
            try:
                result = subprocess.run(['node', command], capture_output=True, text=True)
                if result.returncode == 0:
                    return True, result.stdout
            except Exception:
                pass
                
        return False, ""
        
    def _update_history(self, command: str, success: bool):
        """Update command execution history"""
        if command not in self.execution_history:
            self.execution_history[command] = {
                'success_count': 0,
                'error_count': 0,
                'last_success': None,
                'last_error': None
            }
            
        history = self.execution_history[command]
        if success:
            history['success_count'] += 1
            history['last_success'] = time.time()
        else:
            history['error_count'] += 1
            history['last_error'] = time.time()
            
    def get_command_history(self, command: str) -> Optional[Dict]:
        """Get execution history for a command"""
        return self.execution_history.get(command)
        
    def clear_history(self):
        """Clear command execution history"""
        self.execution_history.clear() 