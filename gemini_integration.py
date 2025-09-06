#!/usr/bin/env python3
"""
Gemini CLI Integration Module

This module provides integration with the Gemini CLI tool for enhanced
natural language understanding and code generation capabilities.

Features:
- Direct integration with Gemini CLI
- Context-aware prompt engineering
- Code understanding and generation
- Multi-modal capabilities (text, images, PDFs)
- Conversation checkpointing
"""

import asyncio
import json
import logging
import os
import subprocess
import tempfile
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)

@dataclass
class GeminiResponse:
    """Response from Gemini CLI"""
    success: bool
    content: str
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None

class GeminiCLIClient:
    """Client for interacting with Gemini CLI"""
    
    def __init__(self, 
                 gemini_cli_path: str = "gemini",
                 model: str = "gemini-pro",
                 project_id: Optional[str] = None,
                 api_key: Optional[str] = None):
        self.gemini_cli_path = gemini_cli_path
        self.model = model
        self.project_id = project_id or os.getenv('GOOGLE_CLOUD_PROJECT')
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        # Check if Gemini CLI is available
        self.available = self._check_availability()
        if not self.available:
            logger.warning("Gemini CLI not available. Some features may be limited.")
    
    def _check_availability(self) -> bool:
        """Check if Gemini CLI is installed and accessible"""
        try:
            result = subprocess.run([self.gemini_cli_path, "--version"], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return False
    
    async def chat(self, prompt: str, 
                   context: Optional[str] = None,
                   include_files: Optional[List[str]] = None) -> GeminiResponse:
        """Send a chat message to Gemini CLI"""
        if not self.available:
            return GeminiResponse(
                success=False,
                content="",
                error="Gemini CLI not available"
            )
        
        try:
            # Build command
            cmd = [self.gemini_cli_path]
            
            # Add model if specified
            if self.model:
                cmd.extend(["-m", self.model])
            
            # Add project ID if specified
            if self.project_id:
                os.environ['GOOGLE_CLOUD_PROJECT'] = self.project_id
            
            # Add API key if specified
            if self.api_key:
                os.environ['GEMINI_API_KEY'] = self.api_key
            
            # Include files in context
            if include_files:
                for file_path in include_files:
                    if os.path.exists(file_path):
                        cmd.extend(["--include-directories", os.path.dirname(file_path)])
            
            # Add context if provided
            full_prompt = prompt
            if context:
                full_prompt = f"Context: {context}\n\nQuery: {prompt}"
            
            # Use non-interactive mode
            cmd.extend(["-p", full_prompt])
            
            # Execute command
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=os.environ.copy()
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=120
            )
            
            if process.returncode == 0:
                return GeminiResponse(
                    success=True,
                    content=stdout.decode('utf-8').strip(),
                    model_used=self.model
                )
            else:
                return GeminiResponse(
                    success=False,
                    content="",
                    error=stderr.decode('utf-8').strip()
                )
                
        except asyncio.TimeoutError:
            return GeminiResponse(
                success=False,
                content="",
                error="Gemini CLI request timed out"
            )
        except Exception as e:
            return GeminiResponse(
                success=False,
                content="",
                error=f"Gemini CLI error: {str(e)}"
            )
    
    async def analyze_code(self, 
                          code_content: str,
                          language: Optional[str] = None,
                          task: str = "analyze") -> GeminiResponse:
        """Analyze code using Gemini CLI"""
        language_hint = f" (Language: {language})" if language else ""
        
        prompts = {
            "analyze": f"Analyze this code{language_hint} and explain what it does:\n\n```\n{code_content}\n```",
            "debug": f"Debug this code{language_hint} and suggest fixes:\n\n```\n{code_content}\n```",
            "optimize": f"Optimize this code{language_hint} for better performance:\n\n```\n{code_content}\n```",
            "explain": f"Explain this code{language_hint} in simple terms:\n\n```\n{code_content}\n```"
        }
        
        prompt = prompts.get(task, prompts["analyze"])
        return await self.chat(prompt)
    
    async def generate_code(self, 
                           description: str,
                           language: str = "python",
                           context: Optional[str] = None) -> GeminiResponse:
        """Generate code based on description"""
        prompt = f"Generate {language} code for: {description}"
        
        if context:
            prompt += f"\n\nAdditional context:\n{context}"
        
        return await self.chat(prompt)
    
    async def understand_instruction(self, 
                                   instruction: str,
                                   available_agents: List[str]) -> GeminiResponse:
        """Use Gemini to understand user instructions and suggest agent actions"""
        context = f"""
You are helping to parse user instructions for a personal assistant system.

Available agents: {', '.join(available_agents)}

For each instruction, determine:
1. Which agent(s) should handle it
2. What specific actions should be taken
3. Any parameters or context needed
4. Priority level (low, normal, high, urgent)

Respond in JSON format with this structure:
{{
  "agents": ["agent_name1", "agent_name2"],
  "actions": [
    {{
      "agent": "agent_name",
      "action": "specific_action",
      "parameters": {{"key": "value"}},
      "description": "what this action does"
    }}
  ],
  "priority": "normal",
  "estimated_duration": 30,
  "requires_confirmation": false
}}
        """
        
        prompt = f"Parse this instruction: '{instruction}'"
        
        response = await self.chat(prompt, context=context)
        
        if response.success:
            try:
                # Try to parse JSON response
                parsed = json.loads(response.content)
                response.metadata = {"parsed_instruction": parsed}
            except json.JSONDecodeError:
                # If not JSON, keep original response
                pass
        
        return response
    
    async def learn_from_execution(self, 
                                  instruction: str,
                                  execution_results: List[Dict],
                                  success: bool) -> GeminiResponse:
        """Learn from execution results to improve future performance"""
        context = f"""
You are helping a personal assistant learn from execution results.

Original instruction: {instruction}
Execution results: {json.dumps(execution_results, indent=2)}
Overall success: {success}

Analyze what went well and what could be improved. Suggest optimizations
for handling similar instructions in the future.
        """
        
        prompt = "Analyze this execution and suggest improvements"
        
        return await self.chat(prompt, context=context)
    
    async def generate_system_commands(self, 
                                     instruction: str,
                                     current_directory: Optional[str] = None,
                                     available_files: Optional[List[str]] = None) -> GeminiResponse:
        """Generate system commands based on natural language instruction"""
        context = f"""
You are helping to translate natural language instructions into safe system commands.

Current directory: {current_directory or 'unknown'}
Available files: {available_files[:10] if available_files else 'unknown'}

Generate safe shell commands that accomplish the user's request.
ONLY suggest safe, read-only commands unless explicitly asked for modifications.

Safe commands include: ls, cd, find, grep, cat, head, tail, ps, df, du, which, etc.
AVOID: rm, del, sudo, chmod with dangerous permissions, etc.

Return commands as a JSON array: ["command1", "command2"]
        """
        
        prompt = f"Generate commands for: '{instruction}'"
        
        response = await self.chat(prompt, context=context)
        
        if response.success:
            try:
                # Try to extract JSON from response
                json_match = re.search(r'\[(.*?)\]', response.content, re.DOTALL)
                if json_match:
                    commands = json.loads(json_match.group(0))
                    response.metadata = {"commands": commands}
            except (json.JSONDecodeError, AttributeError):
                # If no JSON found, try to extract commands from text
                lines = response.content.split('\n')
                commands = []
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#') and not line.startswith('//'):
                        # Remove common prefixes
                        for prefix in ['$', '>', '>>>']:
                            if line.startswith(prefix):
                                line = line[len(prefix):].strip()
                        if line:
                            commands.append(line)
                
                response.metadata = {"commands": commands[:5]}  # Limit to 5 commands
        
        return response
    
    async def generate_browser_actions(self, 
                                     instruction: str,
                                     current_url: Optional[str] = None,
                                     page_context: Optional[str] = None) -> GeminiResponse:
        """Generate browser automation actions based on instruction"""
        context = f"""
You are helping to translate natural language instructions into browser automation actions.

Current URL: {current_url or 'not specified'}
Page context: {page_context or 'not specified'}

Generate browser actions that accomplish the user's request.
Return as JSON array of action objects:

[
  {{
    "type": "navigate|click|type|wait|scroll",
    "selector": "CSS selector or element description",
    "value": "text to type (if applicable)",
    "description": "what this action does"
  }}
]

Common action types:
- navigate: go to URL
- click: click element
- type: enter text
- wait: wait for element
- scroll: scroll page
        """
        
        prompt = f"Generate browser actions for: '{instruction}'"
        
        response = await self.chat(prompt, context=context)
        
        if response.success:
            try:
                # Try to parse JSON response
                json_match = re.search(r'\[(.*?)\]', response.content, re.DOTALL)
                if json_match:
                    actions = json.loads(json_match.group(0))
                    response.metadata = {"actions": actions}
            except (json.JSONDecodeError, AttributeError):
                pass
        
        return response

class EnhancedPromptEngine:
    """Enhanced prompt engineering for better Gemini interactions"""
    
    def __init__(self, gemini_client: GeminiCLIClient):
        self.gemini_client = gemini_client
        self.conversation_history: List[Dict] = []
    
    def build_context_prompt(self, 
                           instruction: str,
                           system_context: Optional[Dict] = None,
                           user_history: Optional[List[str]] = None) -> str:
        """Build a context-aware prompt for better understanding"""
        
        prompt_parts = []
        
        # System context
        if system_context:
            prompt_parts.append("SYSTEM CONTEXT:")
            prompt_parts.append(f"Current directory: {system_context.get('cwd', 'unknown')}")
            prompt_parts.append(f"Operating system: {system_context.get('os', 'unknown')}")
            prompt_parts.append(f"Available tools: {', '.join(system_context.get('tools', []))}")
            prompt_parts.append("")
        
        # User history (for learning patterns)
        if user_history:
            prompt_parts.append("RECENT USER PATTERNS:")
            for i, hist_instruction in enumerate(user_history[-3:], 1):
                prompt_parts.append(f"{i}. {hist_instruction}")
            prompt_parts.append("")
        
        # Main instruction
        prompt_parts.append("USER INSTRUCTION:")
        prompt_parts.append(instruction)
        
        return "\n".join(prompt_parts)
    
    async def optimize_instruction_understanding(self, 
                                               instruction: str,
                                               context: Dict) -> GeminiResponse:
        """Use advanced prompt engineering to understand complex instructions"""
        
        enhanced_prompt = f"""
You are an expert personal assistant AI that understands complex multi-step instructions.

Your task is to break down the user's instruction into actionable steps and determine
the best approach to accomplish their goal.

CAPABILITIES:
- System command execution (safe commands only)
- Web browser automation (Chrome/Firefox)
- File system navigation and search
- Learning from user behavior patterns

CURRENT CONTEXT:
{json.dumps(context, indent=2)}

USER INSTRUCTION: "{instruction}"

Please analyze this instruction and provide:
1. Intent analysis: What is the user trying to accomplish?
2. Required steps: Break down into specific actions
3. Agent assignments: Which agent should handle each step?
4. Risk assessment: Any potential issues or confirmations needed?
5. Success criteria: How to know the task is completed?

Format your response as structured analysis.
        """
        
        return await self.gemini_client.chat(enhanced_prompt)

# Example usage and testing
async def test_gemini_integration():
    """Test the Gemini CLI integration"""
    
    print("🧪 Testing Gemini CLI Integration...")
    
    # Initialize client
    client = GeminiCLIClient()
    
    if not client.available:
        print("❌ Gemini CLI not available. Please install it first:")
        print("   npm install -g @google/gemini-cli")
        return
    
    print("✅ Gemini CLI is available")
    
    # Test basic chat
    print("\n🔹 Testing basic chat...")
    response = await client.chat("Hello! Can you help me understand how to use a personal assistant?")
    if response.success:
        print(f"✅ Chat response: {response.content[:100]}...")
    else:
        print(f"❌ Chat failed: {response.error}")
    
    # Test instruction understanding
    print("\n🔹 Testing instruction understanding...")
    instruction = "do we have college-photo.jpg in desktop"
    response = await client.understand_instruction(instruction, ["SystemAgent", "BrowserAgent"])
    if response.success:
        print(f"✅ Instruction analysis: {response.content[:200]}...")
        if response.metadata and "parsed_instruction" in response.metadata:
            print(f"📋 Parsed: {response.metadata['parsed_instruction']}")
    else:
        print(f"❌ Instruction understanding failed: {response.error}")
    
    # Test command generation
    print("\n🔹 Testing command generation...")
    response = await client.generate_system_commands(instruction, current_directory="/home/user")
    if response.success:
        print(f"✅ Generated commands: {response.content[:200]}...")
        if response.metadata and "commands" in response.metadata:
            print(f"📋 Commands: {response.metadata['commands']}")
    else:
        print(f"❌ Command generation failed: {response.error}")
    
    print("\n✨ Gemini CLI integration test completed!")

if __name__ == "__main__":
    asyncio.run(test_gemini_integration())