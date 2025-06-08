import os
import sys
import json
import traceback
import logging
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import time
from datetime import datetime
from colorama import Fore, Style, init
import threading
import queue

class ErrorHandler:
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir) if config_dir else Path.home() / '.aegis' / 'errors'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._setup_logging()
        self.patterns = self._load_patterns()
        self.history = []
        init()  # Initialize colorama
        
    def _setup_logging(self):
        """Setup logging configuration"""
        log_dir = self.config_dir / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / 'error.log'
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
    def _load_patterns(self) -> Dict[str, Any]:
        """Load error patterns"""
        try:
            patterns_file = self.config_dir / 'patterns.json'
            
            if not patterns_file.exists():
                # Create default patterns
                patterns = {
                    'file_system': {
                        'patterns': [
                            'file not found',
                            'permission denied',
                            'no such file or directory',
                            'is a directory',
                            'not a directory',
                            'directory not empty',
                            'file exists',
                            'file too large',
                            'disk full',
                            'read-only file system'
                        ],
                        'recovery': {
                            'check_permissions': True,
                            'create_missing': True,
                            'clear_space': True,
                            'retry_operation': True
                        }
                    },
                    'network': {
                        'patterns': [
                            'connection refused',
                            'connection timed out',
                            'network unreachable',
                            'host unreachable',
                            'no route to host',
                            'address already in use',
                            'address family not supported',
                            'broken pipe',
                            'connection reset',
                            'dns resolution failed'
                        ],
                        'recovery': {
                            'check_connection': True,
                            'retry_connection': True,
                            'check_dns': True,
                            'check_firewall': True
                        }
                    },
                    'permission': {
                        'patterns': [
                            'permission denied',
                            'access denied',
                            'insufficient permissions',
                            'not authorized',
                            'requires elevated privileges',
                            'operation not permitted',
                            'read-only',
                            'write-protected',
                            'cannot modify',
                            'cannot delete'
                        ],
                        'recovery': {
                            'check_permissions': True,
                            'request_elevation': True,
                            'change_ownership': True,
                            'change_mode': True
                        }
                    },
                    'validation': {
                        'patterns': [
                            'invalid argument',
                            'invalid option',
                            'invalid value',
                            'missing required',
                            'unexpected value',
                            'type error',
                            'format error',
                            'syntax error',
                            'parse error',
                            'validation failed'
                        ],
                        'recovery': {
                            'validate_input': True,
                            'check_format': True,
                            'check_type': True,
                            'check_required': True
                        }
                    },
                    'resource': {
                        'patterns': [
                            'out of memory',
                            'memory allocation failed',
                            'too many open files',
                            'too many processes',
                            'resource temporarily unavailable',
                            'resource busy',
                            'resource deadlock',
                            'resource limit exceeded',
                            'resource exhausted',
                            'resource unavailable'
                        ],
                        'recovery': {
                            'free_memory': True,
                            'close_files': True,
                            'kill_processes': True,
                            'increase_limits': True
                        }
                    }
                }
                
                # Save default patterns
                with open(patterns_file, 'w') as f:
                    json.dump(patterns, f, indent=4)
                    
                return patterns
                
            # Load existing patterns
            with open(patterns_file) as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading error patterns: {e}")
            return {}
            
    def handle_error(self, error: Exception, context: Dict[str, Any] = None):
        """Handle error"""
        try:
            # Get error message
            message = str(error).lower()
            
            # Get error type
            error_type = type(error).__name__
            
            # Create error record
            record = {
                'timestamp': time.time(),
                'type': error_type,
                'message': message,
                'context': context or {},
                'recovery': {}
            }
            
            # Check patterns
            for category, data in self.patterns.items():
                for pattern in data['patterns']:
                    if pattern in message:
                        # Add category
                        record['category'] = category
                        
                        # Try recovery
                        recovery = self._try_recovery(category, data['recovery'], error, context)
                        record['recovery'] = recovery
                        
                        # Add to history
                        self.history.append(record)
                        
                        # Save history
                        self._save_history()
                        
                        # Log error
                        logging.error(f"Error: {message} (Category: {category})")
                        
                        # Print error
                        print(f"\n{Fore.RED}Error: {message}{Style.RESET_ALL}")
                        if recovery:
                            print(f"{Fore.GREEN}Recovery: {recovery['message']}{Style.RESET_ALL}")
                            
                        return record
                        
            # No pattern matched
            record['category'] = 'unknown'
            self.history.append(record)
            self._save_history()
            
            logging.error(f"Unknown error: {message}")
            print(f"\n{Fore.RED}Unknown error: {message}{Style.RESET_ALL}")
            
            return record
        except Exception as e:
            logging.error(f"Error handling error: {e}")
            return None
            
    def _try_recovery(self, category: str, recovery_options: Dict[str, bool], error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Try recovery strategies"""
        try:
            recovery = {
                'success': False,
                'message': 'No recovery attempted',
                'actions': []
            }
            
            # File system recovery
            if category == 'file_system':
                if recovery_options['check_permissions']:
                    if self._check_file_permissions(error, context):
                        recovery['actions'].append('checked_permissions')
                        
                if recovery_options['create_missing']:
                    if self._create_missing_file(error, context):
                        recovery['actions'].append('created_missing')
                        
                if recovery_options['clear_space']:
                    if self._clear_disk_space(error, context):
                        recovery['actions'].append('cleared_space')
                        
                if recovery_options['retry_operation']:
                    if self._retry_file_operation(error, context):
                        recovery['actions'].append('retried_operation')
                        
            # Network recovery
            elif category == 'network':
                if recovery_options['check_connection']:
                    if self._check_network_connection(error, context):
                        recovery['actions'].append('checked_connection')
                        
                if recovery_options['retry_connection']:
                    if self._retry_network_connection(error, context):
                        recovery['actions'].append('retried_connection')
                        
                if recovery_options['check_dns']:
                    if self._check_dns_resolution(error, context):
                        recovery['actions'].append('checked_dns')
                        
                if recovery_options['check_firewall']:
                    if self._check_firewall_rules(error, context):
                        recovery['actions'].append('checked_firewall')
                        
            # Permission recovery
            elif category == 'permission':
                if recovery_options['check_permissions']:
                    if self._check_permissions(error, context):
                        recovery['actions'].append('checked_permissions')
                        
                if recovery_options['request_elevation']:
                    if self._request_elevation(error, context):
                        recovery['actions'].append('requested_elevation')
                        
                if recovery_options['change_ownership']:
                    if self._change_ownership(error, context):
                        recovery['actions'].append('changed_ownership')
                        
                if recovery_options['change_mode']:
                    if self._change_mode(error, context):
                        recovery['actions'].append('changed_mode')
                        
            # Validation recovery
            elif category == 'validation':
                if recovery_options['validate_input']:
                    if self._validate_input(error, context):
                        recovery['actions'].append('validated_input')
                        
                if recovery_options['check_format']:
                    if self._check_format(error, context):
                        recovery['actions'].append('checked_format')
                        
                if recovery_options['check_type']:
                    if self._check_type(error, context):
                        recovery['actions'].append('checked_type')
                        
                if recovery_options['check_required']:
                    if self._check_required(error, context):
                        recovery['actions'].append('checked_required')
                        
            # Resource recovery
            elif category == 'resource':
                if recovery_options['free_memory']:
                    if self._free_memory(error, context):
                        recovery['actions'].append('freed_memory')
                        
                if recovery_options['close_files']:
                    if self._close_files(error, context):
                        recovery['actions'].append('closed_files')
                        
                if recovery_options['kill_processes']:
                    if self._kill_processes(error, context):
                        recovery['actions'].append('killed_processes')
                        
                if recovery_options['increase_limits']:
                    if self._increase_limits(error, context):
                        recovery['actions'].append('increased_limits')
                        
            # Update recovery status
            if recovery['actions']:
                recovery['success'] = True
                recovery['message'] = f"Recovery successful: {', '.join(recovery['actions'])}"
            else:
                recovery['message'] = "No recovery actions succeeded"
                
            return recovery
        except Exception as e:
            logging.error(f"Error trying recovery: {e}")
            return {
                'success': False,
                'message': f"Recovery failed: {str(e)}",
                'actions': []
            }
            
    def _check_file_permissions(self, error: Exception, context: Dict[str, Any] = None) -> bool:
        """Check file permissions"""
        try:
            # TODO: Implement file permission checking
            return False
        except Exception as e:
            logging.error(f"Error checking file permissions: {e}")
            return False
            
    def _create_missing_file(self, error: Exception, context: Dict[str, Any] = None) -> bool:
        """Create missing file"""
        try:
            # TODO: Implement missing file creation
            return False
        except Exception as e:
            logging.error(f"Error creating missing file: {e}")
            return False
            
    def _clear_disk_space(self, error: Exception, context: Dict[str, Any] = None) -> bool:
        """Clear disk space"""
        try:
            # TODO: Implement disk space clearing
            return False
        except Exception as e:
            logging.error(f"Error clearing disk space: {e}")
            return False
            
    def _retry_file_operation(self, error: Exception, context: Dict[str, Any] = None) -> bool:
        """Retry file operation"""
        try:
            # TODO: Implement file operation retry
            return False
        except Exception as e:
            logging.error(f"Error retrying file operation: {e}")
            return False
            
    def _check_network_connection(self, error: Exception, context: Dict[str, Any] = None) -> bool:
        """Check network connection"""
        try:
            # TODO: Implement network connection checking
            return False
        except Exception as e:
            logging.error(f"Error checking network connection: {e}")
            return False
            
    def _retry_network_connection(self, error: Exception, context: Dict[str, Any] = None) -> bool:
        """Retry network connection"""
        try:
            # TODO: Implement network connection retry
            return False
        except Exception as e:
            logging.error(f"Error retrying network connection: {e}")
            return False
            
    def _check_dns_resolution(self, error: Exception, context: Dict[str, Any] = None) -> bool:
        """Check DNS resolution"""
        try:
            # TODO: Implement DNS resolution checking
            return False
        except Exception as e:
            logging.error(f"Error checking DNS resolution: {e}")
            return False
            
    def _check_firewall_rules(self, error: Exception, context: Dict[str, Any] = None) -> bool:
        """Check firewall rules"""
        try:
            # TODO: Implement firewall rule checking
            return False
        except Exception as e:
            logging.error(f"Error checking firewall rules: {e}")
            return False
            
    def _check_permissions(self, error: Exception, context: Dict[str, Any] = None) -> bool:
        """Check permissions"""
        try:
            # TODO: Implement permission checking
            return False
        except Exception as e:
            logging.error(f"Error checking permissions: {e}")
            return False
            
    def _request_elevation(self, error: Exception, context: Dict[str, Any] = None) -> bool:
        """Request elevation"""
        try:
            # TODO: Implement elevation request
            return False
        except Exception as e:
            logging.error(f"Error requesting elevation: {e}")
            return False
            
    def _change_ownership(self, error: Exception, context: Dict[str, Any] = None) -> bool:
        """Change ownership"""
        try:
            # TODO: Implement ownership change
            return False
        except Exception as e:
            logging.error(f"Error changing ownership: {e}")
            return False
            
    def _change_mode(self, error: Exception, context: Dict[str, Any] = None) -> bool:
        """Change mode"""
        try:
            # TODO: Implement mode change
            return False
        except Exception as e:
            logging.error(f"Error changing mode: {e}")
            return False
            
    def _validate_input(self, error: Exception, context: Dict[str, Any] = None) -> bool:
        """Validate input"""
        try:
            # TODO: Implement input validation
            return False
        except Exception as e:
            logging.error(f"Error validating input: {e}")
            return False
            
    def _check_format(self, error: Exception, context: Dict[str, Any] = None) -> bool:
        """Check format"""
        try:
            # TODO: Implement format checking
            return False
        except Exception as e:
            logging.error(f"Error checking format: {e}")
            return False
            
    def _check_type(self, error: Exception, context: Dict[str, Any] = None) -> bool:
        """Check type"""
        try:
            # TODO: Implement type checking
            return False
        except Exception as e:
            logging.error(f"Error checking type: {e}")
            return False
            
    def _check_required(self, error: Exception, context: Dict[str, Any] = None) -> bool:
        """Check required"""
        try:
            # TODO: Implement required checking
            return False
        except Exception as e:
            logging.error(f"Error checking required: {e}")
            return False
            
    def _free_memory(self, error: Exception, context: Dict[str, Any] = None) -> bool:
        """Free memory"""
        try:
            # TODO: Implement memory freeing
            return False
        except Exception as e:
            logging.error(f"Error freeing memory: {e}")
            return False
            
    def _close_files(self, error: Exception, context: Dict[str, Any] = None) -> bool:
        """Close files"""
        try:
            # TODO: Implement file closing
            return False
        except Exception as e:
            logging.error(f"Error closing files: {e}")
            return False
            
    def _kill_processes(self, error: Exception, context: Dict[str, Any] = None) -> bool:
        """Kill processes"""
        try:
            # TODO: Implement process killing
            return False
        except Exception as e:
            logging.error(f"Error killing processes: {e}")
            return False
            
    def _increase_limits(self, error: Exception, context: Dict[str, Any] = None) -> bool:
        """Increase limits"""
        try:
            # TODO: Implement limit increasing
            return False
        except Exception as e:
            logging.error(f"Error increasing limits: {e}")
            return False
            
    def _save_history(self):
        """Save error history"""
        try:
            history_file = self.config_dir / 'history.json'
            with open(history_file, 'w') as f:
                json.dump(self.history, f, indent=4)
        except Exception as e:
            logging.error(f"Error saving error history: {e}")
            
    def get_history(self) -> List[Dict[str, Any]]:
        """Get error history"""
        return self.history
        
    def clear_history(self):
        """Clear error history"""
        self.history = []
        self._save_history()
        
    def print_history(self):
        """Print error history"""
        try:
            if not self.history:
                print(f"\n{Fore.RED}No error history available{Style.RESET_ALL}\n")
                return
                
            print(f"\n{Fore.CYAN}Error History{Style.RESET_ALL}")
            
            for record in self.history:
                print(f"\n{Fore.YELLOW}Error:{Style.RESET_ALL}")
                print(f"Time: {time.ctime(record['timestamp'])}")
                print(f"Type: {record['type']}")
                print(f"Category: {record['category']}")
                print(f"Message: {record['message']}")
                
                if record['context']:
                    print("\nContext:")
                    for key, value in record['context'].items():
                        print(f"  {key}: {value}")
                        
                if record['recovery']:
                    print("\nRecovery:")
                    print(f"  Success: {record['recovery']['success']}")
                    print(f"  Message: {record['recovery']['message']}")
                    if record['recovery']['actions']:
                        print(f"  Actions: {', '.join(record['recovery']['actions'])}")
                        
            print()
        except Exception as e:
            logging.error(f"Error printing error history: {e}")
            
    def get_config_directory(self) -> Path:
        """Get configuration directory"""
        return self.config_dir 