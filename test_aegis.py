#!/usr/bin/env python3
"""
Aegis Shell — Full Pipeline Execution Test
Every command is run through AegisShell exactly as a real user would type it.
Output is saved to test_output.txt.
Run:  python -X utf8 test_aegis.py
"""

import sys
import io
import os
import re
import platform
from pathlib import Path
from unittest.mock import patch
from colorama import init, Fore, Style

init()

# ── Tee: write to console AND capture to buffer ───────────────────────────────
_log_buf = io.StringIO()
_real_out = sys.stdout

class _Tee:
    def __init__(self, a, b): self._a, self._b = a, b
    def write(self, s): self._a.write(s); self._b.write(s)
    def flush(self): self._a.flush(); self._b.flush()
    def __getattr__(self, n): return getattr(self._a, n)

sys.stdout = _Tee(_real_out, _log_buf)
sys.path.insert(0, str(Path(__file__).parent))

IS_WINDOWS  = platform.system() == 'Windows'
CONFIG_FILE = Path.home() / '.aegis' / 'config.json'
HAS_CONFIG  = CONFIG_FILE.exists()

_BAR = '─' * 64
_SEC = '═' * 64
_I   = Fore.CYAN

def section(title):
    print(f'\n{_I}{_SEC}{Style.RESET_ALL}')
    print(f'{_I}  {title}{Style.RESET_ALL}')
    print(f'{_I}{_SEC}{Style.RESET_ALL}')

# ── Boot AegisShell ───────────────────────────────────────────────────────────
section('BOOT — starting AegisShell')
from aegis_shell import AegisShell

if not HAS_CONFIG:
    # No Groq config found: patch _first_time_setup so the test doesn't
    # hang waiting for interactive API key entry.
    def _headless_setup(self):
        self.model      = 'llama-3.3-70b-versatile'
        self.api_key    = ''
        self._tips_seen = []
    with patch.object(AegisShell, '_first_time_setup', _headless_setup):
        shell = AegisShell()
    print(f'{Fore.YELLOW}  No config — LLM commands will be skipped.{Style.RESET_ALL}')
else:
    shell = AegisShell()

print(f'{Fore.GREEN}AegisShell ready.  model={shell.model!r}{Style.RESET_ALL}')
print(f'{Fore.GREEN}executor={type(shell.command_executor).__name__}{Style.RESET_ALL}')

def run(cmd, mock_input=None):
    """
    Run cmd through the full aegis pipeline:
      _handle_builtin  →  alias expansion  →  LLM classify  →  execute
    Exactly what happens when a user types into the aegis prompt.
    """
    print(f'\n{_BAR}')
    print(f'$ {cmd}')
    print(_BAR)
    try:
        if mock_input is not None:
            with patch('builtins.input', return_value=mock_input):
                handled = shell._handle_builtin(cmd)
                if not handled:
                    shell._handle(cmd)
        else:
            handled = shell._handle_builtin(cmd)
            if not handled:
                shell._handle(cmd)
    except SystemExit:
        pass  # exit command — swallow so test continues
    except Exception as e:
        print(f'{Fore.RED}[EXCEPTION] {type(e).__name__}: {e}{Style.RESET_ALL}')

# ═════════════════════════════════════════════════════════════════════════════
section('1 · PowerShell Cmdlets')
# ═════════════════════════════════════════════════════════════════════════════
for cmd in [
    'Get-Date',
    'Get-Location',
    "Write-Host 'hello from aegis'",
    '$PSVersionTable.PSVersion',
    'Get-Process | Select-Object -First 5 Name, CPU',
    'Get-ChildItem -Path . -File | Select-Object -First 5 Name',
    'Test-Path C:\\Windows',
    "Get-Service | Where-Object {$_.Status -eq 'Running'} | Select-Object -First 5 Name",
    'Get-ComputerInfo | Select-Object WindowsVersion, OsArchitecture',
]:
    run(cmd)

# ═════════════════════════════════════════════════════════════════════════════
section('2 · CMD Builtins')
# ═════════════════════════════════════════════════════════════════════════════
for cmd in [
    'ver',
    'whoami',
    'hostname',
    'echo hello from aegis',
    'dir',
    'date /t',
    'time /t',
]:
    run(cmd)

# ═════════════════════════════════════════════════════════════════════════════
section('3 · Unix Commands  (aegis translates on Windows)')
# ═════════════════════════════════════════════════════════════════════════════
for cmd in ['ls', 'ls -la', 'pwd']:
    run(cmd)

run('touch _aegis_test.txt')
run('echo test_content > _aegis_test.txt')
run('cat _aegis_test.txt')
run('type _aegis_test.txt')
run('mkdir _aegis_test_dir')
run('rm _aegis_test.txt',     mock_input='y')
run('rmdir _aegis_test_dir',  mock_input='y')

# ═════════════════════════════════════════════════════════════════════════════
section('4 · Python / pip')
# ═════════════════════════════════════════════════════════════════════════════
for cmd in [
    'python --version',
    'python -c "import sys; print(sys.version)"',
    'python -c "import platform; print(platform.system(), platform.release())"',
    'python -c "print(2 + 2)"',
    'pip --version',
    'pip list',
    'pip show colorama',
    'pip show prompt_toolkit',
    'pip show cryptography',
    'pip check',
]:
    run(cmd)

# ═════════════════════════════════════════════════════════════════════════════
section('5 · Node / npm / npx')
# ═════════════════════════════════════════════════════════════════════════════
for cmd in [
    'node --version',
    'node -e "console.log(process.version)"',
    'node -e "console.log(1 + 1)"',
    'npm --version',
    'npx --version',
]:
    run(cmd)

# ═════════════════════════════════════════════════════════════════════════════
section('6 · Git Commands')
# ═════════════════════════════════════════════════════════════════════════════
for cmd in [
    'git --version',
    'git status',
    'git log --oneline -5',
    'git branch',
    'git diff --stat',
    'git remote -v',
    'git stash list',
    'git config user.name',
    'git config user.email',
]:
    run(cmd)

# ═════════════════════════════════════════════════════════════════════════════
section('7 · Git Aliases  (aegis expands → real git)')
# ═════════════════════════════════════════════════════════════════════════════
for cmd in ['gst', 'gp', 'gpl', 'glog', 'gd', 'gds', 'gb', 'gaa']:
    run(cmd)

# ═════════════════════════════════════════════════════════════════════════════
section('8 · Docker Aliases')
# ═════════════════════════════════════════════════════════════════════════════
for cmd in ['dps', 'dpsa', 'di']:
    run(cmd)

# ═════════════════════════════════════════════════════════════════════════════
section('9 · GitHub / Cloud Aliases')
# ═════════════════════════════════════════════════════════════════════════════
for cmd in ['prs', 'issues', 'aws-whoami', 'k8s-pods']:
    run(cmd)

# ═════════════════════════════════════════════════════════════════════════════
section('10 · Security — warnings and hard blocks')
# ═════════════════════════════════════════════════════════════════════════════
# Warn level — user confirms
run('rm -rf _nonexistent_aegis_dir',  mock_input='y')
run('del _nonexistent_aegis.txt',     mock_input='y')
# Warn level — user cancels
run('rm -rf _nonexistent_aegis_dir2', mock_input='n')
# Hard block — user cancels (NOT running format/shutdown for real)
run('format D:',         mock_input='N')
run('shutdown /s /t 999',mock_input='N')

# ═════════════════════════════════════════════════════════════════════════════
section('11 · Session Variables')
# ═════════════════════════════════════════════════════════════════════════════
run('$PORT = 8080')
run('$APP = myapp')
run('$ENV = production')
run('echo $PORT')
run('echo $APP')
run('echo $APP is on port $PORT env $ENV')
run('vars')
run('unset PORT')
run('vars')

# ═════════════════════════════════════════════════════════════════════════════
section('12 · Credential Manager')
# ═════════════════════════════════════════════════════════════════════════════
run('secret set AEGIS_TEST_KEY aegis_test_value_xyz_123')
run('secret list')
run('secret get AEGIS_TEST_KEY')
run('secret delete AEGIS_TEST_KEY')
run('secret list')

# ═════════════════════════════════════════════════════════════════════════════
section('13 · Themes')
# ═════════════════════════════════════════════════════════════════════════════
run('theme list')
for t in ['dark', 'hacker', 'light', 'minimal', 'ocean', 'default']:
    run(f'theme set {t}')

# ═════════════════════════════════════════════════════════════════════════════
section('14 · Macros')
# ═════════════════════════════════════════════════════════════════════════════
# Recording is triggered in the REPL loop, so we seed the recorder directly
shell.macro_recorder.start('aegis_test_macro')
shell.macro_recorder.record('python --version')
shell.macro_recorder.record('pip --version')
shell.macro_recorder.record('git --version')
shell.macro_recorder.stop()
print('  (macro "aegis_test_macro" seeded with 3 steps)')
run('macro list')
run('macro run aegis_test_macro')
run('macro delete aegis_test_macro')
run('macro list')

# ═════════════════════════════════════════════════════════════════════════════
section('15 · Session Recording')
# ═════════════════════════════════════════════════════════════════════════════
run('record start aegis_test_session')
run('python --version')
run('git --version')
run('record stop')

# ═════════════════════════════════════════════════════════════════════════════
section('16 · Analytics & Stats')
# ═════════════════════════════════════════════════════════════════════════════
run('analytics')
run('stats')

# ═════════════════════════════════════════════════════════════════════════════
section('17 · Learning — cheat sheets')
# ═════════════════════════════════════════════════════════════════════════════
run('cheat')  # list available cheat sheets
for topic in ['git', 'docker', 'pip', 'python', 'linux', 'powershell', 'aegis']:
    run(f'cheat {topic}')

# ═════════════════════════════════════════════════════════════════════════════
section('18 · Help')
# ═════════════════════════════════════════════════════════════════════════════
run('help')

# ═════════════════════════════════════════════════════════════════════════════
section('19 · System Dashboard')
# ═════════════════════════════════════════════════════════════════════════════
run('dashboard 3')  # 3-second run (default is 30)

# ═════════════════════════════════════════════════════════════════════════════
section('20 · Environment Detection')
# ═════════════════════════════════════════════════════════════════════════════
run('env')  # builtin: detect environment in cwd

# ═════════════════════════════════════════════════════════════════════════════
section('21 · SSH Profiles')
# ═════════════════════════════════════════════════════════════════════════════
run('ssh-add testserver 192.168.1.100 ubuntu 22')
run('ssh-list')
run('ssh-connect testserver')

# ═════════════════════════════════════════════════════════════════════════════
section('22 · Aegis Script (.aegis file)')
# ═════════════════════════════════════════════════════════════════════════════
_script = Path('_aegis_test_script.aegis')
_script.write_text(
    '# Aegis test script\n'
    'echo script started\n'
    'python --version\n'
    'pip --version\n'
    'git --version\n'
    '$GREETING = hello\n'
    'echo $GREETING from aegis script\n'
    'echo script done\n'
)
run('_aegis_test_script.aegis')
_script.unlink(missing_ok=True)

# ═════════════════════════════════════════════════════════════════════════════
section('23 · LLM Context')
# ═════════════════════════════════════════════════════════════════════════════
run('context add I am using Python 3.13 on Windows 11')
run('context add My project uses Flask and PostgreSQL on port 5432')
run('context')        # no args = list context entries
run('context clear')
run('context')        # show empty

# ═════════════════════════════════════════════════════════════════════════════
section('24 · Natural Language → Commands  (LLM)')
# ═════════════════════════════════════════════════════════════════════════════
if HAS_CONFIG:
    for nl in [
        'show me all running processes',
        'list files in current directory',
        'what is my IP address',
        'show python version',
        'show current git branch',
        'show last 5 git commits',
        'list all installed python packages',
        'check if docker is running',
        'show disk usage',
        'show environment variables',
        'find all python files',
        'create a folder called output',
    ]:
        run(nl)
else:
    print(f'  [{Fore.YELLOW}SKIP{Style.RESET_ALL}] no config — LLM unavailable')

# ═════════════════════════════════════════════════════════════════════════════
section('25 · Explain Command  (LLM)')
# ═════════════════════════════════════════════════════════════════════════════
if HAS_CONFIG:
    run('explain git rebase -i HEAD~3')
    run('explain docker run -d -p 80:8080 --name web nginx')
    run('explain pip install -r requirements.txt --upgrade')
else:
    print(f'  [{Fore.YELLOW}SKIP{Style.RESET_ALL}] no config')

# ═════════════════════════════════════════════════════════════════════════════
section('26 · Session Stats')
# ═════════════════════════════════════════════════════════════════════════════
run('stats')
run('commit-msg', mock_input='n')  # generates commit message; auto-decline to apply it

# ═════════════════════════════════════════════════════════════════════════════
section('27 · Unknown Commands  (aegis suggests install)')
# ═════════════════════════════════════════════════════════════════════════════
# Stub LLM so it doesn't hang waiting for Groq + auto-install confirmation
import utils.command_executor as _ce_mod
_orig_huc = _ce_mod.handle_unknown_command
_ce_mod.handle_unknown_command = lambda *a, **kw: (None, None)

for cmd in ['htop', 'bat --version', 'exa --version', 'fzf --version']:
    run(cmd)

_ce_mod.handle_unknown_command = _orig_huc  # restore

# ═════════════════════════════════════════════════════════════════════════════
section('28 · Ports')
# ═════════════════════════════════════════════════════════════════════════════
run('ports')

# ═════════════════════════════════════════════════════════════════════════════
section('29 · Update')
# ═════════════════════════════════════════════════════════════════════════════
run('update')

# ═════════════════════════════════════════════════════════════════════════════
section('DONE')
# ═════════════════════════════════════════════════════════════════════════════
print(f'\n  All commands executed through AegisShell pipeline.')
print(f'  Saving output...\n')

# ── Write captured output to file (ANSI stripped) ─────────────────────────────
sys.stdout = _real_out
_ANSI = re.compile(r'\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
_clean = _ANSI.sub('', _log_buf.getvalue()).replace('\r', '')
_out = Path(__file__).parent / 'test_output.txt'
_out.write_text(_clean, encoding='utf-8')
print(f'Output saved → {_out}')
