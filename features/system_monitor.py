import os
import sys
import json
import time
import logging
import threading
import subprocess
import psutil
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from colorama import Fore, Style, init

class SystemMonitor:
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir) if config_dir else Path.home() / '.aegis' / 'monitor'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._setup_logging()
        self.config = self._load_config()
        self.monitoring = False
        self.monitor_thread = None
        self.resource_history = []
        self.alerts = []
        init()  # Initialize colorama
        
    def _setup_logging(self):
        """Setup logging configuration"""
        log_dir = self.config_dir / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / 'monitor.log'
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
    def _load_config(self) -> Dict[str, Any]:
        """Load monitor configuration"""
        try:
            config_file = self.config_dir / 'monitor_config.json'
            
            if not config_file.exists():
                # Create default configuration
                config = {
                    'monitoring_interval': 1.0,  # seconds
                    'history_size': 1000,  # number of records
                    'thresholds': {
                        'cpu_percent': 80.0,
                        'memory_percent': 80.0,
                        'disk_percent': 80.0,
                        'network_io': {
                            'bytes_sent': 1000000,  # 1 MB/s
                            'bytes_recv': 1000000   # 1 MB/s
                        },
                        'process_count': 1000
                    },
                    'alerts': {
                        'enabled': True,
                        'cooldown': 300,  # seconds
                        'notify': True
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
            logging.error(f"Error loading monitor config: {e}")
            return {}
            
    def start_monitoring(self):
        """Start system monitoring"""
        try:
            if self.monitoring:
                logging.warning("Monitoring is already running")
                return
                
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitoring_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            logging.info("System monitoring started")
        except Exception as e:
            logging.error(f"Error starting monitoring: {e}")
            
    def stop_monitoring(self):
        """Stop system monitoring"""
        try:
            if not self.monitoring:
                logging.warning("Monitoring is not running")
                return
                
            self.monitoring = False
            if self.monitor_thread:
                self.monitor_thread.join()
            logging.info("System monitoring stopped")
        except Exception as e:
            logging.error(f"Error stopping monitoring: {e}")
            
    def _monitoring_loop(self):
        """Monitoring loop"""
        try:
            while self.monitoring:
                # Get resource usage
                usage = self._get_resource_usage()
                
                # Check thresholds
                self._check_thresholds(usage)
                
                # Save to history
                self._save_to_history(usage)
                
                # Wait for next interval
                time.sleep(self.config['monitoring_interval'])
        except Exception as e:
            logging.error(f"Error in monitoring loop: {e}")
            self.monitoring = False
            
    def _get_resource_usage(self) -> Dict[str, Any]:
        """Get current resource usage"""
        try:
            # Get CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Get memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Get disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Get network I/O
            network = psutil.net_io_counters()
            network_io = {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv,
                'errin': network.errin,
                'errout': network.errout,
                'dropin': network.dropin,
                'dropout': network.dropout
            }
            
            # Get process count
            process_count = len(psutil.pids())
            
            # Create resource usage record
            usage = {
                'timestamp': time.time(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'disk_percent': disk_percent,
                'network_io': network_io,
                'process_count': process_count
            }
            
            return usage
        except Exception as e:
            logging.error(f"Error getting resource usage: {e}")
            return {}
            
    def _check_thresholds(self, usage: Dict[str, Any]):
        """Check resource usage against thresholds"""
        try:
            if not self.config['alerts']['enabled']:
                return
                
            # Get thresholds
            thresholds = self.config['thresholds']
            
            # Check CPU usage
            if usage['cpu_percent'] > thresholds['cpu_percent']:
                self._create_alert('cpu', usage['cpu_percent'], thresholds['cpu_percent'])
                
            # Check memory usage
            if usage['memory_percent'] > thresholds['memory_percent']:
                self._create_alert('memory', usage['memory_percent'], thresholds['memory_percent'])
                
            # Check disk usage
            if usage['disk_percent'] > thresholds['disk_percent']:
                self._create_alert('disk', usage['disk_percent'], thresholds['disk_percent'])
                
            # Check network I/O
            network_io = usage['network_io']
            if network_io['bytes_sent'] > thresholds['network_io']['bytes_sent']:
                self._create_alert('network_sent', network_io['bytes_sent'], thresholds['network_io']['bytes_sent'])
                
            if network_io['bytes_recv'] > thresholds['network_io']['bytes_recv']:
                self._create_alert('network_recv', network_io['bytes_recv'], thresholds['network_io']['bytes_recv'])
                
            # Check process count
            if usage['process_count'] > thresholds['process_count']:
                self._create_alert('process_count', usage['process_count'], thresholds['process_count'])
        except Exception as e:
            logging.error(f"Error checking thresholds: {e}")
            
    def _create_alert(self, resource: str, value: float, threshold: float):
        """Create alert for threshold violation"""
        try:
            # Check cooldown
            if self.alerts:
                last_alert = self.alerts[-1]
                if time.time() - last_alert['timestamp'] < self.config['alerts']['cooldown']:
                    return
                    
            # Create alert
            alert = {
                'timestamp': time.time(),
                'resource': resource,
                'value': value,
                'threshold': threshold,
                'message': f"{resource} usage ({value:.1f}) exceeded threshold ({threshold:.1f})"
            }
            
            # Add to alerts
            self.alerts.append(alert)
            
            # Save alerts
            self._save_alerts()
            
            # Log alert
            logging.warning(alert['message'])
            
            # Notify if enabled
            if self.config['alerts']['notify']:
                self._notify_alert(alert)
        except Exception as e:
            logging.error(f"Error creating alert: {e}")
            
    def _notify_alert(self, alert: Dict[str, Any]):
        """Notify about alert"""
        try:
            # Print alert
            print(f"\n{Fore.RED}Alert: {alert['message']}{Style.RESET_ALL}")
            
            # TODO: Add more notification methods (email, SMS, etc.)
        except Exception as e:
            logging.error(f"Error notifying alert: {e}")
            
    def _save_to_history(self, usage: Dict[str, Any]):
        """Save resource usage to history"""
        try:
            self.resource_history.append(usage)
            
            # Trim history if needed
            if len(self.resource_history) > self.config['history_size']:
                self.resource_history = self.resource_history[-self.config['history_size']:]
                
            self._save_history()
        except Exception as e:
            logging.error(f"Error saving to history: {e}")
            
    def _save_history(self):
        """Save resource history to file"""
        try:
            history_file = self.config_dir / 'resource_history.json'
            with open(history_file, 'w') as f:
                json.dump(self.resource_history, f, indent=4)
        except Exception as e:
            logging.error(f"Error saving history: {e}")
            
    def _save_alerts(self):
        """Save alerts to file"""
        try:
            alerts_file = self.config_dir / 'alerts.json'
            with open(alerts_file, 'w') as f:
                json.dump(self.alerts, f, indent=4)
        except Exception as e:
            logging.error(f"Error saving alerts: {e}")
            
    def get_resource_history(self) -> List[Dict[str, Any]]:
        """Get resource history"""
        return self.resource_history
        
    def get_alerts(self) -> List[Dict[str, Any]]:
        """Get alerts"""
        return self.alerts
        
    def clear_history(self):
        """Clear resource history"""
        self.resource_history = []
        self._save_history()
        
    def clear_alerts(self):
        """Clear alerts"""
        self.alerts = []
        self._save_alerts()
        
    def print_resource_stats(self):
        """Print resource statistics"""
        try:
            if not self.resource_history:
                print(f"\n{Fore.RED}No resource history available{Style.RESET_ALL}\n")
                return
                
            print(f"\n{Fore.CYAN}Resource Statistics{Style.RESET_ALL}")
            
            # Calculate statistics
            cpu_percent = [r['cpu_percent'] for r in self.resource_history]
            memory_percent = [r['memory_percent'] for r in self.resource_history]
            disk_percent = [r['disk_percent'] for r in self.resource_history]
            network_sent = [r['network_io']['bytes_sent'] for r in self.resource_history]
            network_recv = [r['network_io']['bytes_recv'] for r in self.resource_history]
            process_count = [r['process_count'] for r in self.resource_history]
            
            # Print CPU statistics
            print(f"\n{Fore.YELLOW}CPU Usage:{Style.RESET_ALL}")
            print(f"Current: {cpu_percent[-1]:.1f}%")
            print(f"Average: {sum(cpu_percent) / len(cpu_percent):.1f}%")
            print(f"Minimum: {min(cpu_percent):.1f}%")
            print(f"Maximum: {max(cpu_percent):.1f}%")
            
            # Print memory statistics
            print(f"\n{Fore.YELLOW}Memory Usage:{Style.RESET_ALL}")
            print(f"Current: {memory_percent[-1]:.1f}%")
            print(f"Average: {sum(memory_percent) / len(memory_percent):.1f}%")
            print(f"Minimum: {min(memory_percent):.1f}%")
            print(f"Maximum: {max(memory_percent):.1f}%")
            
            # Print disk statistics
            print(f"\n{Fore.YELLOW}Disk Usage:{Style.RESET_ALL}")
            print(f"Current: {disk_percent[-1]:.1f}%")
            print(f"Average: {sum(disk_percent) / len(disk_percent):.1f}%")
            print(f"Minimum: {min(disk_percent):.1f}%")
            print(f"Maximum: {max(disk_percent):.1f}%")
            
            # Print network statistics
            print(f"\n{Fore.YELLOW}Network I/O:{Style.RESET_ALL}")
            print(f"Bytes Sent:")
            print(f"  Current: {network_sent[-1]}")
            print(f"  Average: {sum(network_sent) / len(network_sent):.0f}")
            print(f"  Maximum: {max(network_sent)}")
            print(f"Bytes Received:")
            print(f"  Current: {network_recv[-1]}")
            print(f"  Average: {sum(network_recv) / len(network_recv):.0f}")
            print(f"  Maximum: {max(network_recv)}")
            
            # Print process statistics
            print(f"\n{Fore.YELLOW}Process Count:{Style.RESET_ALL}")
            print(f"Current: {process_count[-1]}")
            print(f"Average: {sum(process_count) / len(process_count):.0f}")
            print(f"Minimum: {min(process_count)}")
            print(f"Maximum: {max(process_count)}")
            
            print()
        except Exception as e:
            logging.error(f"Error printing resource stats: {e}")
            
    def print_alert_stats(self):
        """Print alert statistics"""
        try:
            if not self.alerts:
                print(f"\n{Fore.RED}No alerts available{Style.RESET_ALL}\n")
                return
                
            print(f"\n{Fore.CYAN}Alert Statistics{Style.RESET_ALL}")
            
            # Calculate statistics
            resources = {}
            for alert in self.alerts:
                resource = alert['resource']
                if resource not in resources:
                    resources[resource] = []
                resources[resource].append(alert)
                
            # Print statistics
            for resource, alerts in resources.items():
                print(f"\n{Fore.YELLOW}{resource}:{Style.RESET_ALL}")
                print(f"Total Alerts: {len(alerts)}")
                print(f"Latest Alert: {time.ctime(alerts[-1]['timestamp'])}")
                print(f"Latest Value: {alerts[-1]['value']:.1f}")
                print(f"Threshold: {alerts[-1]['threshold']:.1f}")
                
            print()
        except Exception as e:
            logging.error(f"Error printing alert stats: {e}")
            
    def get_config_directory(self) -> Path:
        """Get configuration directory"""
        return self.config_dir 