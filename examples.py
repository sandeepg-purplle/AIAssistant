#!/usr/bin/env python3
"""
Personal Assistant - Example Usage Scenarios

This file contains example usage scenarios and demonstrations
of the personal assistant's capabilities.
"""

import asyncio
import os
from personal_assistant import PersonalAssistantOrchestrator

async def demo_system_operations():
    """Demonstrate system command operations"""
    print("🔧 System Operations Demo")
    print("=" * 50)
    
    orchestrator = PersonalAssistantOrchestrator()
    
    examples = [
        "do we have college-photo.jpg in desktop",
        "list all python files in current directory", 
        "check disk space",
        "find all files with 'config' in the name",
        "show current directory",
        "what processes are running"
    ]
    
    for example in examples:
        print(f"\n📋 Instruction: '{example}'")
        result = await orchestrator.process_instruction(example)
        
        if result['success']:
            print("✅ Success!")
            for agent_result in result['results']:
                if agent_result['result']['success']:
                    # Show first few results for system commands
                    agent_data = agent_result['result']['result']
                    if isinstance(agent_data, list) and len(agent_data) > 0:
                        print(f"   📋 {agent_result['agent']}: {agent_data[0]['stdout'][:200]}...")
        else:
            print("❌ Failed!")
            for agent_result in result['results']:
                if 'error' in agent_result['result']:
                    print(f"   ⚠️  {agent_result['agent']}: {agent_result['result']['error']}")

async def demo_browser_operations():
    """Demonstrate browser automation operations"""
    print("\n🌐 Browser Operations Demo")
    print("=" * 50)
    
    orchestrator = PersonalAssistantOrchestrator()
    
    examples = [
        "open chrome browser",
        "go to google.com",
        "navigate to gmail.com",
        # Note: Login examples would require actual credential setup
        # "login to gmail with my credentials",
        # "open first email"
    ]
    
    for example in examples:
        print(f"\n📋 Instruction: '{example}'")
        result = await orchestrator.process_instruction(example)
        
        if result['success']:
            print("✅ Success!")
            for agent_result in result['results']:
                if agent_result['result']['success']:
                    print(f"   📋 {agent_result['agent']}: Operation completed")
        else:
            print("❌ Failed!")
            for agent_result in result['results']:
                if 'error' in agent_result['result']:
                    print(f"   ⚠️  {agent_result['agent']}: {agent_result['result']['error']}")
        
        # Add delay between browser operations
        await asyncio.sleep(2)

async def demo_learning_capabilities():
    """Demonstrate learning and adaptation"""
    print("\n🧠 Learning Capabilities Demo")
    print("=" * 50)
    
    orchestrator = PersonalAssistantOrchestrator()
    
    # Simulate repeated similar instructions to show learning
    similar_instructions = [
        "check if photo.jpg exists in desktop",
        "do we have image.png in desktop", 
        "find document.pdf in desktop folder",
        "look for music.mp3 in desktop directory"
    ]
    
    print("Demonstrating pattern learning with similar instructions:")
    
    for i, instruction in enumerate(similar_instructions, 1):
        print(f"\n📋 Instruction {i}: '{instruction}'")
        result = await orchestrator.process_instruction(instruction)
        
        # Show learning data updates
        if instruction in str(orchestrator.learning_data):
            print("🧠 Learning pattern recognized!")
        
        if result['success']:
            print("✅ Success!")
        else:
            print("❌ Failed!")

async def demo_complex_scenarios():
    """Demonstrate complex multi-step scenarios"""
    print("\n🎯 Complex Scenarios Demo")
    print("=" * 50)
    
    orchestrator = PersonalAssistantOrchestrator()
    
    scenarios = [
        {
            "name": "File Management Workflow",
            "instructions": [
                "check what files are in desktop",
                "find all image files in desktop", 
                "show disk usage"
            ]
        },
        {
            "name": "Development Workflow", 
            "instructions": [
                "list all python files",
                "find files containing 'import'",
                "check current git status"
            ]
        },
        {
            "name": "System Monitoring",
            "instructions": [
                "show system processes",
                "check memory usage",
                "list running services"
            ]
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📊 Scenario: {scenario['name']}")
        print("-" * 30)
        
        for instruction in scenario['instructions']:
            print(f"\n📋 Step: '{instruction}'")
            result = await orchestrator.process_instruction(instruction)
            
            if result['success']:
                print("   ✅ Success!")
            else:
                print("   ❌ Failed!")
            
            # Brief pause between steps
            await asyncio.sleep(1)

async def demo_gemini_integration():
    """Demonstrate Gemini CLI integration"""
    print("\n🤖 Gemini CLI Integration Demo")
    print("=" * 50)
    
    from gemini_integration import GeminiCLIClient
    
    client = GeminiCLIClient()
    
    if not client.available:
        print("❌ Gemini CLI not available. Please install it first:")
        print("   npm install -g @google/gemini-cli")
        print("   Or set up authentication: https://github.com/google-gemini/gemini-cli")
        return
    
    print("✅ Gemini CLI is available")
    
    # Test instruction understanding
    print("\n🔹 Testing Enhanced Instruction Understanding...")
    instruction = "open chrome, go to gmail, and check if I have any new emails"
    
    response = await client.understand_instruction(
        instruction, 
        ["SystemAgent", "BrowserAgent"]
    )
    
    if response.success:
        print(f"✅ Gemini understood the instruction!")
        print(f"📋 Analysis: {response.content[:300]}...")
        
        if response.metadata and "parsed_instruction" in response.metadata:
            parsed = response.metadata["parsed_instruction"]
            print(f"🎯 Agents needed: {parsed.get('agents', [])}")
            print(f"⏱️  Estimated time: {parsed.get('estimated_duration', 'unknown')} seconds")
    else:
        print(f"❌ Gemini analysis failed: {response.error}")

def show_usage_examples():
    """Display usage examples and tips"""
    print("📚 Personal Assistant - Usage Examples")
    print("=" * 50)
    
    examples = {
        "File Operations": [
            "do we have college-photo.jpg in desktop",
            "find all PDF files in documents",
            "list files in current directory",
            "show disk space usage",
            "check if config.yaml exists"
        ],
        
        "Browser Automation": [
            "open chrome and go to gmail",
            "navigate to youtube.com", 
            "open firefox browser",
            "go to linkedin and login",
            "check my emails in gmail"
        ],
        
        "System Monitoring": [
            "show running processes",
            "check memory usage",
            "display system information",
            "list installed packages",
            "check git status"
        ],
        
        "Complex Tasks": [
            "find all python files and check which ones import numpy",
            "backup my desktop files to documents folder",
            "check if the server is running on port 8080",
            "download my latest emails and save to text file",
            "create a summary of today's git commits"
        ]
    }
    
    for category, commands in examples.items():
        print(f"\n🔹 {category}:")
        for cmd in commands:
            print(f"   • {cmd}")
    
    print("\n💡 Tips:")
    print("• Be specific about file names and locations")
    print("• Use natural language - the assistant understands context")
    print("• For browser tasks, mention the specific browser (Chrome/Firefox)")
    print("• The assistant learns from your patterns over time")
    print("• Use 'quit' or 'exit' to end interactive sessions")

async def run_all_demos():
    """Run all demo scenarios"""
    print("🚀 Personal Assistant - Complete Demo")
    print("=" * 60)
    
    # Show usage examples first
    show_usage_examples()
    
    # Run system operations demo
    await demo_system_operations()
    
    # Run learning demo
    await demo_learning_capabilities()
    
    # Run complex scenarios demo
    await demo_complex_scenarios()
    
    # Run Gemini integration demo (if available)
    await demo_gemini_integration()
    
    print("\n✨ Demo completed! The assistant is ready for interactive use.")
    print("Run: python personal_assistant.py --interactive")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Personal Assistant Examples')
    parser.add_argument('--demo', choices=['system', 'browser', 'learning', 'complex', 'gemini', 'all'],
                       default='all', help='Which demo to run')
    parser.add_argument('--examples', action='store_true', help='Show usage examples only')
    
    args = parser.parse_args()
    
    if args.examples:
        show_usage_examples()
    else:
        if args.demo == 'system':
            asyncio.run(demo_system_operations())
        elif args.demo == 'browser':
            asyncio.run(demo_browser_operations())
        elif args.demo == 'learning':
            asyncio.run(demo_learning_capabilities())
        elif args.demo == 'complex':
            asyncio.run(demo_complex_scenarios())
        elif args.demo == 'gemini':
            asyncio.run(demo_gemini_integration())
        else:
            asyncio.run(run_all_demos())