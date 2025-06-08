import os
import sys
import json
import yaml
import toml
import logging
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from colorama import Fore, Style, init

class ConfigManager:
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir) if config_dir else Path.home() / '.aegis' / 'config'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._setup_logging()
        self.config = self._load_config()
        init()  # Initialize colorama
        
    def _setup_logging(self):
        """Setup logging configuration"""
        log_dir = self.config_dir / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / 'config.log'
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration"""
        try:
            config_file = self.config_dir / 'config.json'
            
            if not config_file.exists():
                # Create default configuration
                config = {
                    'shell': {
                        'prompt': '> ',
                        'history_size': 1000,
                        'auto_complete': True,
                        'syntax_highlighting': True
                    },
                    'editor': {
                        'default': 'vim',
                        'line_numbers': True,
                        'tab_size': 4,
                        'auto_indent': True
                    },
                    'theme': {
                        'primary': 'cyan',
                        'secondary': 'yellow',
                        'success': 'green',
                        'warning': 'yellow',
                        'error': 'red',
                        'info': 'blue'
                    },
                    'plugins': {
                        'enabled': [],
                        'disabled': [],
                        'auto_load': True
                    },
                    'paths': {
                        'home': str(Path.home()),
                        'config': str(self.config_dir),
                        'logs': str(self.config_dir / 'logs'),
                        'plugins': str(self.config_dir / 'plugins')
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
            logging.error(f"Error loading config: {e}")
            return {}
            
    def save_config(self):
        """Save configuration"""
        try:
            config_file = self.config_dir / 'config.json'
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            logging.error(f"Error saving config: {e}")
            
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        try:
            # Split key into parts
            parts = key.split('.')
            
            # Get value
            value = self.config
            for part in parts:
                if isinstance(value, dict):
                    value = value.get(part)
                else:
                    return default
                    
            return value if value is not None else default
        except Exception as e:
            logging.error(f"Error getting config value: {e}")
            return default
            
    def set(self, key: str, value: Any):
        """Set configuration value"""
        try:
            # Split key into parts
            parts = key.split('.')
            
            # Set value
            config = self.config
            for part in parts[:-1]:
                if part not in config:
                    config[part] = {}
                config = config[part]
                
            config[parts[-1]] = value
            
            # Save configuration
            self.save_config()
        except Exception as e:
            logging.error(f"Error setting config value: {e}")
            
    def delete(self, key: str):
        """Delete configuration value"""
        try:
            # Split key into parts
            parts = key.split('.')
            
            # Delete value
            config = self.config
            for part in parts[:-1]:
                if part not in config:
                    return
                config = config[part]
                
            if parts[-1] in config:
                del config[parts[-1]]
                
            # Save configuration
            self.save_config()
        except Exception as e:
            logging.error(f"Error deleting config value: {e}")
            
    def validate(self) -> bool:
        """Validate configuration"""
        try:
            # Check required sections
            required_sections = ['shell', 'editor', 'theme', 'plugins', 'paths']
            for section in required_sections:
                if section not in self.config:
                    logging.error(f"Missing required section: {section}")
                    return False
                    
            # Check shell section
            shell = self.config['shell']
            if not isinstance(shell.get('prompt'), str):
                logging.error("Invalid shell prompt")
                return False
            if not isinstance(shell.get('history_size'), int):
                logging.error("Invalid history size")
                return False
            if not isinstance(shell.get('auto_complete'), bool):
                logging.error("Invalid auto complete setting")
                return False
            if not isinstance(shell.get('syntax_highlighting'), bool):
                logging.error("Invalid syntax highlighting setting")
                return False
                
            # Check editor section
            editor = self.config['editor']
            if not isinstance(editor.get('default'), str):
                logging.error("Invalid default editor")
                return False
            if not isinstance(editor.get('line_numbers'), bool):
                logging.error("Invalid line numbers setting")
                return False
            if not isinstance(editor.get('tab_size'), int):
                logging.error("Invalid tab size")
                return False
            if not isinstance(editor.get('auto_indent'), bool):
                logging.error("Invalid auto indent setting")
                return False
                
            # Check theme section
            theme = self.config['theme']
            required_colors = ['primary', 'secondary', 'success', 'warning', 'error', 'info']
            for color in required_colors:
                if not isinstance(theme.get(color), str):
                    logging.error(f"Invalid theme color: {color}")
                    return False
                    
            # Check plugins section
            plugins = self.config['plugins']
            if not isinstance(plugins.get('enabled'), list):
                logging.error("Invalid enabled plugins")
                return False
            if not isinstance(plugins.get('disabled'), list):
                logging.error("Invalid disabled plugins")
                return False
            if not isinstance(plugins.get('auto_load'), bool):
                logging.error("Invalid auto load setting")
                return False
                
            # Check paths section
            paths = self.config['paths']
            required_paths = ['home', 'config', 'logs', 'plugins']
            for path in required_paths:
                if not isinstance(paths.get(path), str):
                    logging.error(f"Invalid path: {path}")
                    return False
                    
            return True
        except Exception as e:
            logging.error(f"Error validating config: {e}")
            return False
            
    def backup(self, name: str = None):
        """Backup configuration"""
        try:
            # Create backup directory
            backup_dir = self.config_dir / 'backups'
            backup_dir.mkdir(exist_ok=True)
            
            # Create backup name
            if name is None:
                name = time.strftime('%Y%m%d_%H%M%S')
                
            # Create backup file
            backup_file = backup_dir / f'config_{name}.json'
            with open(backup_file, 'w') as f:
                json.dump(self.config, f, indent=4)
                
            logging.info(f"Configuration backed up to {backup_file}")
        except Exception as e:
            logging.error(f"Error backing up config: {e}")
            
    def restore(self, name: str):
        """Restore configuration"""
        try:
            # Get backup file
            backup_dir = self.config_dir / 'backups'
            backup_file = backup_dir / f'config_{name}.json'
            
            if not backup_file.exists():
                logging.error(f"Backup not found: {name}")
                return
                
            # Load backup
            with open(backup_file) as f:
                config = json.load(f)
                
            # Validate backup
            if not self._validate_backup(config):
                logging.error("Invalid backup configuration")
                return
                
            # Restore configuration
            self.config = config
            self.save_config()
            
            logging.info(f"Configuration restored from {backup_file}")
        except Exception as e:
            logging.error(f"Error restoring config: {e}")
            
    def _validate_backup(self, config: Dict[str, Any]) -> bool:
        """Validate backup configuration"""
        try:
            # Check required sections
            required_sections = ['shell', 'editor', 'theme', 'plugins', 'paths']
            for section in required_sections:
                if section not in config:
                    return False
                    
            # Check shell section
            shell = config['shell']
            if not isinstance(shell.get('prompt'), str):
                return False
            if not isinstance(shell.get('history_size'), int):
                return False
            if not isinstance(shell.get('auto_complete'), bool):
                return False
            if not isinstance(shell.get('syntax_highlighting'), bool):
                return False
                
            # Check editor section
            editor = config['editor']
            if not isinstance(editor.get('default'), str):
                return False
            if not isinstance(editor.get('line_numbers'), bool):
                return False
            if not isinstance(editor.get('tab_size'), int):
                return False
            if not isinstance(editor.get('auto_indent'), bool):
                return False
                
            # Check theme section
            theme = config['theme']
            required_colors = ['primary', 'secondary', 'success', 'warning', 'error', 'info']
            for color in required_colors:
                if not isinstance(theme.get(color), str):
                    return False
                    
            # Check plugins section
            plugins = config['plugins']
            if not isinstance(plugins.get('enabled'), list):
                return False
            if not isinstance(plugins.get('disabled'), list):
                return False
            if not isinstance(plugins.get('auto_load'), bool):
                return False
                
            # Check paths section
            paths = config['paths']
            required_paths = ['home', 'config', 'logs', 'plugins']
            for path in required_paths:
                if not isinstance(paths.get(path), str):
                    return False
                    
            return True
        except Exception as e:
            logging.error(f"Error validating backup: {e}")
            return False
            
    def export(self, format: str = 'json', file: str = None):
        """Export configuration"""
        try:
            # Create export file
            if file is None:
                file = self.config_dir / f'config.{format}'
            else:
                file = Path(file)
                
            # Export configuration
            if format == 'json':
                with open(file, 'w') as f:
                    json.dump(self.config, f, indent=4)
            elif format == 'yaml':
                with open(file, 'w') as f:
                    yaml.dump(self.config, f, default_flow_style=False)
            elif format == 'toml':
                with open(file, 'w') as f:
                    toml.dump(self.config, f)
            else:
                logging.error(f"Unsupported format: {format}")
                return
                
            logging.info(f"Configuration exported to {file}")
        except Exception as e:
            logging.error(f"Error exporting config: {e}")
            
    def import_(self, file: str, format: str = 'json'):
        """Import configuration"""
        try:
            # Get import file
            file = Path(file)
            if not file.exists():
                logging.error(f"File not found: {file}")
                return
                
            # Import configuration
            if format == 'json':
                with open(file) as f:
                    config = json.load(f)
            elif format == 'yaml':
                with open(file) as f:
                    config = yaml.safe_load(f)
            elif format == 'toml':
                with open(file) as f:
                    config = toml.load(f)
            else:
                logging.error(f"Unsupported format: {format}")
                return
                
            # Validate configuration
            if not self._validate_backup(config):
                logging.error("Invalid configuration")
                return
                
            # Import configuration
            self.config = config
            self.save_config()
            
            logging.info(f"Configuration imported from {file}")
        except Exception as e:
            logging.error(f"Error importing config: {e}")
            
    def print_config(self):
        """Print configuration"""
        try:
            print(f"\n{Fore.CYAN}Configuration{Style.RESET_ALL}")
            
            # Print shell settings
            print(f"\n{Fore.YELLOW}Shell Settings:{Style.RESET_ALL}")
            shell = self.config['shell']
            print(f"Prompt: {shell['prompt']}")
            print(f"History Size: {shell['history_size']}")
            print(f"Auto Complete: {shell['auto_complete']}")
            print(f"Syntax Highlighting: {shell['syntax_highlighting']}")
            
            # Print editor settings
            print(f"\n{Fore.YELLOW}Editor Settings:{Style.RESET_ALL}")
            editor = self.config['editor']
            print(f"Default Editor: {editor['default']}")
            print(f"Line Numbers: {editor['line_numbers']}")
            print(f"Tab Size: {editor['tab_size']}")
            print(f"Auto Indent: {editor['auto_indent']}")
            
            # Print theme settings
            print(f"\n{Fore.YELLOW}Theme Settings:{Style.RESET_ALL}")
            theme = self.config['theme']
            for color, value in theme.items():
                print(f"{color}: {value}")
                
            # Print plugin settings
            print(f"\n{Fore.YELLOW}Plugin Settings:{Style.RESET_ALL}")
            plugins = self.config['plugins']
            print(f"Enabled Plugins: {', '.join(plugins['enabled']) or 'None'}")
            print(f"Disabled Plugins: {', '.join(plugins['disabled']) or 'None'}")
            print(f"Auto Load: {plugins['auto_load']}")
            
            # Print path settings
            print(f"\n{Fore.YELLOW}Path Settings:{Style.RESET_ALL}")
            paths = self.config['paths']
            for path, value in paths.items():
                print(f"{path}: {value}")
                
            print()
        except Exception as e:
            logging.error(f"Error printing config: {e}")
            
    def get_config_directory(self) -> Path:
        """Get configuration directory"""
        return self.config_dir 