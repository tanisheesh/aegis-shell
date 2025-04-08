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
- Analyzes unknown commands
- Suggests correct packages and versions
- Provides context-aware assistance

### 🛠️ Cross-Platform Support
- Compatible with Windows, macOS, and Linux
- Supports major package managers (pip, npm, winget, apt, brew)
- Smart shell detection (CMD, PowerShell, Bash)

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/tanishpoddar/aegis-shell.git
cd aegis-shell

# Install dependencies
pip install -r requirements.txt

# Run setup
python setup.py
```

### First Time Setup

1. Launch Aegis Shell
2. When prompted, set up your OpenRouter API key:
   - Get your key from [OpenRouter](https://openrouter.ai/keys)
   - Enter the key when prompted

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
| `faq` | Show help and FAQ |
| `exit` | Exit Aegis Shell |
| `any command` | Execute if available |
| `unknown command` | Triggers AI assistance |

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [Report Bug](https://github.com/tanishpoddar/aegis-shell/issues)
- [Request Feature](https://github.com/tanishpoddar/aegis-shell/issues)
- [Documentation](https://github.com/tanishpoddar/aegis-shell/wiki)

---

<div align="center">
  <p>🛡️ <b>Aegis Shell</b> - Empowering developers, one command at a time 🛡️</p>
  <p>Last Updated: 2025-04-08</p>
</div>
```
