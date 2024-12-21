# This file is protected under the MIT License.
# Please see the LICENSE and the README file for more information.

# Would you like to contribute?
# Head on to our Github repository:
# https://github.com/islemci/cliwrap

import sys
import os
import subprocess
import json
import time
from collections import Counter

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
BLUE = "\033[0;34m"
MAGENTA = "\033[0;35m"
CYAN = "\033[0;36m"
BOLD_YELLOW = "\033[1;33m"
RESET = "\033[0m"

if __name__ == "__main__":
    # Check the terminal & parse the history file
    def check_and_return_history_file(shell):
        history_file = ""
        home = os.path.expanduser("~")

        if shell == "fish":
            history_file = os.path.join(home, ".local/share/fish/fish_history")
        elif shell == "zsh":
            history_file = os.path.join(os.getenv("ZDOTDIR", home), ".zsh_history")
        elif shell == "csh" or shell == "tcsh":
            history_file = os.path.join(home, ".history")
        elif shell == "bash":
            history_file = os.path.join(home, ".bash_history")
        else:
            print(f"{RED}Your shell is not added to the script. Considering creating an issue on the GitHub repository.{RESET}", file=sys.stderr)
            return None

        if not os.path.isfile(history_file):
            print(f"{RED}The specified terminal history file was not found! Why don't you run `cliwrap -h` to find a compatible one?{RESET}", file=sys.stderr)
            return None

        return history_file

    def detect_history_file(arg):
        if arg.startswith("-"):
            shell = arg[1:]
            return check_and_return_history_file(shell)
        elif arg == "":
            shell = os.path.basename(os.getenv("SHELL", ""))
            return check_and_return_history_file(shell)
        else:
            print(f"{RED}Invalid arguments. Run `cliwrap -h`.{RESET}", file=sys.stderr)
            return None
    # Process the history file
    def preprocess_history(file):
        if os.path.isfile(file):
            if "fish_history" in file:
                with open(file, "r", errors='ignore') as f:
                    return [line.split(": ", 1)[1] for line in f if line.startswith("- cmd: ")]
            else:
                with open(file, "r", errors='ignore') as f:
                    return [line.strip() for line in f if line.strip()]
        else:
            print(f"{RED}Error: No history file found{RESET}", file=sys.stderr)
            return None

    def parse_history(history_data):
        counter = Counter([line.split()[0] for line in history_data if line])
        return counter.most_common(10)

    def parse_full_commands(history_data):
        counter = Counter(history_data)
        return counter.most_common(10)

    def display_title():
        print(CYAN)   
        # ASCII art sometimes acts weird on Python.
        #  https://patorjk.com/software/taag/#p=display&f=Big&t=CLIwrap
        print(r"""
   _____ _      _____                        
  / ____| |    |_   _|                       
 | |    | |      | |_      ___ __ __ _ _ __  
 | |    | |      | \ \ /\ / / '__/ _` | '_ \ 
 | |____| |____ _| |\ V  V /| | | (_| | |_) |
  \_____|______|_____\_/\_/ |_|  \__,_| .__/ 
                                      | |    
                                      |_|    
        """)
        print(RESET)

    def display_table(title, data, suppress_message):
        print(f"\n{MAGENTA}{title}{RESET}")
        print(f"{BOLD_YELLOW}---------------------------------{RESET}")
        print(f"{CYAN}Usage Count | Command{RESET}")
        print(f"{BOLD_YELLOW}---------------------------------{RESET}")
        for cmd, count in data:
            print(f"{count} | {cmd}")
        print(f"{BOLD_YELLOW}---------------------------------{RESET}\n")

        if not suppress_message:
            top_item = data[1][0]
            messages = {
                "git": "Great! You're a git master! Keep version controlling like a pro.",
                "zoom": "Wow, are you like meetings? Good meetings!",
                "ls": "Looks like you're exploring a lot of directories. Neat!",
                "cd": "Navigating through the filesystem like a champ!",
                "mv": "You often move files and folders. Are you tired?",
                "rm": "Don't delete everything! They can be important :)",
                "python": "Python enthusiast detected! Keep coding.",
                "vim": "Spending quality time editing files, I see!",
                "nano": "Spending quality time editing files, I see!",
                "apt": "You like download new packages and apps, am I correct?",
                "brew": "You like download new packages and apps, am I correct?",
                "pacman": "You like download new packages and apps, am I correct?",
                "yay": "You like download new packages and apps, am I correct?",
                "cliwrap": "Your top tool is cliwrap? Thank you for the interest!",
                "code": "VSCode? Do you really program that much?",
                "neofetch": "Are you like neofetch? I think, you'll like CLIwrap too!",
                "fastfetch": "Do you like fastfetch? I think, you'll like CLIwrap too!",
                "nvim": "You’re not just editing files: you’re crafting masterpieces!, one keybind at a time!",
                "make": "You do a lot of compiling, right? Honestly, I'm a fan of yours.",
                "cat": "Don't tell me you even read books from the terminal! Or is it just cat love? :D"
            }
            print(f"{BOLD_YELLOW}{messages.get(top_item, f'Your top tool is {top_item}. Keep rocking your terminal!')}{RESET}")

    def display_help():
        print(f"{CYAN}Usage: cliwrap [options]{RESET}")
        print(f"{BOLD_YELLOW}Options:{RESET}")
        print(f"{GREEN}  -zsh{RESET}    Force Zsh history file")
        print(f"{GREEN}  -bash{RESET}   Force Bash history file")
        print(f"{GREEN}  -csh{RESET}    Force Csh history file")
        print(f"{GREEN}  -tcsh{RESET}   Force Tcsh history file")
        print(f"{GREEN}  -fish{RESET}   Force Fish shell history file")
        print(f"{GREEN}  -h{RESET}      Display this help message")
        print(f"{BOLD_YELLOW}Logging:{RESET}")
        print(f"{GREEN}  --enable-tracking <shell>{RESET}  Enable tracking in the specified shell")
        print(f"{GREEN}  --disable-tracking <shell>{RESET} Disable tracking in the specified shell")
        print(f"{BOLD_YELLOW}Source Code:{RESET}")
        print(f"https://github.com/islemci/cliwrap")

    def is_tracking_enabled(shell_config):
        try:
            with open(shell_config, "r") as f:
                content = f.read()
                return "# CLIwrap tracking code" in content
        except Exception:
            return False

    def enable_tracking(shell):
        home = os.path.expanduser("~")
        log_file = os.path.join(home, "wrapped.json")
        if shell == "bash":
            shell_config = os.path.join(home, ".bashrc")
            tracking_code = "\n# CLIwrap tracking code\ntrap 'cliwrap --log-command \"$BASH_COMMAND\"' DEBUG\n"
        elif shell == "zsh":
            shell_config = os.path.join(home, ".zshrc")
            tracking_code = "\n# CLIwrap tracking code\npreexec() { cliwrap --log-command \"$1\"; }\n"
        elif shell == "fish":
            shell_config = os.path.join(home, ".config/fish/config.fish")
            tracking_code = "\n# CLIwrap tracking code\nfunction fish_preexec --on-event fish_preexec; cliwrap --log-command \"$argv\"; end\n"
        else:
            print(f"{RED}Unsupported shell for tracking.{RESET}", file=sys.stderr)
            sys.exit(1)

        if is_tracking_enabled(shell_config):
            print(f"Tracking is already enabled in {shell_config}")
            return

        try:
            with open(shell_config, "a") as f:
                f.write(tracking_code)
            print(f"Tracking enabled in {shell_config}")

            if not os.path.exists(log_file):
                with open(log_file, "w") as f:
                    json.dump({"startDate": int(time.time()), "commands": []}, f)  # Set startDate as Unix timestamp
        except Exception as e:
            print(f"{RED}Failed to enable tracking: {e}{RESET}", file=sys.stderr)
            sys.exit(1)

    def disable_tracking(shell):
        home = os.path.expanduser("~")
        if shell == "bash":
            shell_config = os.path.join(home, ".bashrc")
            tracking_code = "\n# CLIwrap tracking code\ntrap 'cliwrap --log-command \"$BASH_COMMAND\"' DEBUG\n"
        elif shell == "zsh":
            shell_config = os.path.join(home, ".zshrc")
            tracking_code = "\n# CLIwrap tracking code\npreexec() { cliwrap --log-command \"$1\"; }\n"
        elif shell == "fish":
            shell_config = os.path.join(home, ".config/fish/config.fish")
            tracking_code = "\n# CLIwrap tracking code\nfunction fish_preexec --on-event fish_preexec; cliwrap --log-command \"$argv\"; end\n"
        else:
            print(f"{RED}Unsupported shell for disabling.{RESET}", file=sys.stderr)
            sys.exit(1)

        try:
            with open(shell_config, "r") as f:
                content = f.read()
            content = content.replace(tracking_code, "")
            with open(shell_config, "w") as f:
                f.write(content)
            print(f"Tracking disabled in {shell_config}")
        except Exception as e:
            print(f"{RED}Failed to disable tracking: {e}{RESET}", file=sys.stderr)
            sys.exit(1)

    def log_command(command):
        home = os.path.expanduser("~")
        log_file = os.path.join(home, "wrapped.json")
        tool = command.split()[0] if command else ""
        entry = {
            "command": command,
            "tool": tool,
            "timestamp": int(time.time())
        }
        try:
            if os.path.exists(log_file):
                with open(log_file, "r") as f:
                    data = json.load(f)
            else:
                data = {"startDate": time.strftime("%Y-%m-%d %H:%M:%S"), "commands": []}
            data["commands"].append(entry)
            with open(log_file, "w") as f:
                json.dump(data, f, indent=4)  # Beautify JSON output
        except Exception as e:
            print(f"{RED}Failed to log command: {e}{RESET}", file=sys.stderr)

    def main():
        if len(sys.argv) > 1 and sys.argv[1] == "-h":
            display_help()
            sys.exit(0)

        if len(sys.argv) > 1:
            if sys.argv[1] == "--enable-tracking":
                shell = sys.argv[2] if len(sys.argv) > 2 else ""
                if not shell:
                    print(f"{RED}Please specify a shell after --enable-tracking{RESET}", file=sys.stderr)
                    sys.exit(1)
                enable_tracking(shell)
                sys.exit(0)
            elif sys.argv[1] == "--disable-tracking":
                shell = sys.argv[2] if len(sys.argv) > 2 else ""
                if not shell:
                    print(f"{RED}Please specify a shell after --disable-tracking{RESET}", file=sys.stderr)
                    sys.exit(1)
                disable_tracking(shell)
                sys.exit(0)
            elif sys.argv[1] == "--log-command":
                command = sys.argv[2] if len(sys.argv) > 2 else ""
                log_command(command)
                sys.exit(0)

        history_file = detect_history_file(sys.argv[1] if len(sys.argv) > 1 else "")
        if not history_file:
            sys.exit(1)

        display_title()

        print(f"{GREEN}Parsing history file: {history_file}{RESET}\n")

        history_data = preprocess_history(history_file)
        if not history_data:
            sys.exit(1)

        top_tools = parse_history(history_data)
        display_table("Top Tools", top_tools, True)

        top_commands = parse_full_commands(history_data)
        display_table("Top Full Commands", top_commands, False)

        total_commands = len(history_data)
        print(f"{GREEN}Total Commands Executed: {total_commands}{RESET}")

    main()
