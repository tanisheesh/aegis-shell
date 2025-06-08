import os
import sys
import json
import logging
import subprocess
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from colorama import Fore, Style, init

class PlatformManager:
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir) if config_dir else Path.home() / '.aegis' / 'platform'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._setup_logging()
        self.platform_info = self._detect_platform_info()
        init()  # Initialize colorama
        
    def _setup_logging(self):
        """Setup logging configuration"""
        log_dir = self.config_dir / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / 'platform.log'
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
    def _detect_platform_info(self) -> Dict[str, Any]:
        """Detect platform information"""
        try:
            info_file = self.config_dir / 'platform_info.json'
            
            if not info_file.exists():
                # Detect platform info
                info = {
                    'os': self._detect_os(),
                    'package_managers': self._detect_package_managers(),
                    'system_paths': self._get_system_paths(),
                    'wsl': self._detect_wsl()
                }
                
                # Save platform info
                with open(info_file, 'w') as f:
                    json.dump(info, f, indent=4)
                    
                return info
                
            # Load existing platform info
            with open(info_file) as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error detecting platform info: {e}")
            return {}
            
    def _detect_os(self) -> Dict[str, str]:
        """Detect operating system information"""
        try:
            return {
                'platform': sys.platform,
                'system': os.name,
                'release': os.uname().release if hasattr(os, 'uname') else '',
                'version': os.uname().version if hasattr(os, 'uname') else '',
                'machine': os.uname().machine if hasattr(os, 'uname') else ''
            }
        except Exception as e:
            logging.error(f"Error detecting OS: {e}")
            return {}
            
    def _detect_package_managers(self) -> Dict[str, Dict[str, str]]:
        """Detect installed package managers"""
        try:
            managers = {}
            
            # Check pip
            try:
                result = subprocess.run(
                    ['pip', '--version'],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    managers['pip'] = {
                        'enabled': True,
                        'path': result.stdout.split()[1],
                        'version': result.stdout.split()[1]
                    }
            except Exception:
                pass
                
            # Check apt
            try:
                result = subprocess.run(
                    ['apt', '--version'],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    managers['apt'] = {
                        'enabled': True,
                        'path': result.stdout.split()[1],
                        'version': result.stdout.split()[1]
                    }
            except Exception:
                pass
                
            # Check yum
            try:
                result = subprocess.run(
                    ['yum', '--version'],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    managers['yum'] = {
                        'enabled': True,
                        'path': result.stdout.split()[1],
                        'version': result.stdout.split()[1]
                    }
            except Exception:
                pass
                
            # Check brew
            try:
                result = subprocess.run(
                    ['brew', '--version'],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    managers['brew'] = {
                        'enabled': True,
                        'path': result.stdout.split()[1],
                        'version': result.stdout.split()[1]
                    }
            except Exception:
                pass
                
            # Check chocolatey
            try:
                result = subprocess.run(
                    ['choco', '--version'],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    managers['chocolatey'] = {
                        'enabled': True,
                        'path': result.stdout.split()[1],
                        'version': result.stdout.split()[1]
                    }
            except Exception:
                pass
                
            return managers
        except Exception as e:
            logging.error(f"Error detecting package managers: {e}")
            return {}
            
    def _get_system_paths(self) -> Dict[str, str]:
        """Get system paths"""
        try:
            paths = {}
            
            # Get home directory
            paths['home'] = str(Path.home())
            
            # Get current directory
            paths['current'] = str(Path.cwd())
            
            # Get temp directory
            paths['temp'] = str(Path(os.environ.get('TEMP', '/tmp')))
            
            # Get config directory
            paths['config'] = str(self.config_dir)
            
            # Get executable directory
            paths['executable'] = str(Path(sys.executable).parent)
            
            # Get Python path
            paths['python'] = str(Path(sys.executable))
            
            # Get PATH environment variable
            paths['path'] = os.environ.get('PATH', '')
            
            return paths
        except Exception as e:
            logging.error(f"Error getting system paths: {e}")
            return {}
            
    def _detect_wsl(self) -> Dict[str, Any]:
        """Detect Windows Subsystem for Linux"""
        try:
            wsl_info = {
                'enabled': False,
                'version': '',
                'default_distro': ''
            }
            
            if sys.platform == 'win32':
                # Check if WSL is enabled
                try:
                    result = subprocess.run(
                        ['wsl', '--status'],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        wsl_info['enabled'] = True
                        
                        # Get WSL version
                        version_result = subprocess.run(
                            ['wsl', '--version'],
                            capture_output=True,
                            text=True
                        )
                        if version_result.returncode == 0:
                            wsl_info['version'] = version_result.stdout.split()[1]
                            
                        # Get default distribution
                        distro_result = subprocess.run(
                            ['wsl', '--list', '--verbose'],
                            capture_output=True,
                            text=True
                        )
                        if distro_result.returncode == 0:
                            for line in distro_result.stdout.splitlines():
                                if '*' in line:
                                    wsl_info['default_distro'] = line.split()[1]
                                    break
                except Exception:
                    pass
                    
            return wsl_info
        except Exception as e:
            logging.error(f"Error detecting WSL: {e}")
            return {'enabled': False}
            
    def get_platform_info(self) -> Dict[str, Any]:
        """Get platform information"""
        return self.platform_info
        
    def get_os_info(self) -> Dict[str, str]:
        """Get operating system information"""
        return self.platform_info.get('os', {})
        
    def get_package_managers(self) -> Dict[str, Dict[str, str]]:
        """Get installed package managers"""
        return self.platform_info.get('package_managers', {})
        
    def get_system_paths(self) -> Dict[str, str]:
        """Get system paths"""
        return self.platform_info.get('system_paths', {})
        
    def get_wsl_info(self) -> Dict[str, Any]:
        """Get WSL information"""
        return self.platform_info.get('wsl', {})
        
    def print_platform_info(self):
        """Print platform information"""
        try:
            print(f"\n{Fore.CYAN}Platform Information{Style.RESET_ALL}")
            
            # Print OS info
            os_info = self.get_os_info()
            print(f"\n{Fore.YELLOW}Operating System:{Style.RESET_ALL}")
            print(f"Platform: {os_info.get('platform', '')}")
            print(f"System: {os_info.get('system', '')}")
            print(f"Release: {os_info.get('release', '')}")
            print(f"Version: {os_info.get('version', '')}")
            print(f"Machine: {os_info.get('machine', '')}")
            
            # Print package managers
            managers = self.get_package_managers()
            print(f"\n{Fore.YELLOW}Package Managers:{Style.RESET_ALL}")
            for name, info in managers.items():
                print(f"\n{name}:")
                print(f"  Enabled: {info.get('enabled', False)}")
                print(f"  Path: {info.get('path', '')}")
                print(f"  Version: {info.get('version', '')}")
                
            # Print system paths
            paths = self.get_system_paths()
            print(f"\n{Fore.YELLOW}System Paths:{Style.RESET_ALL}")
            for name, path in paths.items():
                print(f"{name}: {path}")
                
            # Print WSL info
            wsl_info = self.get_wsl_info()
            print(f"\n{Fore.YELLOW}Windows Subsystem for Linux:{Style.RESET_ALL}")
            print(f"Enabled: {wsl_info.get('enabled', False)}")
            if wsl_info.get('enabled'):
                print(f"Version: {wsl_info.get('version', '')}")
                print(f"Default Distribution: {wsl_info.get('default_distro', '')}")
        except Exception as e:
            logging.error(f"Error printing platform info: {e}")
            
    def get_config_directory(self) -> Path:
        """Get configuration directory"""
        return self.config_dir 