import subprocess
import os
import platform
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import time
import psutil
from colorama import Fore, Style
from .command_detector import CommandDetector
from .package_manager import PackageManager
from .env_detector import EnvironmentDetector

class SmartCommandExecutor:
    def __init__(self):
        self.command_detector = CommandDetector()
        self.package_manager = PackageManager()
        self.env_detector = EnvironmentDetector()
        self.command_history: List[Dict] = []
        self.success_count = 0
        self.total_count = 0
        self._load_history()
        
    def _load_history(self):
        """Load command history from file"""
        history_file = Path.home() / '.aegis' / 'command_execution_history.json'
        if history_file.exists():
            with open(history_file) as f:
                self.command_history = json.load(f)
                
    def _save_history(self):
        """Save command history to file"""
        history_file = Path.home() / '.aegis' / 'command_execution_history.json'
        history_file.parent.mkdir(parents=True, exist_ok=True)
        with open(history_file, 'w') as f:
            json.dump(self.command_history, f)
            
    def execute_command(self, command: str) -> Tuple[bool, str]:
        """Execute a command with smart features"""
        if not command.strip():
            return True, ""
            
        # Add to history
        self.command_history.append({
            'command': command,
            'timestamp': time.time(),
            'success': False,
            'output': '',
            'error': ''
        })
        self.total_count += 1
        
        # Check for command suggestions
        suggestions = self.command_detector.get_suggestions(command)
        if suggestions and command not in suggestions:
            print(Fore.YELLOW + f"\nDid you mean one of these commands?" + Style.RESET_ALL)
            for i, suggestion in enumerate(suggestions[:3], 1):
                print(f"{i}. {suggestion}")
            response = input(Fore.YELLOW + "\nUse suggestion? (y/n): " + Style.RESET_ALL)
            if response.lower() == 'y':
                choice = input(Fore.YELLOW + "Enter number (1-3): " + Style.RESET_ALL)
                try:
                    command = suggestions[int(choice) - 1]
                except (ValueError, IndexError):
                    pass
                    
        # Expand aliases
        command = self.command_detector.expand_alias(command)
        
        # Apply templates
        if command in self.command_detector.command_templates:
            params = {}
            template = self.command_detector.command_templates[command]
            for param in re.findall(r'\{(\w+)\}', template):
                if param not in params:
                    value = input(Fore.YELLOW + f"Enter value for {param}: " + Style.RESET_ALL)
                    params[param] = value
            command = self.command_detector.apply_template(command, **params)
            
        # Detect environment
        env = self.env_detector.detect_environment()
        
        # Execute command
        try:
            start_time = time.time()
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Monitor process
            while process.poll() is None:
                # Check resource usage
                try:
                    process_info = psutil.Process(process.pid)
                    cpu_percent = process_info.cpu_percent()
                    memory_percent = process_info.memory_percent()
                    
                    if cpu_percent > 80 or memory_percent > 80:
                        print(Fore.YELLOW + f"\nWarning: High resource usage detected" + Style.RESET_ALL)
                        print(f"CPU: {cpu_percent}%")
                        print(f"Memory: {memory_percent}%")
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                    
                time.sleep(0.1)
                
            # Get output
            stdout, stderr = process.communicate()
            end_time = time.time()
            
            # Update history
            self.command_history[-1].update({
                'success': process.returncode == 0,
                'output': stdout,
                'error': stderr,
                'duration': end_time - start_time
            })
            
            if process.returncode == 0:
                self.success_count += 1
                self._save_history()
                return True, stdout
            else:
                # Check if command not found
                if "not recognized" in stderr or "not found" in stderr:
                    # Try to install the command
                    package_name = command.split()[0]
                    if self.package_manager.install_package(package_name):
                        # Retry command
                        return self.execute_command(command)
                        
                self._save_history()
                return False, stderr
                
        except Exception as e:
            self.command_history[-1].update({
                'error': str(e)
            })
            self._save_history()
            return False, str(e)
            
    def get_success_rate(self) -> float:
        """Get command execution success rate"""
        if self.total_count == 0:
            return 0.0
        return (self.success_count / self.total_count) * 100
        
    def get_command_stats(self) -> Dict:
        """Get command execution statistics"""
        stats = {
            'total_commands': self.total_count,
            'successful_commands': self.success_count,
            'success_rate': self.get_success_rate(),
            'average_duration': 0.0,
            'most_used_commands': [],
            'most_failed_commands': []
        }
        
        if self.command_history:
            # Calculate average duration
            durations = [cmd['duration'] for cmd in self.command_history if 'duration' in cmd]
            if durations:
                stats['average_duration'] = sum(durations) / len(durations)
                
            # Get most used commands
            command_counts = {}
            for cmd in self.command_history:
                command = cmd['command']
                command_counts[command] = command_counts.get(command, 0) + 1
            stats['most_used_commands'] = sorted(
                command_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            # Get most failed commands
            failed_commands = {}
            for cmd in self.command_history:
                if not cmd['success']:
                    command = cmd['command']
                    failed_commands[command] = failed_commands.get(command, 0) + 1
            stats['most_failed_commands'] = sorted(
                failed_commands.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
        return stats
        
    def print_stats(self):
        """Print command execution statistics"""
        stats = self.get_command_stats()
        
        print(Fore.CYAN + "\nCommand Execution Statistics:" + Style.RESET_ALL)
        print(f"\nTotal Commands: {stats['total_commands']}")
        print(f"Successful Commands: {stats['successful_commands']}")
        print(f"Success Rate: {stats['success_rate']:.2f}%")
        print(f"Average Duration: {stats['average_duration']:.2f} seconds")
        
        if stats['most_used_commands']:
            print(Fore.GREEN + "\nMost Used Commands:" + Style.RESET_ALL)
            for command, count in stats['most_used_commands']:
                print(f"  - {command}: {count} times")
                
        if stats['most_failed_commands']:
            print(Fore.RED + "\nMost Failed Commands:" + Style.RESET_ALL)
            for command, count in stats['most_failed_commands']:
                print(f"  - {command}: {count} times") 