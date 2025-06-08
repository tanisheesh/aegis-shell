import os
import sys
import subprocess
import winreg
import psutil
import time
from pathlib import Path
from typing import Dict, List, Set, Optional
import threading

class SystemMonitor:
    def __init__(self):
        self.available_commands: Set[str] = set()
        self.package_managers: Dict[str, bool] = {}
        self.programming_languages: Dict[str, str] = {}
        self.system_services: Dict[str, bool] = {}
        self.command_cache: Dict[str, Dict] = {}
        self.is_monitoring = False
        self.last_scan_time = 0
        self.watched_directories = set()
        
    def start_monitoring(self):
        """Start monitoring system changes"""
        self.is_monitoring = True
        self._scan_system()
        self._start_periodic_scan()
        
    def stop_monitoring(self):
        """Stop monitoring system changes"""
        self.is_monitoring = False
        
    def _scan_system(self):
        """Perform initial system scan"""
        self._scan_path()
        self._scan_program_files()
        self._detect_package_managers()
        self._detect_programming_languages()
        self._scan_system_services()
        self.last_scan_time = time.time()
        
    def _scan_path(self):
        """Scan system PATH for available commands"""
        path_dirs = os.environ['PATH'].split(os.pathsep)
        for directory in path_dirs:
            if os.path.exists(directory) and os.path.isdir(directory):
                try:
                    self.watched_directories.add(directory)
                    for file in os.listdir(directory):
                        if file.endswith('.exe') or file.endswith('.bat') or file.endswith('.cmd'):
                            self.available_commands.add(file.split('.')[0])
                except (PermissionError, OSError) as e:
                    print(f"Warning: Could not scan directory {directory}: {e}")
                    
    def _scan_program_files(self):
        """Scan Program Files directories for installed applications"""
        program_files_dirs = [
            os.environ.get('ProgramFiles', 'C:\\Program Files'),
            os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)')
        ]
        
        for directory in program_files_dirs:
            if os.path.exists(directory) and os.path.isdir(directory):
                try:
                    self.watched_directories.add(directory)
                    for root, _, files in os.walk(directory):
                        for file in files:
                            if file.endswith('.exe'):
                                self.available_commands.add(file.split('.')[0])
                except (PermissionError, OSError) as e:
                    print(f"Warning: Could not scan directory {directory}: {e}")
                    
    def _detect_package_managers(self):
        """Detect available package managers"""
        package_managers = {
            'winget': 'winget --version',
            'pip': 'pip --version',
            'npm': 'npm --version',
            'choco': 'choco --version',
            'scoop': 'scoop --version',
            'nuget': 'nuget help'
        }
        
        for manager, check_cmd in package_managers.items():
            try:
                subprocess.run(check_cmd.split(), capture_output=True, check=True)
                self.package_managers[manager] = True
            except (subprocess.SubprocessError, FileNotFoundError):
                self.package_managers[manager] = False
                
    def _detect_programming_languages(self):
        """Detect installed programming languages"""
        languages = {
            'python': 'python --version',
            'node': 'node --version',
            'java': 'java --version',
            'ruby': 'ruby --version',
            'go': 'go version'
        }
        
        for lang, check_cmd in languages.items():
            try:
                result = subprocess.run(check_cmd.split(), capture_output=True, text=True)
                if result.returncode == 0:
                    self.programming_languages[lang] = result.stdout.strip()
            except (subprocess.SubprocessError, FileNotFoundError):
                continue
                
    def _scan_system_services(self):
        """Scan system services"""
        for service in psutil.win_service_iter():
            try:
                # Get basic service info first
                name = service.name()
                status = service.status()
                self.system_services[name] = status == 'running'
            except (psutil.NoSuchProcess, psutil.AccessDenied, FileNotFoundError, Exception) as e:
                # Skip services that can't be queried
                continue
                
    def _check_directory_changes(self):
        """Check if any watched directories have changed"""
        for directory in self.watched_directories:
            try:
                if os.path.exists(directory) and os.path.isdir(directory):
                    current_time = os.path.getmtime(directory)
                    if current_time > self.last_scan_time:
                        return True
            except (PermissionError, OSError):
                continue
        return False
        
    def _start_periodic_scan(self):
        """Start periodic system scanning"""
        def periodic_scan():
            while self.is_monitoring:
                try:
                    # Check for directory changes
                    if self._check_directory_changes():
                        self._scan_system()
                    else:
                        # Only update services and health metrics
                        self._scan_system_services()
                    time.sleep(30)  # Check every 30 seconds
                except Exception as e:
                    print(f"Warning: Error during periodic scan: {e}")
                    time.sleep(30)  # Wait before retrying
                    
        scan_thread = threading.Thread(target=periodic_scan, daemon=True)
        scan_thread.start()
        
    def is_command_available(self, command: str) -> bool:
        """Check if a command is available"""
        return command in self.available_commands
        
    def get_package_manager(self, command: str) -> Optional[str]:
        """Determine the appropriate package manager for a command"""
        # Add logic to determine package manager based on command context
        if command.startswith('pip'):
            return 'pip'
        elif command.startswith('npm'):
            return 'npm'
        elif command.startswith('winget'):
            return 'winget'
        return None
        
    def get_command_info(self, command: str) -> Dict:
        """Get detailed information about a command"""
        if command in self.command_cache:
            return self.command_cache[command]
            
        info = {
            'available': self.is_command_available(command),
            'package_manager': self.get_package_manager(command),
            'last_used': None,
            'success_rate': 0,
            'error_count': 0
        }
        
        self.command_cache[command] = info
        return info
        
    def update_command_stats(self, command: str, success: bool):
        """Update command usage statistics"""
        if command in self.command_cache:
            info = self.command_cache[command]
            info['last_used'] = time.time()
            if success:
                info['success_rate'] = (info['success_rate'] * info['error_count'] + 1) / (info['error_count'] + 1)
            else:
                info['error_count'] += 1
                
    def get_system_health(self) -> Dict:
        """Get system health metrics"""
        try:
            return {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'network_connections': len(psutil.net_connections()),
                'running_processes': len(psutil.pids())
            }
        except Exception as e:
            # Return basic metrics if detailed ones fail
            return {
                'cpu_percent': 0,
                'memory_percent': 0,
                'disk_usage': 0,
                'network_connections': 0,
                'running_processes': 0,
                'error': str(e)
            } 