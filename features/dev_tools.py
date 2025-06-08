import os
import sys
import json
import logging
import subprocess
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from colorama import Fore, Style, init

class DevToolsManager:
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir) if config_dir else Path.home() / '.aegis' / 'dev_tools'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._setup_logging()
        self.tools_config = self._load_tools_config()
        init()  # Initialize colorama
        
    def _setup_logging(self):
        """Setup logging configuration"""
        log_dir = self.config_dir / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / 'dev_tools.log'
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
    def _load_tools_config(self) -> Dict[str, Any]:
        """Load tools configuration"""
        try:
            config_file = self.config_dir / 'tools_config.json'
            
            if not config_file.exists():
                # Create default configuration
                config = {
                    'git': {
                        'enabled': True,
                        'path': None,
                        'version': None
                    },
                    'ides': {
                        'vscode': {
                            'enabled': True,
                            'path': None,
                            'version': None
                        },
                        'pycharm': {
                            'enabled': True,
                            'path': None,
                            'version': None
                        },
                        'sublime': {
                            'enabled': True,
                            'path': None,
                            'version': None
                        }
                    },
                    'build_tools': {
                        'cmake': {
                            'enabled': True,
                            'path': None,
                            'version': None
                        },
                        'make': {
                            'enabled': True,
                            'path': None,
                            'version': None
                        },
                        'ninja': {
                            'enabled': True,
                            'path': None,
                            'version': None
                        },
                        'gradle': {
                            'enabled': True,
                            'path': None,
                            'version': None
                        }
                    },
                    'frameworks': {
                        'node': {
                            'enabled': True,
                            'path': None,
                            'version': None
                        },
                        'python': {
                            'enabled': True,
                            'path': None,
                            'version': None
                        },
                        'java': {
                            'enabled': True,
                            'path': None,
                            'version': None
                        },
                        'dotnet': {
                            'enabled': True,
                            'path': None,
                            'version': None
                        }
                    }
                }
                
                # Save default configuration
                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=4)
                    
                return config
                
            # Load existing configuration
            with open(config_file) as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading tools config: {e}")
            return {}
            
    def _detect_git(self) -> Dict[str, Any]:
        """Detect Git installation"""
        try:
            git_info = {
                'enabled': False,
                'path': None,
                'version': None
            }
            
            # Try to get Git version
            try:
                git_version = subprocess.check_output(['git', '--version']).decode().strip()
                git_info['enabled'] = True
                git_info['version'] = git_version
                
                # Get Git path
                if sys.platform == 'win32':
                    git_path = subprocess.check_output(['where', 'git']).decode().strip()
                else:
                    git_path = subprocess.check_output(['which', 'git']).decode().strip()
                    
                git_info['path'] = git_path
            except Exception:
                pass
                
            return git_info
        except Exception as e:
            logging.error(f"Error detecting Git: {e}")
            return {}
            
    def _detect_ides(self) -> Dict[str, Any]:
        """Detect IDE installations"""
        try:
            ides = {
                'vscode': {
                    'enabled': False,
                    'path': None,
                    'version': None
                },
                'pycharm': {
                    'enabled': False,
                    'path': None,
                    'version': None
                },
                'sublime': {
                    'enabled': False,
                    'path': None,
                    'version': None
                }
            }
            
            # Detect VS Code
            try:
                if sys.platform == 'win32':
                    vscode_path = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Microsoft VS Code', 'Code.exe')
                elif sys.platform == 'darwin':
                    vscode_path = '/Applications/Visual Studio Code.app/Contents/MacOS/Electron'
                else:
                    vscode_path = '/usr/bin/code'
                    
                if os.path.exists(vscode_path):
                    ides['vscode']['enabled'] = True
                    ides['vscode']['path'] = vscode_path
                    
                    # Get version
                    version = subprocess.check_output([vscode_path, '--version']).decode().strip()
                    ides['vscode']['version'] = version
            except Exception:
                pass
                
            # Detect PyCharm
            try:
                if sys.platform == 'win32':
                    pycharm_path = os.path.join(os.environ.get('PROGRAMFILES', ''), 'JetBrains', 'PyCharm', 'bin', 'pycharm64.exe')
                elif sys.platform == 'darwin':
                    pycharm_path = '/Applications/PyCharm.app/Contents/MacOS/pycharm'
                else:
                    pycharm_path = '/usr/bin/pycharm'
                    
                if os.path.exists(pycharm_path):
                    ides['pycharm']['enabled'] = True
                    ides['pycharm']['path'] = pycharm_path
                    
                    # Get version
                    version = subprocess.check_output([pycharm_path, '--version']).decode().strip()
                    ides['pycharm']['version'] = version
            except Exception:
                pass
                
            # Detect Sublime Text
            try:
                if sys.platform == 'win32':
                    sublime_path = os.path.join(os.environ.get('PROGRAMFILES', ''), 'Sublime Text', 'sublime_text.exe')
                elif sys.platform == 'darwin':
                    sublime_path = '/Applications/Sublime Text.app/Contents/MacOS/Sublime Text'
                else:
                    sublime_path = '/usr/bin/subl'
                    
                if os.path.exists(sublime_path):
                    ides['sublime']['enabled'] = True
                    ides['sublime']['path'] = sublime_path
                    
                    # Get version
                    version = subprocess.check_output([sublime_path, '--version']).decode().strip()
                    ides['sublime']['version'] = version
            except Exception:
                pass
                
            return ides
        except Exception as e:
            logging.error(f"Error detecting IDEs: {e}")
            return {}
            
    def _detect_build_tools(self) -> Dict[str, Any]:
        """Detect build tool installations"""
        try:
            build_tools = {
                'cmake': {
                    'enabled': False,
                    'path': None,
                    'version': None
                },
                'make': {
                    'enabled': False,
                    'path': None,
                    'version': None
                },
                'ninja': {
                    'enabled': False,
                    'path': None,
                    'version': None
                },
                'gradle': {
                    'enabled': False,
                    'path': None,
                    'version': None
                }
            }
            
            # Detect CMake
            try:
                cmake_version = subprocess.check_output(['cmake', '--version']).decode().strip()
                build_tools['cmake']['enabled'] = True
                build_tools['cmake']['version'] = cmake_version
                
                # Get path
                if sys.platform == 'win32':
                    cmake_path = subprocess.check_output(['where', 'cmake']).decode().strip()
                else:
                    cmake_path = subprocess.check_output(['which', 'cmake']).decode().strip()
                    
                build_tools['cmake']['path'] = cmake_path
            except Exception:
                pass
                
            # Detect Make
            try:
                make_version = subprocess.check_output(['make', '--version']).decode().strip()
                build_tools['make']['enabled'] = True
                build_tools['make']['version'] = make_version
                
                # Get path
                if sys.platform == 'win32':
                    make_path = subprocess.check_output(['where', 'make']).decode().strip()
                else:
                    make_path = subprocess.check_output(['which', 'make']).decode().strip()
                    
                build_tools['make']['path'] = make_path
            except Exception:
                pass
                
            # Detect Ninja
            try:
                ninja_version = subprocess.check_output(['ninja', '--version']).decode().strip()
                build_tools['ninja']['enabled'] = True
                build_tools['ninja']['version'] = ninja_version
                
                # Get path
                if sys.platform == 'win32':
                    ninja_path = subprocess.check_output(['where', 'ninja']).decode().strip()
                else:
                    ninja_path = subprocess.check_output(['which', 'ninja']).decode().strip()
                    
                build_tools['ninja']['path'] = ninja_path
            except Exception:
                pass
                
            # Detect Gradle
            try:
                gradle_version = subprocess.check_output(['gradle', '--version']).decode().strip()
                build_tools['gradle']['enabled'] = True
                build_tools['gradle']['version'] = gradle_version
                
                # Get path
                if sys.platform == 'win32':
                    gradle_path = subprocess.check_output(['where', 'gradle']).decode().strip()
                else:
                    gradle_path = subprocess.check_output(['which', 'gradle']).decode().strip()
                    
                build_tools['gradle']['path'] = gradle_path
            except Exception:
                pass
                
            return build_tools
        except Exception as e:
            logging.error(f"Error detecting build tools: {e}")
            return {}
            
    def _detect_frameworks(self) -> Dict[str, Any]:
        """Detect framework installations"""
        try:
            frameworks = {
                'node': {
                    'enabled': False,
                    'path': None,
                    'version': None
                },
                'python': {
                    'enabled': False,
                    'path': None,
                    'version': None
                },
                'java': {
                    'enabled': False,
                    'path': None,
                    'version': None
                },
                'dotnet': {
                    'enabled': False,
                    'path': None,
                    'version': None
                }
            }
            
            # Detect Node.js
            try:
                node_version = subprocess.check_output(['node', '--version']).decode().strip()
                frameworks['node']['enabled'] = True
                frameworks['node']['version'] = node_version
                
                # Get path
                if sys.platform == 'win32':
                    node_path = subprocess.check_output(['where', 'node']).decode().strip()
                else:
                    node_path = subprocess.check_output(['which', 'node']).decode().strip()
                    
                frameworks['node']['path'] = node_path
            except Exception:
                pass
                
            # Detect Python
            try:
                python_version = sys.version
                frameworks['python']['enabled'] = True
                frameworks['python']['version'] = python_version
                frameworks['python']['path'] = sys.executable
            except Exception:
                pass
                
            # Detect Java
            try:
                java_version = subprocess.check_output(['java', '-version'], stderr=subprocess.STDOUT).decode().strip()
                frameworks['java']['enabled'] = True
                frameworks['java']['version'] = java_version
                
                # Get path
                if sys.platform == 'win32':
                    java_path = subprocess.check_output(['where', 'java']).decode().strip()
                else:
                    java_path = subprocess.check_output(['which', 'java']).decode().strip()
                    
                frameworks['java']['path'] = java_path
            except Exception:
                pass
                
            # Detect .NET
            try:
                dotnet_version = subprocess.check_output(['dotnet', '--version']).decode().strip()
                frameworks['dotnet']['enabled'] = True
                frameworks['dotnet']['version'] = dotnet_version
                
                # Get path
                if sys.platform == 'win32':
                    dotnet_path = subprocess.check_output(['where', 'dotnet']).decode().strip()
                else:
                    dotnet_path = subprocess.check_output(['which', 'dotnet']).decode().strip()
                    
                frameworks['dotnet']['path'] = dotnet_path
            except Exception:
                pass
                
            return frameworks
        except Exception as e:
            logging.error(f"Error detecting frameworks: {e}")
            return {}
            
    def detect_tools(self):
        """Detect development tools"""
        try:
            # Update tools configuration
            self.tools_config['git'] = self._detect_git()
            self.tools_config['ides'] = self._detect_ides()
            self.tools_config['build_tools'] = self._detect_build_tools()
            self.tools_config['frameworks'] = self._detect_frameworks()
            
            # Save updated configuration
            config_file = self.config_dir / 'tools_config.json'
            with open(config_file, 'w') as f:
                json.dump(self.tools_config, f, indent=4)
                
            logging.info("Development tools detection completed")
        except Exception as e:
            logging.error(f"Error detecting tools: {e}")
            
    def get_tools_config(self) -> Dict[str, Any]:
        """Get tools configuration"""
        return self.tools_config
        
    def get_git_info(self) -> Dict[str, Any]:
        """Get Git information"""
        return self.tools_config.get('git', {})
        
    def get_ide_info(self, ide: str) -> Dict[str, Any]:
        """Get IDE information"""
        return self.tools_config.get('ides', {}).get(ide, {})
        
    def get_build_tool_info(self, tool: str) -> Dict[str, Any]:
        """Get build tool information"""
        return self.tools_config.get('build_tools', {}).get(tool, {})
        
    def get_framework_info(self, framework: str) -> Dict[str, Any]:
        """Get framework information"""
        return self.tools_config.get('frameworks', {}).get(framework, {})
        
    def print_tools_info(self):
        """Print tools information"""
        try:
            print(f"\n{Fore.CYAN}Development Tools Information{Style.RESET_ALL}")
            
            # Print Git info
            print(f"\n{Fore.YELLOW}Git:{Style.RESET_ALL}")
            git_info = self.tools_config.get('git', {})
            for key, value in git_info.items():
                print(f"{key}: {value}")
                
            # Print IDE info
            print(f"\n{Fore.YELLOW}IDEs:{Style.RESET_ALL}")
            ides = self.tools_config.get('ides', {})
            for name, info in ides.items():
                print(f"\n{name}:")
                for key, value in info.items():
                    print(f"  {key}: {value}")
                    
            # Print build tools info
            print(f"\n{Fore.YELLOW}Build Tools:{Style.RESET_ALL}")
            build_tools = self.tools_config.get('build_tools', {})
            for name, info in build_tools.items():
                print(f"\n{name}:")
                for key, value in info.items():
                    print(f"  {key}: {value}")
                    
            # Print frameworks info
            print(f"\n{Fore.YELLOW}Frameworks:{Style.RESET_ALL}")
            frameworks = self.tools_config.get('frameworks', {})
            for name, info in frameworks.items():
                print(f"\n{name}:")
                for key, value in info.items():
                    print(f"  {key}: {value}")
                    
            print()
        except Exception as e:
            logging.error(f"Error printing tools info: {e}")
            
    def get_config_directory(self) -> Path:
        """Get configuration directory"""
        return self.config_dir 