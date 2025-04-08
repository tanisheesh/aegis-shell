# utils/gui_download_support.py - Enhanced version for GUI

import sys
import threading
import tkinter as tk
from queue import Queue
from tkinter import ttk

class GuiProgressUpdater:
    """A class to handle download progress updates in the GUI version of AegisShell"""
    
    def __init__(self, output_area):
        self.output_area = output_area
        self.original_stdout = sys.stdout
        self.progress_text = ""
        self.last_line = ""
        self.buffer = Queue()
        self.running = True
        
        # Start update thread
        threading.Thread(target=self._update_gui, daemon=True).start()
        
    def _update_gui(self):
        """Update GUI from buffer"""
        while self.running:
            try:
                text, is_progress = self.buffer.get(timeout=0.1)
                
                self.output_area.config(state=tk.NORMAL)
                
                if is_progress:
                    # Find the last line and replace it
                    last_line_index = self.output_area.index("end-1c linestart")
                    if self.progress_text:  # If we've already started a progress line
                        self.output_area.delete(last_line_index, "end-1c")
                    
                    # Write the updated line
                    self.output_area.insert("end-1c", text)
                    self.progress_text = text
                else:
                    # For normal text, just write it
                    self.output_area.insert(tk.END, text)
                    self.progress_text = ""  # Reset progress text when a new line is written
                
                self.output_area.see(tk.END)
                self.output_area.config(state=tk.DISABLED)
            except:
                continue
    
    def write(self, text):
        """Handle writing to ensure progress updates work in GUI"""
        # If text starts with a carriage return, it's a progress update
        is_progress = text.startswith('\r')
        if is_progress:
            text = text[1:]  # Remove the carriage return
            
        # Write to original stdout too
        self.original_stdout.write(text)
        
        # Add to buffer for GUI update
        self.buffer.put((text, is_progress))
            
    def flush(self):
        """Required for any stdout replacement"""
        self.original_stdout.flush()
        
    def stop(self):
        """Stop the update thread"""
        self.running = False
        
def redirect_stdout_for_gui(output_area):
    """Redirect stdout to handle progress updates in GUI"""
    sys.stdout = GuiProgressUpdater(output_area)
    
def restore_stdout():
    """Restore the original stdout"""
    if hasattr(sys.stdout, 'original_stdout'):
        sys.stdout = sys.stdout.original_stdout

# Progress bar widget for the GUI
class DownloadProgressBar(tk.Frame):
    def __init__(self, master, package_name, installer, **kwargs):
        super().__init__(master, **kwargs)
        self.package_name = package_name
        self.installer = installer
        
        # Create progress bar widget
        self.label = tk.Label(self, text=f"Installing {package_name} via {installer}")
        self.label.pack(side=tk.TOP, fill=tk.X)
        
        self.progress = ttk.Progressbar(self, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        self.status = tk.Label(self, text="Starting...")
        self.status.pack(side=tk.TOP, fill=tk.X)
        
    def update_progress(self, value):
        """Update progress bar value (0-100)"""
        self.progress["value"] = value
        percentage = int(value)
        self.status.config(text=f"Progress: {percentage}%")
        self.update_idletasks()
        
    def complete(self, success=True):
        """Mark as complete"""
        if success:
            self.progress["value"] = 100
            self.status.config(text="Installation complete!")
        else:
            self.status.config(text="Installation failed!")