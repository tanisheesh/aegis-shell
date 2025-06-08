import os
import sys
import json
import time
import logging
import unittest
import subprocess
import psutil
from typing import Dict, List, Optional, Any, Union, Callable
from pathlib import Path
from colorama import Fore, Style, init

class TestRunner:
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir) if config_dir else Path.home() / '.aegis' / 'tests'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._setup_logging()
        self.test_results = {}
        self.performance_results = {}
        self.debug_info = {}
        init()  # Initialize colorama
        
    def _setup_logging(self):
        """Setup logging configuration"""
        log_dir = self.config_dir / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / 'test.log'
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
    def run_tests(self, test_dir: str = 'tests'):
        """Run tests in specified directory"""
        try:
            # Discover and run tests
            loader = unittest.TestLoader()
            start_dir = Path(test_dir)
            suite = loader.discover(start_dir, pattern='test_*.py')
            
            # Run tests
            runner = unittest.TextTestRunner(verbosity=2)
            result = runner.run(suite)
            
            # Save results
            self.test_results = {
                'timestamp': time.time(),
                'tests_run': result.testsRun,
                'failures': len(result.failures),
                'errors': len(result.errors),
                'skipped': len(result.skipped),
                'success': result.wasSuccessful()
            }
            
            # Save detailed results
            if result.failures:
                self.test_results['failure_details'] = [
                    {
                        'test': str(f[0]),
                        'message': str(f[1])
                    }
                    for f in result.failures
                ]
                
            if result.errors:
                self.test_results['error_details'] = [
                    {
                        'test': str(e[0]),
                        'message': str(e[1])
                    }
                    for e in result.errors
                ]
                
            # Save results to file
            self._save_test_results()
            
            # Print summary
            self._print_test_summary()
            
            return self.test_results
        except Exception as e:
            logging.error(f"Error running tests: {e}")
            return None
            
    def run_performance_test(self, command: str, iterations: int = 5, timeout: int = 30):
        """Run performance test on command"""
        try:
            results = []
            
            for i in range(iterations):
                # Run command
                start_time = time.time()
                process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                # Monitor process
                cpu_percent = []
                memory_percent = []
                
                while process.poll() is None:
                    if time.time() - start_time > timeout:
                        process.kill()
                        break
                        
                    try:
                        p = psutil.Process(process.pid)
                        cpu_percent.append(p.cpu_percent())
                        memory_percent.append(p.memory_percent())
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        break
                        
                    time.sleep(0.1)
                    
                # Get output
                stdout, stderr = process.communicate()
                end_time = time.time()
                
                # Calculate metrics
                duration = end_time - start_time
                avg_cpu = sum(cpu_percent) / len(cpu_percent) if cpu_percent else 0
                avg_memory = sum(memory_percent) / len(memory_percent) if memory_percent else 0
                
                results.append({
                    'iteration': i + 1,
                    'duration': duration,
                    'cpu_percent': avg_cpu,
                    'memory_percent': avg_memory,
                    'exit_code': process.returncode,
                    'stdout': stdout.decode() if stdout else '',
                    'stderr': stderr.decode() if stderr else ''
                })
                
            # Calculate statistics
            durations = [r['duration'] for r in results]
            cpu_percents = [r['cpu_percent'] for r in results]
            memory_percents = [r['memory_percent'] for r in results]
            
            self.performance_results = {
                'timestamp': time.time(),
                'command': command,
                'iterations': iterations,
                'timeout': timeout,
                'results': results,
                'statistics': {
                    'duration': {
                        'min': min(durations),
                        'max': max(durations),
                        'avg': sum(durations) / len(durations)
                    },
                    'cpu_percent': {
                        'min': min(cpu_percents),
                        'max': max(cpu_percents),
                        'avg': sum(cpu_percents) / len(cpu_percents)
                    },
                    'memory_percent': {
                        'min': min(memory_percents),
                        'max': max(memory_percents),
                        'avg': sum(memory_percents) / len(memory_percents)
                    }
                }
            }
            
            # Save results to file
            self._save_performance_results()
            
            # Print summary
            self._print_performance_summary()
            
            return self.performance_results
        except Exception as e:
            logging.error(f"Error running performance test: {e}")
            return None
            
    def debug_command(self, command: str, timeout: int = 30):
        """Debug command execution"""
        try:
            # Run command
            start_time = time.time()
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Monitor process
            cpu_percent = []
            memory_percent = []
            io_counters = []
            
            while process.poll() is None:
                if time.time() - start_time > timeout:
                    process.kill()
                    break
                    
                try:
                    p = psutil.Process(process.pid)
                    cpu_percent.append(p.cpu_percent())
                    memory_percent.append(p.memory_percent())
                    io_counters.append(p.io_counters())
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    break
                    
                time.sleep(0.1)
                
            # Get output
            stdout, stderr = process.communicate()
            end_time = time.time()
            
            # Calculate metrics
            duration = end_time - start_time
            avg_cpu = sum(cpu_percent) / len(cpu_percent) if cpu_percent else 0
            avg_memory = sum(memory_percent) / len(memory_percent) if memory_percent else 0
            
            # Calculate I/O statistics
            if io_counters:
                read_bytes = io_counters[-1].read_bytes - io_counters[0].read_bytes
                write_bytes = io_counters[-1].write_bytes - io_counters[0].write_bytes
                read_count = io_counters[-1].read_count - io_counters[0].read_count
                write_count = io_counters[-1].write_count - io_counters[0].write_count
            else:
                read_bytes = write_bytes = read_count = write_count = 0
                
            self.debug_info = {
                'timestamp': time.time(),
                'command': command,
                'duration': duration,
                'exit_code': process.returncode,
                'stdout': stdout.decode() if stdout else '',
                'stderr': stderr.decode() if stderr else '',
                'resource_usage': {
                    'cpu_percent': {
                        'min': min(cpu_percent) if cpu_percent else 0,
                        'max': max(cpu_percent) if cpu_percent else 0,
                        'avg': avg_cpu
                    },
                    'memory_percent': {
                        'min': min(memory_percent) if memory_percent else 0,
                        'max': max(memory_percent) if memory_percent else 0,
                        'avg': avg_memory
                    },
                    'io': {
                        'read_bytes': read_bytes,
                        'write_bytes': write_bytes,
                        'read_count': read_count,
                        'write_count': write_count
                    }
                }
            }
            
            # Save results to file
            self._save_debug_info()
            
            # Print summary
            self._print_debug_summary()
            
            return self.debug_info
        except Exception as e:
            logging.error(f"Error debugging command: {e}")
            return None
            
    def _save_test_results(self):
        """Save test results to file"""
        try:
            results_file = self.config_dir / 'test_results.json'
            with open(results_file, 'w') as f:
                json.dump(self.test_results, f, indent=4)
        except Exception as e:
            logging.error(f"Error saving test results: {e}")
            
    def _save_performance_results(self):
        """Save performance results to file"""
        try:
            results_file = self.config_dir / 'performance_results.json'
            with open(results_file, 'w') as f:
                json.dump(self.performance_results, f, indent=4)
        except Exception as e:
            logging.error(f"Error saving performance results: {e}")
            
    def _save_debug_info(self):
        """Save debug info to file"""
        try:
            info_file = self.config_dir / 'debug_info.json'
            with open(info_file, 'w') as f:
                json.dump(self.debug_info, f, indent=4)
        except Exception as e:
            logging.error(f"Error saving debug info: {e}")
            
    def _print_test_summary(self):
        """Print test summary"""
        try:
            print(f"\n{Fore.CYAN}Test Summary{Style.RESET_ALL}")
            print(f"\nTests Run: {self.test_results['tests_run']}")
            print(f"Failures: {self.test_results['failures']}")
            print(f"Errors: {self.test_results['errors']}")
            print(f"Skipped: {self.test_results['skipped']}")
            print(f"Success: {self.test_results['success']}")
            
            if self.test_results.get('failure_details'):
                print(f"\n{Fore.RED}Failures:{Style.RESET_ALL}")
                for f in self.test_results['failure_details']:
                    print(f"\nTest: {f['test']}")
                    print(f"Message: {f['message']}")
                    
            if self.test_results.get('error_details'):
                print(f"\n{Fore.RED}Errors:{Style.RESET_ALL}")
                for e in self.test_results['error_details']:
                    print(f"\nTest: {e['test']}")
                    print(f"Message: {e['message']}")
        except Exception as e:
            logging.error(f"Error printing test summary: {e}")
            
    def _print_performance_summary(self):
        """Print performance summary"""
        try:
            print(f"\n{Fore.CYAN}Performance Summary{Style.RESET_ALL}")
            print(f"\nCommand: {self.performance_results['command']}")
            print(f"Iterations: {self.performance_results['iterations']}")
            
            stats = self.performance_results['statistics']
            print(f"\nDuration (seconds):")
            print(f"  Min: {stats['duration']['min']:.2f}")
            print(f"  Max: {stats['duration']['max']:.2f}")
            print(f"  Avg: {stats['duration']['avg']:.2f}")
            
            print(f"\nCPU Usage (%):")
            print(f"  Min: {stats['cpu_percent']['min']:.2f}")
            print(f"  Max: {stats['cpu_percent']['max']:.2f}")
            print(f"  Avg: {stats['cpu_percent']['avg']:.2f}")
            
            print(f"\nMemory Usage (%):")
            print(f"  Min: {stats['memory_percent']['min']:.2f}")
            print(f"  Max: {stats['memory_percent']['max']:.2f}")
            print(f"  Avg: {stats['memory_percent']['avg']:.2f}")
        except Exception as e:
            logging.error(f"Error printing performance summary: {e}")
            
    def _print_debug_summary(self):
        """Print debug summary"""
        try:
            print(f"\n{Fore.CYAN}Debug Summary{Style.RESET_ALL}")
            print(f"\nCommand: {self.debug_info['command']}")
            print(f"Duration: {self.debug_info['duration']:.2f} seconds")
            print(f"Exit Code: {self.debug_info['exit_code']}")
            
            if self.debug_info['stderr']:
                print(f"\n{Fore.RED}Error Output:{Style.RESET_ALL}")
                print(self.debug_info['stderr'])
                
            usage = self.debug_info['resource_usage']
            print(f"\nCPU Usage (%):")
            print(f"  Min: {usage['cpu_percent']['min']:.2f}")
            print(f"  Max: {usage['cpu_percent']['max']:.2f}")
            print(f"  Avg: {usage['cpu_percent']['avg']:.2f}")
            
            print(f"\nMemory Usage (%):")
            print(f"  Min: {usage['memory_percent']['min']:.2f}")
            print(f"  Max: {usage['memory_percent']['max']:.2f}")
            print(f"  Avg: {usage['memory_percent']['avg']:.2f}")
            
            print(f"\nI/O Statistics:")
            print(f"  Read: {usage['io']['read_bytes']} bytes ({usage['io']['read_count']} operations)")
            print(f"  Write: {usage['io']['write_bytes']} bytes ({usage['io']['write_count']} operations)")
        except Exception as e:
            logging.error(f"Error printing debug summary: {e}")
            
    def get_config_directory(self) -> Path:
        """Get configuration directory"""
        return self.config_dir 