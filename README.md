# <img src="https://img.shields.io/badge/%F0%9F%9B%A1%EF%B8%8F-Aegis%20Shell-blue?style=for-the-badge" alt="Aegis Shell" />

<div align="center">
  
![Version](https://img.shields.io/badge/version-1.0.0-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-orange)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

</div>

<p align="center">
  <img src="https://raw.githubusercontent.com/username/aegis-shell/main/resources/aegis_logo.png" alt="Aegis Shell Logo" width="250"/>
</p>

<div align="center">
  <h3>🛡️ The AI-Powered Developer Command Center 🛡️</h3>
  <p><i>Made with ❤️ by Tanish, Nidhi & Nishant</i></p>
</div>

---

## 📖 Overview

**Aegis Shell** is an intelligent terminal companion that transforms your development workflow by eliminating the friction between you and your tools. Stop wasting time on package installation errors, environment configurations, and researching CLI commands. Aegis Shell detects what's missing and handles it for you, keeping you in your creative flow.

<div align="center">
<img src="https://img.shields.io/badge/🚀%20Streamlined%20Development-6C5CE7?style=for-the-badge" alt="Streamlined Development" />
<img src="https://img.shields.io/badge/🤖%20AI%20Assistant-00B894?style=for-the-badge" alt="AI Assistant" />
<img src="https://img.shields.io/badge/⚡%20Cross%20Platform-FF7675?style=for-the-badge" alt="Cross Platform" />
</div>

---

## ✨ Key Features

### 🔍 Smart Command Detection
- **Automatic Tool Recognition:** Identifies when commands aren't installed on your system
- **Instant Installation Offers:** Provides one-click solutions to install missing tools
- **Cross-Platform Compatibility:** Works with the appropriate package manager for your OS

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

1. Download the latest installer from the [Releases](https://github.com/tanishpoddar/aegis-shell/releases) page
2. Run the installer and follow the on-screen instructions
3. The installer will:
   - Install required dependencies
   - Copy files to the installation directory
   - Add Aegis Shell to your system PATH
   - Create desktop and start menu shortcuts
   - Guide you through first-time setup

### Mac

1. Download the latest Mac package from the [Releases](https://github.com/tanishpoddar/aegis-shell/releases) page
2. Extract the zip file
3. Run the AegisShell executable
4. Follow the first-time setup instructions

### Building from Source

### Windows Build

1. Clone the repository:
   ```bash
   git clone https://github.com/tanishpoddar/aegis-shell.git
   cd aegis-shell
   ```

2. Run the build script:
   ```bash
   python setup.py
   ```

3. The Windows installer will be created as `AegisShell-Windows.zip` in the root directory

### Mac Build

1. Clone the repository:
   ```bash
   git clone https://github.com/tanishpoddar/aegis-shell.git
   cd aegis-shell
   ```

2. Make the build script executable:
   ```bash
   chmod +x build_mac.sh
   ```

3. Run the build script:
   ```bash
   ./build_mac.sh
   ```

4. The Mac package will be created as `AegisShell-Mac.zip` in the root directory

---

## 🚀 Getting Started

### First-Time Setup

When you first run Aegis Shell, you'll be prompted to:

1. Select an OpenRouter model
2. Enter your OpenRouter API key

Your API key will be securely stored and encrypted on your system.

### Using Aegis Shell

```bash
# Basic command usage (just like a regular terminal)
$ aegis-shell ls -la
$ aegis-shell python script.py
$ aegis-shell npm start

# When you use an unknown tool, Aegis offers to install it
$ aegis-shell flutter --version
[Aegis] 'flutter' not found on your system. Installation command: winget install Flutter.Flutter
Do you want to install it? [y/N]: y
[Aegis] Installing flutter via winget [██████████] 100%
[Aegis] Successfully installed flutter!
[Aegis] Now executing your original command.

# AI assistance for truly unknown commands
$ aegis-shell someobscuretool
[Aegis] Unknown command: 'someobscuretool'
[Aegis] Would you like me to ask the AI for help? [y/N]: y
[LLM AI Response]:
Based on analysis, 'someobscuretool' might be a data analysis CLI tool. 
To install it, run: pip install someobscuretool
```

---

## 🔧 Technical Architecture

<div align="center">
  <img src="https://mermaid.ink/img/pako:eNp1kk1vgzAMhv9K5NOmVYKVj7XVtNOkSdM0aYcddvESA9EIRCTptFL_-0IoW7utexi_fmzHiV_AqDggJHAWM9MV1YY1FdNkKiuYnkG29jQTIvvYC0NnI1ltnYW9dUdPSF2Jag2zhN_X8Gm1MiU3DXwIoyWrMUZUVUO-WL9b64gqXzAn9u5lDvF7nKSLNPb9l3g-X8RJnMz9aSz-0Nzng03aE-aU3UmhrMaqxVLBJkGlUO0Iy6X7-SGwfYQVF4XJmLEpljWWWMF7ypwRXkiLrZBV1Y1hRfC5VLIzbT3pjJQVbHJWa8FlNfwzGEzzgRpK5USFVx1nX6kx7CKOFnXLNEXlWUKO07LqJlwR7jvgGhj9dpz8ZtFfW6EuPe33J0_TCnYFfbVj3SPTsEn3lUzXcZqmmzR93qTbaBE_xUm8_LNJ6EJ_AfSXvdo?type=png" alt="Aegis Shell Architecture" width="600"/>
</div>

Aegis Shell consists of several key components:

1. **Core Terminal Interface**: Built with Python and prompt_toolkit for advanced auto-completion
2. **Command Handler**: Detects, parses, and routes commands appropriately 
3. **LLM AI Integration**: Connects to OpenRouter API for AI assistance on unknown commands
4. **Package Manager Integrations**: Interfaces with various package managers across platforms
5. **Configuration System**: Manages user preferences and command mappings

---

## 📋 Command Reference

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