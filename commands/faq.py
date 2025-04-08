# commands/faq.py

from colorama import Fore, Style

def show_faq():
    """Display frequently asked questions about Aegis Shell"""
    print(Fore.CYAN + Style.BRIGHT + "Frequently Asked Questions" + Style.RESET_ALL)
    print()
    
    questions = [
        {
            "q": "What is Aegis Shell?",
            "a": "Aegis Shell is an AI-powered terminal that helps developers install and manage tools and packages across different platforms."
        },
        {
            "q": "How do I install a package?",
            "a": "Simply type the name of the tool or package you want to use. Aegis will detect if it's not installed and offer to install it for you."
        },
        {
            "q": "Which package managers are supported?",
            "a": "Aegis supports pip, npm, winget, apt, brew, and more depending on your operating system."
        },
        {
            "q": "How does the AI help me?",
            "a": "If you try to use an unknown command, Aegis can use AI to identify what the command might be and suggest how to install it."
        },
        {
            "q": "Can I add custom commands?",
            "a": "Yes! When you install packages through Aegis, they are automatically added to the command mappings for future use."
        },
        {
            "q": "How do I update Aegis Shell?",
            "a": "Run the command 'update' to check for and install updates to Aegis Shell."
        },
        {
            "q": "I found a bug, how do I report it?",
            "a": "Please report bugs on our GitHub repository or contact the developers: Tanish, Nidhi & Nishant."
        }
    ]
    
    for i, qa in enumerate(questions, 1):
        print(Fore.GREEN + f"{i}. {qa['q']}" + Style.RESET_ALL)
        print(Fore.WHITE + f"   {qa['a']}")
        print()
    
    print(Fore.YELLOW + "For more information, type 'help' to see all available commands." + Style.RESET_ALL)