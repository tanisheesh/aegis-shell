import os
import subprocess
from typing import Dict, List, Optional, Set
from pathlib import Path
import json
import re
from colorama import Fore, Style

class EnvironmentDetector:
    def __init__(self):
        self.ide_patterns = {
            'vscode': ['.vscode', 'settings.json'],
            'pycharm': ['.idea', 'workspace.xml'],
            'eclipse': ['.project', '.classpath'],
            'intellij': ['.idea', 'workspace.xml'],
            'vim': ['.vimrc', '.vim'],
            'sublime': ['.sublime-project', '.sublime-workspace']
        }
        
        self.framework_patterns = {
            'django': ['manage.py', 'settings.py'],
            'flask': ['app.py', 'flask_app.py'],
            'react': ['package.json', 'src/App.js'],
            'angular': ['angular.json', 'src/app'],
            'vue': ['package.json', 'src/App.vue'],
            'spring': ['pom.xml', 'application.properties'],
            'laravel': ['artisan', 'composer.json'],
            'rails': ['Gemfile', 'config/routes.rb']
        }
        
        self.build_tools = {
            'maven': ['pom.xml'],
            'gradle': ['build.gradle', 'settings.gradle'],
            'npm': ['package.json'],
            'yarn': ['yarn.lock'],
            'pip': ['requirements.txt'],
            'composer': ['composer.json'],
            'cargo': ['Cargo.toml'],
            'go': ['go.mod']
        }
        
        self.database_patterns = {
            'postgresql': ['postgresql.conf', 'pg_hba.conf'],
            'mysql': ['my.cnf', 'my.ini'],
            'mongodb': ['mongod.conf'],
            'sqlite': ['.db', '.sqlite'],
            'redis': ['redis.conf']
        }
        
        self.detected_env: Dict[str, Set[str]] = {
            'ides': set(),
            'frameworks': set(),
            'build_tools': set(),
            'databases': set(),
            'languages': set()
        }
        
    def detect_environment(self, path: str = '.') -> Dict[str, Set[str]]:
        """Detect development environment in the given path"""
        path = Path(path)
        
        # Reset detected environment
        for key in self.detected_env:
            self.detected_env[key] = set()
            
        # Detect IDEs
        self._detect_ides(path)
        
        # Detect frameworks
        self._detect_frameworks(path)
        
        # Detect build tools
        self._detect_build_tools(path)
        
        # Detect databases
        self._detect_databases(path)
        
        # Detect programming languages
        self._detect_languages(path)
        
        return self.detected_env
        
    def _detect_ides(self, path: Path):
        """Detect IDEs by looking for specific files and directories"""
        for ide, patterns in self.ide_patterns.items():
            for pattern in patterns:
                if list(path.glob(f'**/{pattern}')):
                    self.detected_env['ides'].add(ide)
                    break
                    
    def _detect_frameworks(self, path: Path):
        """Detect frameworks by looking for specific files"""
        for framework, patterns in self.framework_patterns.items():
            for pattern in patterns:
                if list(path.glob(f'**/{pattern}')):
                    self.detected_env['frameworks'].add(framework)
                    break
                    
    def _detect_build_tools(self, path: Path):
        """Detect build tools by looking for specific files"""
        for tool, patterns in self.build_tools.items():
            for pattern in patterns:
                if list(path.glob(f'**/{pattern}')):
                    self.detected_env['build_tools'].add(tool)
                    break
                    
    def _detect_databases(self, path: Path):
        """Detect databases by looking for specific files"""
        for db, patterns in self.database_patterns.items():
            for pattern in patterns:
                if list(path.glob(f'**/{pattern}')):
                    self.detected_env['databases'].add(db)
                    break
                    
    def _detect_languages(self, path: Path):
        """Detect programming languages by analyzing files"""
        language_patterns = {
            'python': ['.py'],
            'javascript': ['.js'],
            'typescript': ['.ts'],
            'java': ['.java'],
            'csharp': ['.cs'],
            'php': ['.php'],
            'ruby': ['.rb'],
            'go': ['.go'],
            'rust': ['.rs'],
            'c': ['.c'],
            'cpp': ['.cpp'],
            'swift': ['.swift'],
            'kotlin': ['.kt'],
            'scala': ['.scala']
        }
        
        for lang, extensions in language_patterns.items():
            for ext in extensions:
                if list(path.glob(f'**/*{ext}')):
                    self.detected_env['languages'].add(lang)
                    break
                    
    def get_ide_config(self, ide: str) -> Optional[Dict]:
        """Get IDE configuration if available"""
        if ide not in self.detected_env['ides']:
            return None
            
        config_path = None
        if ide == 'vscode':
            config_path = Path('.vscode/settings.json')
        elif ide == 'pycharm':
            config_path = Path('.idea/workspace.xml')
        elif ide == 'eclipse':
            config_path = Path('.project')
        elif ide == 'intellij':
            config_path = Path('.idea/workspace.xml')
        elif ide == 'vim':
            config_path = Path('.vimrc')
        elif ide == 'sublime':
            config_path = Path('.sublime-project')
            
        if config_path and config_path.exists():
            try:
                with open(config_path) as f:
                    return json.load(f)
            except:
                return None
                
        return None
        
    def get_framework_config(self, framework: str) -> Optional[Dict]:
        """Get framework configuration if available"""
        if framework not in self.detected_env['frameworks']:
            return None
            
        config_path = None
        if framework == 'django':
            config_path = Path('settings.py')
        elif framework == 'flask':
            config_path = Path('config.py')
        elif framework in ['react', 'angular', 'vue']:
            config_path = Path('package.json')
        elif framework == 'spring':
            config_path = Path('application.properties')
        elif framework == 'laravel':
            config_path = Path('.env')
        elif framework == 'rails':
            config_path = Path('config/database.yml')
            
        if config_path and config_path.exists():
            try:
                with open(config_path) as f:
                    return json.load(f)
            except:
                return None
                
        return None
        
    def get_build_tool_config(self, tool: str) -> Optional[Dict]:
        """Get build tool configuration if available"""
        if tool not in self.detected_env['build_tools']:
            return None
            
        config_path = None
        if tool == 'maven':
            config_path = Path('pom.xml')
        elif tool == 'gradle':
            config_path = Path('build.gradle')
        elif tool in ['npm', 'yarn']:
            config_path = Path('package.json')
        elif tool == 'pip':
            config_path = Path('requirements.txt')
        elif tool == 'composer':
            config_path = Path('composer.json')
        elif tool == 'cargo':
            config_path = Path('Cargo.toml')
        elif tool == 'go':
            config_path = Path('go.mod')
            
        if config_path and config_path.exists():
            try:
                with open(config_path) as f:
                    return json.load(f)
            except:
                return None
                
        return None
        
    def get_database_config(self, db: str) -> Optional[Dict]:
        """Get database configuration if available"""
        if db not in self.detected_env['databases']:
            return None
            
        config_path = None
        if db == 'postgresql':
            config_path = Path('postgresql.conf')
        elif db == 'mysql':
            config_path = Path('my.cnf')
        elif db == 'mongodb':
            config_path = Path('mongod.conf')
        elif db == 'redis':
            config_path = Path('redis.conf')
            
        if config_path and config_path.exists():
            try:
                with open(config_path) as f:
                    return json.load(f)
            except:
                return None
                
        return None
        
    def print_environment(self):
        """Print detected environment information"""
        print(Fore.CYAN + "\nDetected Development Environment:" + Style.RESET_ALL)
        
        if self.detected_env['ides']:
            print(Fore.GREEN + "\nIDEs:" + Style.RESET_ALL)
            for ide in sorted(self.detected_env['ides']):
                print(f"  - {ide}")
                
        if self.detected_env['frameworks']:
            print(Fore.GREEN + "\nFrameworks:" + Style.RESET_ALL)
            for framework in sorted(self.detected_env['frameworks']):
                print(f"  - {framework}")
                
        if self.detected_env['build_tools']:
            print(Fore.GREEN + "\nBuild Tools:" + Style.RESET_ALL)
            for tool in sorted(self.detected_env['build_tools']):
                print(f"  - {tool}")
                
        if self.detected_env['databases']:
            print(Fore.GREEN + "\nDatabases:" + Style.RESET_ALL)
            for db in sorted(self.detected_env['databases']):
                print(f"  - {db}")
                
        if self.detected_env['languages']:
            print(Fore.GREEN + "\nProgramming Languages:" + Style.RESET_ALL)
            for lang in sorted(self.detected_env['languages']):
                print(f"  - {lang}") 