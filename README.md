# <img src="https://img.shields.io/badge/%F0%9F%9B%A1%EF%B8%8F-Aegis%20Shell-blue?style=for-the-badge" alt="Aegis Shell" />

<div align="center">
  
![Version](https://img.shields.io/badge/version-1.0.0-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-orange)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

</div>

<div align="center">
  <h3>🛡️ The AI-Powered Developer Command Center 🛡️</h3>
</div>

## 📖 Overview

Aegis Shell is your intelligent terminal companion that streamlines development workflow by automatically managing tools and dependencies. It eliminates common development friction points by handling package installations, providing AI-powered assistance, and maintaining cross-platform compatibility.

## ✨ Key Features

### 🔍 Smart Command Detection
- Automatically identifies missing system tools
- Provides instant installation solutions
- Works with your OS's native package manager

### 🤖 AI-Powered Assistant
- **Unknown Command Analysis:** Intelligently identifies what tool you're trying to use
- **Smart Installation Suggestions:** Recommends the correct package and version
- **Context-Aware Responses:** Understands the developer's intent

### 🛠️ Multi-Environment Support
- **Cross-Platform:** Works seamlessly on Windows, macOS, and Linux
- **Multiple Package Managers:** Supports pip, npm, winget, apt, brew, and more
- **Smart Shell Switching:** Intelligently switches between CMD, PowerShell, and Bash

### 📦 Package Management
- **Auto-Detection:** Identifies the right package manager for each tool
- **Interactive Installation:** Shows real-time progress with beautiful progress bars
- **Post-Installation Execution:** Immediately runs your original command after installation

### 🔒 Secure & Personalized
- **User-Specific API Keys:** Each user maintains their own secure AI API key
- **Local Configuration:** Settings stored in the user's home directory
- **Permission Handling:** Detects and advises on admin privileges when needed

---

## 🖥️ Installation

<div align="center">
<img src="https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows" />
<img src="https://img.shields.io/badge/macOS-000000?style=for-the-badge&logo=apple&logoColor=white" alt="macOS" />
<img src="https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black" alt="Linux" />
</div>

### Windows

```powershell
# Option 1: Run the installer
AegisShell_Setup.exe

# Option 2: Extract the zip and run
Extract AegisShell.zip to any location
Run AegisShell.exe
```

### macOS / Linux

```bash
# Extract the zip
unzip AegisShell.zip -d /preferred/location

# Run the executable
cd /preferred/location/AegisShell
./AegisShell
```

### Building from Source

```bash
# Clone the repository
git clone https://github.com/username/aegis-shell.git
cd aegis-shell

# Install dependencies
pip install -r requirements.txt

# Run the setup script
python setup.py
```

---

## 🚀 Getting Started

### First-Time Setup

1. Launch Aegis Shell from your installation location
2. You'll see the welcome ASCII art and introduction
3. When you first use an AI feature, you'll be prompted to set up your API key:
   - Go to [OpenRouter Keys](https://openrouter.ai/keys)
   - Create a free account and generate an API key
   - Copy and paste the key when prompted

### Basic Usage

```bash
# Regular terminal commands
$ aegis-shell ls -la
$ aegis-shell python script.py

# Handling unknown tools
$ aegis-shell flutter --version
[Aegis] 'flutter' not found. Install? [y/N]: y
[Aegis] Installing flutter... [██████████] 100%
```

## 🔧 Technical Details

- Built with Python 3.8+
- Uses prompt_toolkit for terminal interface
- OpenRouter API integration for AI features
- Cross-platform package management
- Local configuration storage

## 📋 Available Commands

| Command | Description |
|---------|-------------|
| `faq` | Show frequently asked questions and help |
| `exit` | Exit the Aegis Shell |
| `any command` | Execute the command if available |
| `unknown command` | If not found, Aegis will offer to install or use AI to assist |

---

## 🏆 Advanced Features

### Custom Command Mappings

Aegis Shell automatically maintains a database of commands in `config/commands_mapping.json`. This file maps commands to their installation methods and can be extended with custom entries.

```json
{
  "flask": {
    "language": "python",
    "install_cmd": "pip install flask"
  }
}
```

### Cross-Platform Intelligence

When you try to use a Linux command on Windows (or vice versa), Aegis Shell automatically suggests the appropriate alternative:

```
$ aegis-shell apt install python3
[Aegis] 'apt' is a Linux package manager and isn't available on Windows.
[Aegis] On Windows, you can use alternatives like:
1. winget - Windows Package Manager
2. chocolatey - A package manager for Windows
[Aegis] Would you like to install one of these? (1/2/N):
```

---

## 🤝 Contributing

We welcome contributions to Aegis Shell! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add some amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/aegis-shell.git
cd aegis-shell

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dev dependencies
pip install -r requirements-dev.txt

# Run the application in development mode
python aegis_shell.py
```

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- Built with [prompt_toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit) for advanced terminal features
- AI capabilities powered by [OpenRouter](https://openrouter.ai)
- Package management inspired by various package managers' best practices
- Special thanks to all our contributors and early testers

---

<div align="center">
  <p>
    <a href="https://github.com/username/aegis-shell/issues">Report Bug</a> •
    <a href="https://github.com/username/aegis-shell/issues">Request Feature</a> •
    <a href="https://github.com/username/aegis-shell/wiki">Documentation</a>
  </p>
  <p>🛡️ <b>Aegis Shell</b> - Empowering developers, one command at a time 🛡️</p>
</div>