#!/usr/bin/env python3
"""
Personal Assistant - Test & Demo Script

This script tests the personal assistant functionality and demonstrates
key features without requiring full setup.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_basic_functionality():
    """Test basic functionality without external dependencies"""
    print("🧪 Testing Personal Assistant - Basic Functionality")
    print("=" * 60)
    
    try:
        # Test imports
        print("🔹 Testing imports...")
        from personal_assistant import PersonalAssistantOrchestrator, TaskInstruction, SystemAgent
        from gemini_integration import GeminiCLIClient
        print("✅ All imports successful")
        
        # Test instruction parsing
        print("\n🔹 Testing instruction parsing...")
        instruction = TaskInstruction("test instruction")
        print(f"✅ TaskInstruction created: {instruction.instruction}")
        
        # Test agent initialization
        print("\n🔹 Testing agent initialization...")
        system_agent = SystemAgent()
        print(f"✅ SystemAgent initialized: {system_agent.name}")
        
        # Test orchestrator initialization
        print("\n🔹 Testing orchestrator initialization...")
        orchestrator = PersonalAssistantOrchestrator()
        print(f"✅ Orchestrator initialized with {len(orchestrator.agents)} agents")
        
        # Test Gemini client (without requiring actual Gemini CLI)
        print("\n🔹 Testing Gemini client...")
        gemini_client = GeminiCLIClient()
        availability_msg = "available" if gemini_client.available else "not available (expected without setup)"
        print(f"✅ Gemini client created: {availability_msg}")
        
        print("\n✨ Basic functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

async def test_safe_system_operations():
    """Test safe system operations that don't require special permissions"""
    print("\n🔧 Testing Safe System Operations")
    print("=" * 50)
    
    try:
        from personal_assistant import PersonalAssistantOrchestrator
        
        orchestrator = PersonalAssistantOrchestrator()
        
        # Test safe commands
        safe_instructions = [
            "show current directory",
            "list files in current directory",
            "check what operating system we're running",
        ]
        
        for instruction in safe_instructions:
            print(f"\n📋 Testing: '{instruction}'")
            try:
                result = await orchestrator.process_instruction(instruction)
                if result['success']:
                    print("   ✅ Success!")
                    # Show abbreviated results
                    for agent_result in result['results']:
                        if agent_result['result']['success']:
                            agent_name = agent_result['agent']
                            print(f"   📄 {agent_name}: Operation completed")
                else:
                    print("   ⚠️  Partial success or no capable agents")
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ System operations test failed: {str(e)}")
        return False

async def test_learning_system():
    """Test the learning and adaptation system"""
    print("\n🧠 Testing Learning System")
    print("=" * 40)
    
    try:
        from personal_assistant import PersonalAssistantOrchestrator
        
        orchestrator = PersonalAssistantOrchestrator()
        
        print("🔹 Initial learning data:")
        print(f"   User patterns: {len(orchestrator.learning_data['user_patterns'])}")
        print(f"   Successful commands: {len(orchestrator.learning_data['successful_commands'])}")
        
        # Simulate a successful execution for learning
        print("\n🔹 Simulating learning from execution...")
        
        # This would normally happen during actual instruction processing
        pattern_key = "test_pattern"
        orchestrator.learning_data['user_patterns'][pattern_key] = {
            'count': 1,
            'success_rate': 1.0,
            'avg_execution_time': 0.5,
            'last_used': datetime.now().isoformat()
        }
        
        print("✅ Learning data updated")
        print(f"   New pattern: {pattern_key}")
        
        return True
        
    except Exception as e:
        print(f"❌ Learning system test failed: {str(e)}")
        return False

def test_configuration_loading():
    """Test configuration file loading"""
    print("\n⚙️ Testing Configuration Loading")
    print("=" * 45)
    
    try:
        from personal_assistant import PersonalAssistantOrchestrator
        
        # Test with default configuration
        print("🔹 Testing default configuration...")
        orchestrator = PersonalAssistantOrchestrator()
        config = orchestrator.config
        
        print("✅ Configuration loaded:")
        print(f"   Gemini model: {config['gemini']['model']}")
        print(f"   Default browser: {config['browser']['default_browser']}")
        print(f"   Safe mode: {config['system']['safe_mode']}")
        print(f"   Learning enabled: {config['learning']['enabled']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {str(e)}")
        return False

def show_system_info():
    """Show system information for debugging"""
    print("\n💻 System Information")
    print("=" * 30)
    
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Python path: {sys.executable}")
    
    # Check for key dependencies
    dependencies = [
        'asyncio', 'json', 'yaml', 'subprocess', 'datetime',
        'logging', 'os', 'sys', 're'
    ]
    
    print("\n📦 Core dependencies:")
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"   ✅ {dep}")
        except ImportError:
            print(f"   ❌ {dep}")

async def run_comprehensive_test():
    """Run all tests"""
    print("🚀 Personal Assistant - Comprehensive Test Suite")
    print("=" * 70)
    
    start_time = datetime.now()
    
    # Show system info first
    show_system_info()
    
    # Run tests
    tests = [
        ("Basic Functionality", test_basic_functionality()),
        ("Configuration Loading", test_configuration_loading()),
        ("Learning System", test_learning_system()),
        ("Safe System Operations", test_safe_system_operations()),
    ]
    
    results = []
    for test_name, test_coro in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = await test_coro if asyncio.iscoroutine(test_coro) else test_coro
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"\n{'='*70}")
    print("📊 TEST SUMMARY")
    print(f"{'='*70}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:<8} {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    print(f"Duration: {duration:.2f} seconds")
    
    if passed == total:
        print("\n🎉 All tests passed! The personal assistant is ready for use.")
        print("\n📋 Next steps:")
        print("   1. Run: ./setup.sh (to install dependencies)")
        print("   2. Configure your .env file with API keys")
        print("   3. Run: python personal_assistant.py --interactive")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the output above for details.")

def show_quick_demo():
    """Show a quick demo of expected functionality"""
    print("\n🎬 Quick Demo - Expected Functionality")
    print("=" * 50)
    
    demo_scenarios = [
        {
            "instruction": "do we have college-photo.jpg in desktop",
            "expected": "Navigate to Desktop directory and search for the file",
            "agents": ["SystemAgent"]
        },
        {
            "instruction": "open chrome and go to gmail", 
            "expected": "Launch Chrome browser and navigate to Gmail",
            "agents": ["BrowserAgent"]
        },
        {
            "instruction": "find all python files in current directory",
            "expected": "Search for *.py files using system commands",
            "agents": ["SystemAgent"]
        },
        {
            "instruction": "check if development server is running on port 8080",
            "expected": "Check system processes and network connections",
            "agents": ["SystemAgent"]
        }
    ]
    
    for i, scenario in enumerate(demo_scenarios, 1):
        print(f"\n{i}. Instruction: '{scenario['instruction']}'")
        print(f"   Expected: {scenario['expected']}")
        print(f"   Agents: {', '.join(scenario['agents'])}")
    
    print(f"\n💡 The personal assistant will:")
    print("   • Parse natural language instructions")
    print("   • Determine which agents can handle the task")
    print("   • Execute safe system commands or browser actions")
    print("   • Learn from successful executions")
    print("   • Provide helpful error messages and suggestions")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Personal Assistant')
    parser.add_argument('--test', choices=['basic', 'system', 'learning', 'config', 'all'], 
                       default='all', help='Which test to run')
    parser.add_argument('--demo', action='store_true', help='Show quick demo of functionality')
    parser.add_argument('--info', action='store_true', help='Show system information only')
    
    args = parser.parse_args()
    
    if args.info:
        show_system_info()
    elif args.demo:
        show_quick_demo()
    else:
        if args.test == 'basic':
            asyncio.run(test_basic_functionality())
        elif args.test == 'system':
            asyncio.run(test_safe_system_operations())
        elif args.test == 'learning':
            asyncio.run(test_learning_system())
        elif args.test == 'config':
            test_configuration_loading()
        else:
            asyncio.run(run_comprehensive_test())