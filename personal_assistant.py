#!/usr/bin/env python3
"""
Personal Assistant - AI Agent Orchestrator

A comprehensive personal assistant that can understand natural language instructions
and orchestrate multiple AI agents to complete complex tasks including:
- System/terminal operations
- Browser automation
- File management
- Web interactions
- Task decomposition and execution

Integrates with Gemini CLI and supports local LLMs for enhanced capabilities.
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import re

# Third-party imports (will be installed via requirements.txt)
try:
    import aiohttp
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    import yaml
    from crewai import Agent, Task, Crew, Process
except ImportError:
    print("Installing required dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", 
                          "crewai", "selenium", "aiohttp", "pyyaml", "beautifulsoup4", "requests"])
    # Re-import after installation
    import aiohttp
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    import yaml
    from crewai import Agent, Task, Crew, Process

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/personal_assistant.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TaskInstruction:
    """Represents a user instruction with context and metadata"""
    instruction: str
    timestamp: datetime = datetime.now()
    context: Dict[str, Any] = None
    priority: str = "normal"  # low, normal, high, urgent
    estimated_duration: Optional[int] = None  # minutes
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}

@dataclass
class AgentResponse:
    """Response from an agent execution"""
    agent_name: str
    success: bool
    result: Any
    error: Optional[str] = None
    execution_time: Optional[float] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class BaseAgent(ABC):
    """Abstract base class for all agents"""
    
    def __init__(self, name: str, description: str, gemini_client=None):
        self.name = name
        self.description = description
        self.gemini_client = gemini_client
        self.execution_history: List[Dict] = []
    
    @abstractmethod
    async def execute(self, instruction: TaskInstruction) -> AgentResponse:
        """Execute the given instruction"""
        pass
    
    async def can_handle(self, instruction: TaskInstruction) -> bool:
        """Determine if this agent can handle the given instruction"""
        return False
    
    def log_execution(self, instruction: TaskInstruction, response: AgentResponse):
        """Log execution for learning purposes"""
        self.execution_history.append({
            'timestamp': datetime.now().isoformat(),
            'instruction': instruction.instruction,
            'success': response.success,
            'result': str(response.result)[:200],  # Truncate long results
            'error': response.error
        })

class SystemAgent(BaseAgent):
    """Agent for system and terminal operations"""
    
    def __init__(self, gemini_client=None):
        super().__init__(
            name="SystemAgent",
            description="Handles system commands, file operations, and terminal interactions",
            gemini_client=gemini_client
        )
        self.safe_commands = {
            'ls', 'dir', 'pwd', 'cd', 'find', 'locate', 'grep', 'cat', 'head', 'tail',
            'ps', 'top', 'df', 'du', 'free', 'uname', 'whoami', 'date', 'cal',
            'which', 'whereis', 'file', 'stat', 'wc', 'sort', 'uniq', 'cut'
        }
    
    async def can_handle(self, instruction: TaskInstruction) -> bool:
        """Check if instruction involves system operations"""
        keywords = ['file', 'directory', 'folder', 'desktop', 'ls', 'find', 'search', 
                   'terminal', 'command', 'system', 'check', 'exists']
        return any(keyword in instruction.instruction.lower() for keyword in keywords)
    
    async def execute(self, instruction: TaskInstruction) -> AgentResponse:
        """Execute system commands based on natural language instruction"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Parse instruction and determine commands
            commands = await self._parse_instruction_to_commands(instruction)
            results = []
            
            for cmd in commands:
                if self._is_safe_command(cmd):
                    result = subprocess.run(
                        cmd, shell=True, capture_output=True, text=True, timeout=30
                    )
                    results.append({
                        'command': cmd,
                        'stdout': result.stdout,
                        'stderr': result.stderr,
                        'returncode': result.returncode
                    })
                else:
                    return AgentResponse(
                        agent_name=self.name,
                        success=False,
                        result=None,
                        error=f"Command '{cmd}' is not in safe commands list"
                    )
            
            execution_time = asyncio.get_event_loop().time() - start_time
            response = AgentResponse(
                agent_name=self.name,
                success=True,
                result=results,
                execution_time=execution_time,
                metadata={'commands_executed': len(commands)}
            )
            
            self.log_execution(instruction, response)
            return response
            
        except subprocess.TimeoutExpired:
            return AgentResponse(
                agent_name=self.name,
                success=False,
                result=None,
                error="Command execution timed out"
            )
        except Exception as e:
            return AgentResponse(
                agent_name=self.name,
                success=False,
                result=None,
                error=str(e)
            )
    
    async def _parse_instruction_to_commands(self, instruction: TaskInstruction) -> List[str]:
        """Parse natural language instruction into system commands"""
        text = instruction.instruction.lower()
        commands = []
        
        # Example: "do we have college-photo.jpg in desktop"
        if "desktop" in text and ("have" in text or "exists" in text or "find" in text):
            desktop_path = os.path.expanduser("~/Desktop")
            if os.path.exists(desktop_path):
                commands.append(f"cd '{desktop_path}' && ls -la")
                # Extract filename if mentioned
                if ".jpg" in text or ".png" in text or ".pdf" in text:
                    # Use regex to find filename
                    filename_match = re.search(r'(\w+[-\w]*\.\w+)', text)
                    if filename_match:
                        filename = filename_match.group(1)
                        commands.append(f"find '{desktop_path}' -name '*{filename}*' -type f")
            else:
                commands.append("ls ~/Desktop 2>/dev/null || echo 'Desktop directory not found'")
        
        # Example: "list files in current directory"
        elif "list" in text and "file" in text:
            commands.append("ls -la")
        
        # Example: "find all python files"
        elif "find" in text and "python" in text:
            commands.append("find . -name '*.py' -type f")
        
        # Example: "check disk space"
        elif "disk" in text and "space" in text:
            commands.append("df -h")
        
        # Example: "show running processes"
        elif "process" in text or "running" in text:
            commands.append("ps aux")
        
        # Default fallback
        if not commands:
            commands.append("pwd && ls -la")
        
        return commands
    
    def _is_safe_command(self, command: str) -> bool:
        """Check if command is safe to execute"""
        # Extract the main command
        cmd_parts = command.split()
        if not cmd_parts:
            return False
        
        main_cmd = cmd_parts[0].split('/')[-1]  # Handle paths like /bin/ls
        
        # Check against dangerous patterns
        dangerous_patterns = ['rm', 'del', 'format', 'fdisk', 'mkfs', 'dd', 
                            'chmod 777', 'chown', 'sudo', 'su', 'passwd']
        
        for pattern in dangerous_patterns:
            if pattern in command.lower():
                return False
        
        # Allow safe commands and common command combinations
        safe_starts = ['cd', 'ls', 'find', 'grep', 'cat', 'head', 'tail', 'pwd', 
                      'df', 'du', 'ps', 'top', 'which', 'file', 'stat']
        
        return main_cmd in self.safe_commands or any(command.startswith(safe) for safe in safe_starts)

class BrowserAgent(BaseAgent):
    """Agent for browser automation and web interactions"""
    
    def __init__(self, gemini_client=None):
        super().__init__(
            name="BrowserAgent", 
            description="Handles web browser automation, login, navigation, and interactions",
            gemini_client=gemini_client
        )
        self.driver = None
        self.current_browser = None
    
    async def can_handle(self, instruction: TaskInstruction) -> bool:
        """Check if instruction involves browser operations"""
        keywords = ['browser', 'chrome', 'firefox', 'website', 'login', 'gmail', 
                   'email', 'web', 'navigate', 'click', 'open', 'url']
        return any(keyword in instruction.instruction.lower() for keyword in keywords)
    
    async def execute(self, instruction: TaskInstruction) -> AgentResponse:
        """Execute browser automation based on instruction"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Parse instruction and determine browser actions
            actions = await self._parse_instruction_to_actions(instruction)
            results = []
            
            for action in actions:
                result = await self._execute_browser_action(action, instruction)
                results.append(result)
            
            execution_time = asyncio.get_event_loop().time() - start_time
            response = AgentResponse(
                agent_name=self.name,
                success=all(r.get('success', False) for r in results),
                result=results,
                execution_time=execution_time,
                metadata={'actions_executed': len(actions)}
            )
            
            self.log_execution(instruction, response)
            return response
            
        except Exception as e:
            logger.error(f"Browser agent error: {str(e)}")
            return AgentResponse(
                agent_name=self.name,
                success=False,
                result=None,
                error=str(e)
            )
    
    async def _parse_instruction_to_actions(self, instruction: TaskInstruction) -> List[Dict]:
        """Parse natural language instruction into browser actions"""
        text = instruction.instruction.lower()
        actions = []
        
        # Example: "open chrome and go to gmail"
        if "chrome" in text or "browser" in text:
            actions.append({'type': 'open_browser', 'browser': 'chrome'})
        
        if "firefox" in text:
            actions.append({'type': 'open_browser', 'browser': 'firefox'})
        
        # Example: "go to gmail" or "navigate to https://gmail.com"
        if "gmail" in text:
            actions.append({'type': 'navigate', 'url': 'https://gmail.com'})
        
        # Example: "login with credentials" - would need secure credential storage
        if "login" in text:
            actions.append({'type': 'login', 'service': 'gmail'})
        
        # Example: "open first email"
        if "first email" in text or "first mail" in text:
            actions.append({'type': 'click_first_email'})
        
        return actions
    
    async def _execute_browser_action(self, action: Dict, instruction: TaskInstruction) -> Dict:
        """Execute a specific browser action"""
        try:
            if action['type'] == 'open_browser':
                return await self._open_browser(action.get('browser', 'chrome'))
            
            elif action['type'] == 'navigate':
                return await self._navigate_to_url(action['url'])
            
            elif action['type'] == 'login':
                return await self._handle_login(action['service'], instruction)
            
            elif action['type'] == 'click_first_email':
                return await self._click_first_email()
            
            else:
                return {'success': False, 'error': f"Unknown action type: {action['type']}"}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _open_browser(self, browser: str = 'chrome') -> Dict:
        """Open a web browser"""
        try:
            if self.driver:
                self.driver.quit()
            
            if browser.lower() == 'chrome':
                options = ChromeOptions()
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                # Remove headless for user interaction
                # options.add_argument('--headless')  
                self.driver = webdriver.Chrome(options=options)
            else:  # firefox
                options = FirefoxOptions()
                # options.add_argument('--headless')
                self.driver = webdriver.Firefox(options=options)
            
            self.current_browser = browser
            return {'success': True, 'message': f'Opened {browser} browser'}
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to open browser: {str(e)}'}
    
    async def _navigate_to_url(self, url: str) -> Dict:
        """Navigate to a specific URL"""
        if not self.driver:
            await self._open_browser()
        
        try:
            self.driver.get(url)
            return {'success': True, 'message': f'Navigated to {url}', 'current_url': self.driver.current_url}
        except Exception as e:
            return {'success': False, 'error': f'Failed to navigate to {url}: {str(e)}'}
    
    async def _handle_login(self, service: str, instruction: TaskInstruction) -> Dict:
        """Handle login process - would need secure credential management"""
        # Note: This is a placeholder - in production, you'd want secure credential storage
        if service == 'gmail':
            try:
                # Wait for login elements to be present
                wait = WebDriverWait(self.driver, 10)
                
                # This would need actual credential management
                return {
                    'success': True, 
                    'message': 'Login process initiated - manual intervention may be required for security',
                    'note': 'Automated login requires secure credential storage implementation'
                }
            except Exception as e:
                return {'success': False, 'error': f'Login failed: {str(e)}'}
    
    async def _click_first_email(self) -> Dict:
        """Click on the first email in Gmail inbox"""
        try:
            wait = WebDriverWait(self.driver, 10)
            # Gmail inbox structure may vary, this is a general approach
            first_email = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[role="main"] tr:first-child'))
            )
            first_email.click()
            return {'success': True, 'message': 'Clicked on first email'}
        except Exception as e:
            return {'success': False, 'error': f'Failed to click first email: {str(e)}'}
    
    def __del__(self):
        """Cleanup browser driver"""
        if self.driver:
            self.driver.quit()

class PersonalAssistantOrchestrator:
    """Main orchestrator that coordinates all agents"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.agents: List[BaseAgent] = []
        self.gemini_client = self._init_gemini_client()
        self.learning_data = self._load_learning_data()
        self._initialize_agents()
        
        logger.info("Personal Assistant Orchestrator initialized")
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from file or use defaults"""
        default_config = {
            'gemini': {
                'api_key': os.getenv('GEMINI_API_KEY'),
                'model': 'gemini-pro',
                'use_local_llm': False,
                'local_llm_endpoint': 'http://localhost:11434'  # Ollama default
            },
            'browser': {
                'default_browser': 'chrome',
                'headless': False,
                'timeout': 30
            },
            'system': {
                'safe_mode': True,
                'allowed_directories': ['~/Desktop', '~/Documents', '~/Downloads'],
                'max_execution_time': 300
            },
            'learning': {
                'enabled': True,
                'data_file': '/tmp/assistant_learning.json'
            }
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f)
            default_config.update(user_config)
        
        return default_config
    
    def _init_gemini_client(self):
        """Initialize Gemini CLI client"""
        # This would integrate with the Gemini CLI tool
        # For now, return a placeholder
        return None
    
    def _load_learning_data(self) -> Dict:
        """Load learning data from previous interactions"""
        learning_file = self.config['learning']['data_file']
        if os.path.exists(learning_file):
            try:
                with open(learning_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.warning("Invalid learning data file, starting fresh")
        
        return {'user_patterns': {}, 'successful_commands': [], 'failed_commands': []}
    
    def _save_learning_data(self):
        """Save learning data for future use"""
        if self.config['learning']['enabled']:
            learning_file = self.config['learning']['data_file']
            with open(learning_file, 'w') as f:
                json.dump(self.learning_data, f, indent=2)
    
    def _initialize_agents(self):
        """Initialize all available agents"""
        self.agents = [
            SystemAgent(gemini_client=self.gemini_client),
            BrowserAgent(gemini_client=self.gemini_client),
        ]
        
        logger.info(f"Initialized {len(self.agents)} agents: {[agent.name for agent in self.agents]}")
    
    async def process_instruction(self, instruction_text: str) -> Dict[str, Any]:
        """Main method to process user instructions"""
        instruction = TaskInstruction(instruction=instruction_text)
        
        logger.info(f"Processing instruction: {instruction_text}")
        
        # Determine which agents can handle this instruction
        capable_agents = []
        for agent in self.agents:
            if await agent.can_handle(instruction):
                capable_agents.append(agent)
        
        if not capable_agents:
            return {
                'success': False,
                'message': 'No agents available to handle this instruction',
                'instruction': instruction_text,
                'suggestions': self._get_instruction_suggestions(instruction_text)
            }
        
        # Execute with capable agents
        results = []
        for agent in capable_agents:
            try:
                result = await agent.execute(instruction)
                results.append({
                    'agent': agent.name,
                    'result': asdict(result)
                })
                
                # Learn from successful executions
                if result.success:
                    self._learn_from_execution(instruction, agent, result)
                
            except Exception as e:
                logger.error(f"Error executing with {agent.name}: {str(e)}")
                results.append({
                    'agent': agent.name,
                    'result': {
                        'success': False,
                        'error': str(e)
                    }
                })
        
        # Save learning data
        self._save_learning_data()
        
        return {
            'success': any(r['result']['success'] for r in results),
            'instruction': instruction_text,
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
    
    def _learn_from_execution(self, instruction: TaskInstruction, agent: BaseAgent, result: AgentResponse):
        """Learn from successful executions to improve future performance"""
        pattern_key = f"{agent.name}_{instruction.instruction[:50]}"
        
        if pattern_key not in self.learning_data['user_patterns']:
            self.learning_data['user_patterns'][pattern_key] = {
                'count': 0,
                'success_rate': 0.0,
                'avg_execution_time': 0.0,
                'last_used': None
            }
        
        pattern_data = self.learning_data['user_patterns'][pattern_key]
        pattern_data['count'] += 1
        pattern_data['last_used'] = datetime.now().isoformat()
        
        if result.execution_time:
            pattern_data['avg_execution_time'] = (
                (pattern_data['avg_execution_time'] * (pattern_data['count'] - 1) + result.execution_time) /
                pattern_data['count']
            )
        
        if result.success:
            pattern_data['success_rate'] = (
                (pattern_data['success_rate'] * (pattern_data['count'] - 1) + 1.0) /
                pattern_data['count']
            )
    
    def _get_instruction_suggestions(self, instruction: str) -> List[str]:
        """Provide suggestions for unsupported instructions"""
        suggestions = [
            "Try: 'check if file exists in desktop'",
            "Try: 'open chrome and go to gmail'", 
            "Try: 'list files in current directory'",
            "Try: 'find all python files'",
            "Try: 'show disk space'",
        ]
        
        # Add learned patterns as suggestions
        for pattern_key in self.learning_data['user_patterns']:
            if self.learning_data['user_patterns'][pattern_key]['success_rate'] > 0.8:
                # Extract original instruction from pattern
                original = pattern_key.split('_', 1)[1]
                suggestions.append(f"Similar to: '{original}...'")
        
        return suggestions[:5]  # Return top 5 suggestions

    async def interactive_mode(self):
        """Start interactive mode for continuous conversation"""
        print("🤖 Personal Assistant initialized!")
        print("💡 Try commands like:")
        print("   - 'do we have college-photo.jpg in desktop'")
        print("   - 'open chrome and go to gmail'")
        print("   - 'list all python files in current directory'")
        print("   - Type 'quit' to exit\n")
        
        while True:
            try:
                instruction = input("You: ").strip()
                
                if instruction.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Goodbye!")
                    break
                
                if not instruction:
                    continue
                
                print("🔄 Processing...")
                result = await self.process_instruction(instruction)
                
                if result['success']:
                    print("✅ Task completed successfully!")
                    for agent_result in result['results']:
                        if agent_result['result']['success']:
                            print(f"   📋 {agent_result['agent']}: {agent_result['result']['result']}")
                else:
                    print("❌ Task failed or partially completed:")
                    for agent_result in result['results']:
                        if 'error' in agent_result['result']:
                            print(f"   ⚠️  {agent_result['agent']}: {agent_result['result']['error']}")
                    
                    if 'suggestions' in result:
                        print("\n💭 Suggestions:")
                        for suggestion in result['suggestions']:
                            print(f"   • {suggestion}")
                
                print()  # Empty line for readability
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")

async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Personal Assistant AI Agent Orchestrator')
    parser.add_argument('--config', type=str, help='Path to configuration file')
    parser.add_argument('--instruction', type=str, help='Single instruction to execute')
    parser.add_argument('--interactive', action='store_true', default=True, 
                       help='Start in interactive mode (default)')
    
    args = parser.parse_args()
    
    # Initialize the orchestrator
    orchestrator = PersonalAssistantOrchestrator(config_path=args.config)
    
    if args.instruction:
        # Execute single instruction
        result = await orchestrator.process_instruction(args.instruction)
        print(json.dumps(result, indent=2))
    else:
        # Start interactive mode
        await orchestrator.interactive_mode()

if __name__ == "__main__":
    asyncio.run(main())