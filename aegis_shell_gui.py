import os
import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
from pathlib import Path
import json
import subprocess
import importlib

# Custom imports - make sure these paths work with the GUI application
# Add parent directory to path to ensure modules can be imported
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Try to import required modules
try:
    from commands.command_handler import handle_command
    from config_loader import load_command_mappings, load_config
    from utils.permissions import check_admin_rights
    from utils.gui_download_support import redirect_stdout_for_gui, restore_stdout
except ImportError as e:
    print(f"Error importing modules: {e}")
    
# Define paths
BASE_DIR = Path(__file__).resolve().parent
RESOURCE_DIR = BASE_DIR / "resources"
CONFIG_DIR = BASE_DIR / "config"
COMMAND_MAPPINGS_FILE = CONFIG_DIR / "commands_mapping.json"

class RedirectedOutput:
    """Redirect stdout/stderr to the GUI"""
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.buffer = queue.Queue()
        self.original_stdout = sys.stdout
        self.running = True
        
        # Start thread to handle output
        threading.Thread(target=self._output_reader, daemon=True).start()
    
    def write(self, text):
        self.buffer.put(text)
        self.original_stdout.write(text)
        
    def flush(self):
        self.original_stdout.flush()
        
    def _output_reader(self):
        """Read from buffer and update text widget"""
        while self.running:
            try:
                text = self.buffer.get(timeout=0.1)
                self.text_widget.configure(state=tk.NORMAL)
                self.text_widget.insert(tk.END, text)
                self.text_widget.see(tk.END)
                self.text_widget.configure(state=tk.DISABLED)
                self.text_widget.update_idletasks()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error in output reader: {e}")

    def stop(self):
        self.running = False

class AegisShellGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Aegis Shell - AI-Powered Developer Terminal")
        self.geometry("900x600")
        self.minsize(800, 500)
        
        # Apply dark theme
        self.configure(bg='#121212')
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.apply_dark_theme()
        
        # Load configurations
        self.load_configs()
        
        # Set up the main UI
        self.setup_ui()
        
        # Set up redirected output
        self.redirector = RedirectedOutput(self.terminal)
        sys.stdout = self.redirector
        sys.stderr = self.redirector
        
        # Initialize prompt mode flag (to handle y/n inputs correctly)
        self.in_prompt_mode = False
        self.current_prompt_handler = None
        
        # Welcome message
        self.show_welcome()
        
    def apply_dark_theme(self):
        """Apply dark theme to the entire UI"""
        # Configure colors
        bg_color = '#121212'
        fg_color = '#ffffff'
        accent_color = '#1e88e5'
        secondary_bg = '#1e1e1e'
        
        # Configure ttk styles
        self.style.configure('TFrame', background=bg_color)
        self.style.configure('TLabel', background=bg_color, foreground=fg_color)
        self.style.configure('TButton', background=secondary_bg, foreground=fg_color)
        self.style.configure('TEntry', fieldbackground=secondary_bg, foreground=fg_color)
        
        # Configure scrollbar colors
        self.style.configure('TScrollbar', background=secondary_bg, troughcolor=bg_color, 
                            arrowcolor=fg_color, bordercolor=secondary_bg)
    
    def load_configs(self):
        """Load configurations and command mappings"""
        try:
            self.mappings = load_command_mappings()
            self.config = load_config()
            print(f"Loaded {len(self.mappings)} command mappings")
        except Exception as e:
            print(f"Error loading configurations: {e}")
            self.mappings = {}
            self.config = {}
            
        # Add FAQ command to mappings
        if "faq" not in self.mappings:
            self.mappings["faq"] = {
                "language": "internal",
                "description": "Show frequently asked questions"
            }
    
    def setup_ui(self):
        """Set up the user interface"""
        # Create frame for toolbar with minimal options (dark mode)
        toolbar_frame = ttk.Frame(self)
        toolbar_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Create only essential buttons (removed Python, npm, Git)
        ttk.Button(toolbar_frame, text="📋 FAQ", command=self.show_faq).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="🧹 Clear", command=self.clear_terminal).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="⚙️ Settings", command=self.show_settings).pack(side=tk.LEFT, padx=2)
        
        # Main terminal area
        terminal_frame = ttk.Frame(self)
        terminal_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Terminal output area with larger font and dark colors
        self.terminal = scrolledtext.ScrolledText(terminal_frame, wrap=tk.WORD, 
                                               bg='#121212', fg='#ffffff',
                                               insertbackground='#ffffff',
                                               font=('Consolas', 12))  # Increased font size
        self.terminal.pack(fill=tk.BOTH, expand=True)
        self.terminal.configure(state=tk.DISABLED)
        
        # Command entry area
        entry_frame = ttk.Frame(self)
        entry_frame.pack(fill=tk.X, padx=5, pady=5)
        
        prompt_label = ttk.Label(entry_frame, text="$ aegis-shell")
        prompt_label.pack(side=tk.LEFT)
        
        self.command_entry = ttk.Entry(entry_frame, font=('Consolas', 12))  # Increased font size
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.command_entry.bind("<Return>", self.on_command_enter)
        self.command_entry.focus_set()
        
        # Special buttons for yes/no prompts (initially hidden)
        self.prompt_frame = ttk.Frame(entry_frame)
        self.prompt_frame.pack(side=tk.RIGHT)
        self.prompt_frame.pack_forget()  # Hide initially
        
        self.yes_button = ttk.Button(self.prompt_frame, text="Yes", command=lambda: self.handle_prompt_response('y'))
        self.yes_button.pack(side=tk.LEFT, padx=2)
        
        self.no_button = ttk.Button(self.prompt_frame, text="No", command=lambda: self.handle_prompt_response('n'))
        self.no_button.pack(side=tk.LEFT, padx=2)
        
        # Run button with dark styling
        run_button = ttk.Button(entry_frame, text="Run", command=self.on_run_button)
        run_button.pack(side=tk.RIGHT)
        
        # Set up auto-completion
        self.setup_autocomplete()
        
        # Status bar with dark styling
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Check admin rights
        if not check_admin_rights():
            self.status_var.set("Warning: Not running with admin rights. Some operations may fail.")
    
    def setup_autocomplete(self):
        """Set up command auto-completion"""
        # This is a simplified autocomplete - in a real app you'd want more advanced handling
        self.command_options = list(self.mappings.keys())
        
        def autocomplete(event):
            # Get text up to cursor position
            text = self.command_entry.get()
            if text and ' ' not in text:  # Only complete the first word
                matches = [cmd for cmd in self.command_options if cmd.startswith(text)]
                if len(matches) == 1:
                    self.command_entry.delete(0, tk.END)
                    self.command_entry.insert(0, matches[0] + " ")
                    return "break"
                elif len(matches) > 1:
                    # Show matches in terminal
                    self.terminal.configure(state=tk.NORMAL)
                    self.terminal.insert(tk.END, "\nPossible commands: " + ", ".join(matches) + "\n")
                    self.terminal.see(tk.END)
                    self.terminal.configure(state=tk.DISABLED)
            return None
        
        self.command_entry.bind("<Tab>", autocomplete)
    
    def show_welcome(self):
        """Display the welcome message and ASCII art"""
        self.terminal.configure(state=tk.NORMAL)
        
        # Try to load ASCII art
        try:
            art_path = RESOURCE_DIR / "ascii_art.txt"
            if art_path.exists():
                with open(art_path, "r") as f:
                    art = f.read()
                self.terminal.insert(tk.END, art + "\n", "cyan")
            else:
                self.terminal.insert(tk.END, "ASCII art file not found\n", "red")
        except Exception as e:
            self.terminal.insert(tk.END, f"Error loading ASCII art: {e}\n", "red")
        
        # Welcome messages
        self.terminal.insert(tk.END, "Welcome to the ultimate AI-powered terminal shell.\n", "cyan")
        self.terminal.insert(tk.END, "Made with ❤️  by Tanish, Nidhi & Nishant\n", "magenta")
        self.terminal.insert(tk.END, "Type 'exit' to quit. Type 'faq' for help.\n\n", "yellow")
        
        self.terminal.configure(state=tk.DISABLED)
    
    def on_command_enter(self, event=None):
        """Handle command entry - check for prompt mode first"""
        command = self.command_entry.get().strip()
        if not command:
            return
        
        self.command_entry.delete(0, tk.END)
        
        # If we're in prompt mode, don't interpret as a command
        if self.in_prompt_mode:
            self.handle_prompt_response(command)
        else:
            self.run_command(command)
    
    def handle_prompt_response(self, response):
        """Handle a response to a y/n prompt"""
        # Log the response in the terminal
        self.terminal.configure(state=tk.NORMAL)
        self.terminal.insert(tk.END, f"{response}\n")
        self.terminal.configure(state=tk.DISABLED)
        self.terminal.see(tk.END)
        
        # Exit prompt mode
        self.exit_prompt_mode()
        
        # Pass the response to stdin
        if self.current_prompt_handler:
            self.current_prompt_handler(response)
            self.current_prompt_handler = None
    
    def enter_prompt_mode(self, callback=None):
        """Enter prompt mode (waiting for y/n)"""
        self.in_prompt_mode = True
        self.current_prompt_handler = callback
        self.prompt_frame.pack(side=tk.RIGHT)
        self.command_entry.delete(0, tk.END)
        self.command_entry.focus_set()
    
    def exit_prompt_mode(self):
        """Exit prompt mode"""
        self.in_prompt_mode = False
        self.prompt_frame.pack_forget()
    
    def on_run_button(self):
        """Handle Run button click"""
        self.on_command_enter()
    
    def run_command(self, command):
        """Execute a command"""
        self.terminal.configure(state=tk.NORMAL)
        self.terminal.insert(tk.END, f"\n$ aegis-shell {command}\n", "prompt")
        self.terminal.configure(state=tk.DISABLED)
        self.terminal.see(tk.END)
        
        if command.lower() == "exit":
            self.terminal.configure(state=tk.NORMAL)
            self.terminal.insert(tk.END, "[Aegis] Goodbye, warrior! 🛡️\n", "cyan")
            self.terminal.configure(state=tk.DISABLED)
            self.after(1000, self.destroy)
            return
        
        if command.lower() == "clear":
            self.clear_terminal()
            return
            
        if command.lower() == "faq":
            self.show_faq()
            return
            
        # Run command in separate thread to keep UI responsive
        threading.Thread(target=self._execute_command, args=(command,), daemon=True).start()
    
    def _execute_command(self, command):
        """Execute command in background thread"""
        try:
            self.status_var.set(f"Executing: {command}")
            
            # Override stdin to capture y/n responses
            orig_stdin = sys.stdin
            
            # Create a custom stdin that will wait for responses
            class CustomStdin:
                def __init__(self, gui):
                    self.gui = gui
                    self.response_queue = queue.Queue()
                
                def readline(self):
                    # Show prompt UI
                    self.gui.after(0, lambda: self.gui.enter_prompt_mode(
                        lambda response: self.response_queue.put(response + '\n')
                    ))
                    
                    # Wait for response
                    response = self.response_queue.get()
                    return response
            
            # Override stdin
            sys.stdin = CustomStdin(self)
            
            # Execute command
            handle_command(command, self.mappings, self.config)
            
            # Restore stdin
            sys.stdin = orig_stdin
            
            # Make sure we exit prompt mode
            self.after(0, self.exit_prompt_mode)
            
            self.status_var.set("Ready")
        except Exception as e:
            self.terminal.configure(state=tk.NORMAL)
            self.terminal.insert(tk.END, f"[Aegis] Error: {e}\n", "error")
            self.terminal.configure(state=tk.DISABLED)
            self.status_var.set("Error occurred")
            
            # Make sure we exit prompt mode
            self.after(0, self.exit_prompt_mode)
    
    def show_faq(self):
        """Show the FAQ content"""
        try:
            from commands.faq import show_faq
            show_faq()
        except ImportError:
            self.terminal.configure(state=tk.NORMAL)
            self.terminal.insert(tk.END, "FAQ module not found!\n", "error")
            self.terminal.configure(state=tk.DISABLED)
    
    def clear_terminal(self):
        """Clear the terminal content"""
        self.terminal.configure(state=tk.NORMAL)
        self.terminal.delete(1.0, tk.END)
        self.terminal.configure(state=tk.DISABLED)
    
    def show_settings(self):
        """Show settings dialog"""
        settings_window = tk.Toplevel(self)
        settings_window.title("Aegis Shell Settings")
        settings_window.geometry("500x400")
        settings_window.transient(self)
        settings_window.grab_set()
        
        # Apply dark theme to settings window
        settings_window.configure(bg='#121212')
        
        notebook = ttk.Notebook(settings_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # General settings tab
        general_tab = ttk.Frame(notebook)
        notebook.add(general_tab, text="General")
        
        ttk.Label(general_tab, text="Default Language:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        lang_var = tk.StringVar(value=self.config.get("default_language", "python"))
        lang_combo = ttk.Combobox(general_tab, textvariable=lang_var, 
                                  values=["python", "javascript", "system"])
        lang_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Font size setting
        ttk.Label(general_tab, text="Terminal Font Size:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        font_size_var = tk.StringVar(value="12")
        font_size_combo = ttk.Combobox(general_tab, textvariable=font_size_var, 
                                       values=["10", "11", "12", "14", "16", "18"])
        font_size_combo.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Apply font size button
        ttk.Button(general_tab, text="Apply Font Size", 
                   command=lambda: self.apply_font_size(int(font_size_var.get()))).grid(
            row=1, column=2, padx=5, pady=5)
        
        ttk.Button(general_tab, text="Save", 
                   command=lambda: self.save_settings({
                       "default_language": lang_var.get(),
                       "font_size": font_size_var.get()
                   })).grid(
            row=10, column=0, columnspan=2, pady=20)
        
        # Commands tab
        commands_tab = ttk.Frame(notebook)
        notebook.add(commands_tab, text="Commands")
        
        # Command list display
        ttk.Label(commands_tab, text="Available Commands:").pack(anchor=tk.W, padx=5, pady=5)
        
        cmd_frame = ttk.Frame(commands_tab)
        cmd_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create treeview with dark theme
        columns = ("Command", "Language", "Install Method")
        cmd_tree = ttk.Treeview(cmd_frame, columns=columns, show="headings")
        
        # Configure columns
        for col in columns:
            cmd_tree.heading(col, text=col)
            cmd_tree.column(col, width=150)
            
        # Add scrollbar
        scrollbar = ttk.Scrollbar(cmd_frame, orient=tk.VERTICAL, command=cmd_tree.yview)
        cmd_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        cmd_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Populate treeview
        for command, details in self.mappings.items():
            language = details.get("language", "system")
            install_cmd = details.get("install_cmd", "N/A")
            cmd_tree.insert("", tk.END, values=(command, language, install_cmd))
    
    def apply_font_size(self, size):
        """Change the terminal font size"""
        self.terminal.configure(font=('Consolas', size))
        self.command_entry.configure(font=('Consolas', size))
    
    def save_settings(self, settings):
        """Save settings to config file"""
        # Update config
        self.config.update(settings)
        
        # Save to file
        try:
            with open(CONFIG_DIR / "config.json", "w") as f:
                json.dump(self.config, f, indent=4)
            messagebox.showinfo("Settings", "Settings saved successfully!")
            
            # Apply font size if it was changed
            if "font_size" in settings:
                try:
                    self.apply_font_size(int(settings["font_size"]))
                except:
                    pass
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def on_close(self):
        """Handle application close"""
        # Restore stdout and stderr
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        
        # Stop the redirector thread
        if hasattr(self, 'redirector'):
            self.redirector.stop()
            
        self.destroy()

# Configure terminal text tags
def setup_text_tags(terminal):
    """Set up text tags for colored output"""
    terminal.tag_configure("cyan", foreground="#00FFFF")
    terminal.tag_configure("green", foreground="#00FF00")
    terminal.tag_configure("yellow", foreground="#FFFF00")
    terminal.tag_configure("magenta", foreground="#FF00FF")
    terminal.tag_configure("red", foreground="#FF0000")
    terminal.tag_configure("blue", foreground="#0000FF")
    terminal.tag_configure("prompt", foreground="#00FFFF")
    terminal.tag_configure("error", foreground="#FF0000")

# Main application entry point
if __name__ == "__main__":
    app = AegisShellGUI()
    
    # Set up text tags after the app is created
    setup_text_tags(app.terminal)
    
    # Handle proper cleanup on close
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    
    # Start the application
    app.mainloop()