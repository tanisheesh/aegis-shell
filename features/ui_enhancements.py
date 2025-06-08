import os
import sys
import json
import time
import logging
import shutil
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from colorama import Fore, Style, init

class UIEnhancements:
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir) if config_dir else Path.home() / '.aegis' / 'ui'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._setup_logging()
        self.config = self._load_config()
        init()  # Initialize colorama
        
    def _setup_logging(self):
        """Setup logging configuration"""
        log_dir = self.config_dir / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / 'ui.log'
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
    def _load_config(self) -> Dict[str, Any]:
        """Load UI configuration"""
        try:
            config_file = self.config_dir / 'ui_config.json'
            
            if not config_file.exists():
                # Create default configuration
                config = {
                    'theme': {
                        'primary': 'cyan',
                        'secondary': 'yellow',
                        'success': 'green',
                        'warning': 'yellow',
                        'error': 'red',
                        'info': 'blue'
                    },
                    'notifications': {
                        'enabled': True,
                        'duration': 5,  # seconds
                        'position': 'top-right'
                    },
                    'progress': {
                        'style': 'block',
                        'width': 50,
                        'fill': '█',
                        'empty': '░'
                    },
                    'table': {
                        'style': 'simple',
                        'header': True,
                        'border': True
                    },
                    'menu': {
                        'style': 'simple',
                        'highlight': True,
                        'clear_screen': True
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
            logging.error(f"Error loading UI config: {e}")
            return {}
            
    def show_notification(self, message: str, level: str = 'info', duration: Optional[int] = None):
        """Show notification"""
        try:
            if not self.config['notifications']['enabled']:
                return
                
            # Get color based on level
            color = getattr(Fore, self.config['theme'][level].upper())
            
            # Get duration
            duration = duration or self.config['notifications']['duration']
            
            # Print notification
            print(f"\n{color}{message}{Style.RESET_ALL}")
            
            # Wait for duration
            time.sleep(duration)
            
            # Clear notification
            print('\033[F\033[K', end='')
        except Exception as e:
            logging.error(f"Error showing notification: {e}")
            
    def show_spinner(self, message: str, func: callable, *args, **kwargs):
        """Show loading spinner"""
        try:
            # Spinner characters
            spinner = '⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
            
            # Start spinner
            i = 0
            while True:
                # Print spinner
                sys.stdout.write(f'\r{spinner[i]} {message}')
                sys.stdout.flush()
                
                # Check if function is done
                if func(*args, **kwargs):
                    break
                    
                # Update spinner
                i = (i + 1) % len(spinner)
                time.sleep(0.1)
                
            # Clear spinner
            sys.stdout.write('\r\033[K')
            sys.stdout.flush()
        except Exception as e:
            logging.error(f"Error showing spinner: {e}")
            
    def show_progress(self, current: int, total: int, message: str = ''):
        """Show progress bar"""
        try:
            # Get progress bar style
            style = self.config['progress']['style']
            width = self.config['progress']['width']
            fill = self.config['progress']['fill']
            empty = self.config['progress']['empty']
            
            # Calculate progress
            progress = current / total
            filled = int(width * progress)
            
            # Create progress bar
            if style == 'block':
                bar = fill * filled + empty * (width - filled)
            else:
                bar = '=' * filled + '-' * (width - filled)
                
            # Print progress bar
            print(f'\r{message} [{bar}] {progress:.1%}', end='')
            
            # Clear progress bar if done
            if current == total:
                print()
        except Exception as e:
            logging.error(f"Error showing progress: {e}")
            
    def show_table(self, headers: List[str], rows: List[List[str]], title: str = ''):
        """Show formatted table"""
        try:
            # Get table style
            style = self.config['table']['style']
            show_header = self.config['table']['header']
            show_border = self.config['table']['border']
            
            # Calculate column widths
            widths = [len(h) for h in headers]
            for row in rows:
                for i, cell in enumerate(row):
                    widths[i] = max(widths[i], len(str(cell)))
                    
            # Print title
            if title:
                print(f"\n{Fore.CYAN}{title}{Style.RESET_ALL}")
                
            # Print header
            if show_header:
                if show_border:
                    print('┌' + '┬'.join('─' * (w + 2) for w in widths) + '┐')
                    
                header = '│ ' + ' │ '.join(f"{h:<{w}}" for h, w in zip(headers, widths)) + ' │'
                print(header)
                
                if show_border:
                    print('├' + '┼'.join('─' * (w + 2) for w in widths) + '┤')
                    
            # Print rows
            for row in rows:
                if show_border:
                    print('│ ' + ' │ '.join(f"{str(cell):<{w}}" for cell, w in zip(row, widths)) + ' │')
                else:
                    print('  '.join(f"{str(cell):<{w}}" for cell, w in zip(row, widths)))
                    
            # Print footer
            if show_border:
                print('└' + '┴'.join('─' * (w + 2) for w in widths) + '┘')
                
            print()
        except Exception as e:
            logging.error(f"Error showing table: {e}")
            
    def show_tree(self, path: str, level: int = 0, max_level: Optional[int] = None):
        """Show directory tree"""
        try:
            # Check if max level reached
            if max_level is not None and level > max_level:
                return
                
            # Get directory contents
            path = Path(path)
            if not path.exists():
                return
                
            # Print current directory
            prefix = '  ' * level
            if level == 0:
                print(f"\n{Fore.CYAN}{path.name}{Style.RESET_ALL}")
            else:
                print(f"{prefix}{Fore.CYAN}{path.name}{Style.RESET_ALL}")
                
            # Print files and directories
            for item in sorted(path.iterdir()):
                if item.is_dir():
                    self.show_tree(item, level + 1, max_level)
                else:
                    print(f"{prefix}  {Fore.GREEN}{item.name}{Style.RESET_ALL}")
        except Exception as e:
            logging.error(f"Error showing tree: {e}")
            
    def show_menu(self, title: str, options: List[str], message: str = '') -> int:
        """Show interactive menu"""
        try:
            # Get menu style
            style = self.config['menu']['style']
            highlight = self.config['menu']['highlight']
            clear = self.config['menu']['clear_screen']
            
            # Clear screen if enabled
            if clear:
                os.system('cls' if os.name == 'nt' else 'clear')
                
            # Print title
            print(f"\n{Fore.CYAN}{title}{Style.RESET_ALL}")
            
            # Print message
            if message:
                print(f"\n{message}")
                
            # Print options
            for i, option in enumerate(options, 1):
                if highlight:
                    print(f"{i}. {Fore.YELLOW}{option}{Style.RESET_ALL}")
                else:
                    print(f"{i}. {option}")
                    
            # Get selection
            while True:
                try:
                    choice = int(input("\nEnter choice: "))
                    if 1 <= choice <= len(options):
                        return choice
                    print(f"{Fore.RED}Invalid choice{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED}Invalid input{Style.RESET_ALL}")
        except Exception as e:
            logging.error(f"Error showing menu: {e}")
            return 0
            
    def show_dialog(self, title: str, message: str, buttons: List[str] = None) -> int:
        """Show dialog box"""
        try:
            # Set default buttons
            if buttons is None:
                buttons = ['OK', 'Cancel']
                
            # Get terminal size
            columns, rows = shutil.get_terminal_size()
            
            # Create dialog box
            box_width = min(max(len(title), len(message), max(len(b) for b in buttons)) + 4, columns - 4)
            box_height = 5 + len(message.split('\n'))
            
            # Print top border
            print(f"\n{' ' * ((columns - box_width) // 2)}┌{'─' * box_width}┐")
            
            # Print title
            title_padding = (box_width - len(title)) // 2
            print(f"{' ' * ((columns - box_width) // 2)}│{' ' * title_padding}{Fore.CYAN}{title}{Style.RESET_ALL}{' ' * (box_width - title_padding - len(title))}│")
            
            # Print separator
            print(f"{' ' * ((columns - box_width) // 2)}├{'─' * box_width}┤")
            
            # Print message
            for line in message.split('\n'):
                line_padding = (box_width - len(line)) // 2
                print(f"{' ' * ((columns - box_width) // 2)}│{' ' * line_padding}{line}{' ' * (box_width - line_padding - len(line))}│")
                
            # Print separator
            print(f"{' ' * ((columns - box_width) // 2)}├{'─' * box_width}┤")
            
            # Print buttons
            button_padding = (box_width - sum(len(b) + 2 for b in buttons)) // 2
            print(f"{' ' * ((columns - box_width) // 2)}│{' ' * button_padding}{'  '.join(f'[{Fore.YELLOW}{i + 1}{Style.RESET_ALL}] {b}' for i, b in enumerate(buttons))}{' ' * (box_width - button_padding - sum(len(b) + 2 for b in buttons))}│")
            
            # Print bottom border
            print(f"{' ' * ((columns - box_width) // 2)}└{'─' * box_width}┘")
            
            # Get selection
            while True:
                try:
                    choice = int(input("\nEnter choice: "))
                    if 1 <= choice <= len(buttons):
                        return choice
                    print(f"{Fore.RED}Invalid choice{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED}Invalid input{Style.RESET_ALL}")
        except Exception as e:
            logging.error(f"Error showing dialog: {e}")
            return 0
            
    def show_help(self, command: str = None):
        """Show help information"""
        try:
            # Load help data
            help_file = self.config_dir / 'help.json'
            if not help_file.exists():
                return
                
            with open(help_file) as f:
                help_data = json.load(f)
                
            # Show specific command help
            if command:
                if command in help_data:
                    data = help_data[command]
                    print(f"\n{Fore.CYAN}{command}{Style.RESET_ALL}")
                    print(f"\n{data['description']}")
                    print(f"\nUsage: {data['usage']}")
                    
                    if 'options' in data:
                        print("\nOptions:")
                        for opt, desc in data['options'].items():
                            print(f"  {opt}: {desc}")
                            
                    if 'examples' in data:
                        print("\nExamples:")
                        for ex in data['examples']:
                            print(f"  {ex}")
                else:
                    print(f"\n{Fore.RED}No help available for {command}{Style.RESET_ALL}")
                return
                
            # Show general help
            print(f"\n{Fore.CYAN}Available Commands:{Style.RESET_ALL}")
            for cmd, data in help_data.items():
                print(f"\n{Fore.YELLOW}{cmd}{Style.RESET_ALL}")
                print(f"  {data['description']}")
                
            print(f"\nUse 'help <command>' for more information")
        except Exception as e:
            logging.error(f"Error showing help: {e}")
            
    def show_version(self):
        """Show version information"""
        try:
            # Load version data
            version_file = self.config_dir / 'version.json'
            if not version_file.exists():
                return
                
            with open(version_file) as f:
                version_data = json.load(f)
                
            # Print version information
            print(f"\n{Fore.CYAN}Version Information{Style.RESET_ALL}")
            print(f"\nVersion: {version_data['version']}")
            print(f"Build: {version_data['build']}")
            print(f"Date: {version_data['date']}")
            
            if 'changes' in version_data:
                print("\nChanges:")
                for change in version_data['changes']:
                    print(f"  {change}")
        except Exception as e:
            logging.error(f"Error showing version: {e}")
            
    def show_license(self):
        """Show license information"""
        try:
            # Load license data
            license_file = self.config_dir / 'license.txt'
            if not license_file.exists():
                return
                
            with open(license_file) as f:
                license_text = f.read()
                
            # Print license information
            print(f"\n{Fore.CYAN}License Information{Style.RESET_ALL}")
            print(f"\n{license_text}")
        except Exception as e:
            logging.error(f"Error showing license: {e}")
            
    def show_credits(self):
        """Show credits information"""
        try:
            # Load credits data
            credits_file = self.config_dir / 'credits.json'
            if not credits_file.exists():
                return
                
            with open(credits_file) as f:
                credits_data = json.load(f)
                
            # Print credits information
            print(f"\n{Fore.CYAN}Credits{Style.RESET_ALL}")
            
            if 'authors' in credits_data:
                print("\nAuthors:")
                for author in credits_data['authors']:
                    print(f"  {author}")
                    
            if 'contributors' in credits_data:
                print("\nContributors:")
                for contributor in credits_data['contributors']:
                    print(f"  {contributor}")
                    
            if 'libraries' in credits_data:
                print("\nLibraries:")
                for lib, info in credits_data['libraries'].items():
                    print(f"  {lib}: {info}")
        except Exception as e:
            logging.error(f"Error showing credits: {e}")
            
    def show_changelog(self):
        """Show changelog information"""
        try:
            # Load changelog data
            changelog_file = self.config_dir / 'changelog.json'
            if not changelog_file.exists():
                return
                
            with open(changelog_file) as f:
                changelog_data = json.load(f)
                
            # Print changelog information
            print(f"\n{Fore.CYAN}Changelog{Style.RESET_ALL}")
            
            for version, changes in changelog_data.items():
                print(f"\n{Fore.YELLOW}Version {version}{Style.RESET_ALL}")
                for change in changes:
                    print(f"  {change}")
        except Exception as e:
            logging.error(f"Error showing changelog: {e}")
            
    def show_about(self):
        """Show about information"""
        try:
            # Load about data
            about_file = self.config_dir / 'about.json'
            if not about_file.exists():
                return
                
            with open(about_file) as f:
                about_data = json.load(f)
                
            # Print about information
            print(f"\n{Fore.CYAN}About{Style.RESET_ALL}")
            print(f"\n{about_data['description']}")
            
            if 'features' in about_data:
                print("\nFeatures:")
                for feature in about_data['features']:
                    print(f"  {feature}")
                    
            if 'contact' in about_data:
                print("\nContact:")
                for method, info in about_data['contact'].items():
                    print(f"  {method}: {info}")
        except Exception as e:
            logging.error(f"Error showing about: {e}")
            
    def get_config_directory(self) -> Path:
        """Get configuration directory"""
        return self.config_dir 