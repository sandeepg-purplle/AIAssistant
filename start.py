#!/usr/bin/env python3
"""
Personal Assistant - Quick Start Launcher

Simple launcher script that provides an easy way to start the personal assistant
with different modes and configurations.
"""

import sys
import os
import asyncio
import subprocess
from datetime import datetime

def print_banner():
    """Print a welcome banner"""
    print("🤖 Personal Assistant - AI Agent Orchestrator")
    print("=" * 55)
    print("Intelligent multi-agent system for automating your tasks")
    print("Built with Gemini CLI, CrewAI, and Browser Automation")
    print("=" * 55)
    print()

def check_dependencies():
    """Check if basic dependencies are available"""
    print("🔍 Checking dependencies...")
    
    checks = []
    
    # Check Python version
    if sys.version_info >= (3, 8):
        checks.append(("Python 3.8+", True, f"✅ Python {sys.version.split()[0]}"))
    else:
        checks.append(("Python 3.8+", False, f"❌ Python {sys.version.split()[0]} (upgrade needed)"))
    
    # Check if virtual environment is active
    venv_active = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    checks.append(("Virtual Environment", venv_active, "✅ Active" if venv_active else "⚠️  Not active"))
    
    # Check for key Python modules
    modules = ['asyncio', 'json', 'logging', 'subprocess', 'datetime']
    for module in modules:
        try:
            __import__(module)
            checks.append((f"Module: {module}", True, "✅ Available"))
        except ImportError:
            checks.append((f"Module: {module}", False, "❌ Missing"))
    
    # Check for optional dependencies
    optional_deps = [
        ('selenium', 'Browser automation'),
        ('yaml', 'Configuration files'),
        ('aiohttp', 'Async HTTP requests')
    ]
    
    for module, description in optional_deps:
        try:
            __import__(module)
            checks.append((f"{description}", True, "✅ Available"))
        except ImportError:
            checks.append((f"{description}", False, "⚠️  Not installed (run setup.sh)"))
    
    # Check for Gemini CLI
    try:
        result = subprocess.run(['gemini', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            checks.append(("Gemini CLI", True, "✅ Available"))
        else:
            checks.append(("Gemini CLI", False, "❌ Not working"))
    except (FileNotFoundError, subprocess.TimeoutExpired):
        checks.append(("Gemini CLI", False, "⚠️  Not installed"))
    
    # Display results
    for name, status, message in checks:
        print(f"  {message}")
    
    # Summary
    critical_failures = sum(1 for name, status, _ in checks[:4] if not status)  # First 4 are critical
    if critical_failures > 0:
        print(f"\n❌ {critical_failures} critical issues found. Run ./setup.sh first.")
        return False
    else:
        print(f"\n✅ Core dependencies check passed!")
        return True

def show_quick_help():
    """Show quick help and usage examples"""
    print("\n📚 Quick Help")
    print("-" * 20)
    print("Example commands to try:")
    print("  • 'do we have college-photo.jpg in desktop'")
    print("  • 'list all python files in current directory'") 
    print("  • 'open chrome and go to gmail'")
    print("  • 'check disk space'")
    print("  • 'find files containing config'")
    print()
    print("Commands:")
    print("  • Type 'help' for more assistance")
    print("  • Type 'quit' or 'exit' to end session")
    print("  • Type 'demo' to see example scenarios")
    print()

async def start_interactive_mode():
    """Start the interactive assistant"""
    try:
        from personal_assistant import PersonalAssistantOrchestrator
        
        print("🚀 Starting Personal Assistant...")
        orchestrator = PersonalAssistantOrchestrator()
        
        show_quick_help()
        
        await orchestrator.interactive_mode()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Try running: ./setup.sh")
    except Exception as e:
        print(f"❌ Error starting assistant: {e}")

def show_menu():
    """Show main menu options"""
    print("🎯 What would you like to do?")
    print("=" * 35)
    print("1. 🤖 Start Interactive Assistant")
    print("2. 🧪 Run Tests")
    print("3. 🎬 View Demo Examples")
    print("4. ⚙️  Check System Info") 
    print("5. 📖 Setup Instructions")
    print("6. ❌ Exit")
    print()
    
    while True:
        try:
            choice = input("Enter choice (1-6): ").strip()
            
            if choice == '1':
                print("\n" + "="*50)
                asyncio.run(start_interactive_mode())
                break
            elif choice == '2':
                print("\n" + "="*50)
                subprocess.run([sys.executable, 'test_assistant.py', '--test', 'all'])
                break
            elif choice == '3':
                print("\n" + "="*50)
                subprocess.run([sys.executable, 'examples.py', '--examples'])
                break
            elif choice == '4':
                print("\n" + "="*50)
                subprocess.run([sys.executable, 'test_assistant.py', '--info'])
                break
            elif choice == '5':
                show_setup_instructions()
                break
            elif choice == '6':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-6.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def show_setup_instructions():
    """Show setup instructions"""
    print("\n📖 Setup Instructions")
    print("=" * 30)
    print("1. Run the setup script:")
    print("   ./setup.sh")
    print()
    print("2. Get a Gemini API key:")
    print("   • Visit: https://aistudio.google.com/apikey")
    print("   • Add to .env file: GEMINI_API_KEY=your_key_here")
    print()
    print("3. Optional - Install Gemini CLI:")
    print("   npm install -g @google/gemini-cli")
    print()
    print("4. Optional - Install local LLM (Ollama):")
    print("   • Visit: https://ollama.ai/")
    print("   • Pull model: ollama pull llama2")
    print()
    print("5. Start the assistant:")
    print("   python start.py")

def main():
    """Main entry point"""
    print_banner()
    
    # Check if this is first run
    if len(sys.argv) > 1 and sys.argv[1] == '--direct':
        # Direct mode - start assistant immediately
        asyncio.run(start_interactive_mode())
        return
    
    # Check basic dependencies
    deps_ok = check_dependencies()
    
    if not deps_ok:
        print("\n❌ Please run setup first: ./setup.sh")
        print("Or run: python start.py --help")
        return
    
    # Show menu
    show_menu()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--help', '-h']:
            print("Personal Assistant Launcher")
            print()
            print("Usage:")
            print("  python start.py           # Show menu")
            print("  python start.py --direct  # Start assistant directly")
            print()
            show_setup_instructions()
        elif sys.argv[1] == '--direct':
            asyncio.run(start_interactive_mode())
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Use --help for usage information")
    else:
        main()