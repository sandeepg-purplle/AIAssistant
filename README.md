# 🤖 Personal Assistant - AI Agent Orchestrator

A comprehensive personal assistant that understands natural language instructions and orchestrates multiple AI agents to complete complex tasks across your system and browsers.

## ✨ Features

### 🧠 **Intelligent Agent Orchestration**
- **Multi-Agent Architecture**: Coordinates specialized agents for different tasks
- **Natural Language Understanding**: Processes plain English instructions
- **Task Decomposition**: Breaks complex requests into actionable steps
- **Learning & Adaptation**: Improves performance based on your usage patterns

### 🖥️ **System Integration**
- **Terminal Operations**: Execute safe system commands and file operations
- **File System Navigation**: Find files, check directories, manage disk space
- **Process Monitoring**: Check running processes, system resources
- **Git Integration**: Status checks, commit history, repository management

### 🌐 **Browser Automation**
- **Multi-Browser Support**: Chrome, Firefox automation
- **Web Navigation**: URL navigation, page interactions
- **Login Automation**: Secure credential management (with proper setup)
- **Email Management**: Gmail integration for checking and managing emails

### 🤖 **Gemini CLI Integration**
- **Enhanced Understanding**: Leverages Gemini's language capabilities
- **Code Analysis**: Understand and generate code snippets
- **Context-Aware Responses**: Better instruction parsing with context
- **Multi-modal Support**: Text, images, and document understanding

### 🎯 **Example Use Cases**
- *"Do we have college-photo.jpg in desktop?"* → Navigates to Desktop, searches for file
- *"Open Chrome and log into Gmail"* → Opens browser, navigates to Gmail
- *"Find all Python files that import numpy"* → System search with filtering
- *"Check if the development server is running"* → Process monitoring and port checking
- *"Create a summary of today's git commits"* → Git integration with AI summarization

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 20+ (for Gemini CLI integration)
- Chrome or Firefox browser (for web automation)

### Automatic Setup
```bash
# Clone or download the project
git clone <your-repo-url>
cd personal-assistant

# Run the setup script
chmod +x setup.sh
./setup.sh
```

### Manual Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Gemini CLI
npm install -g @google/gemini-cli

# Copy and configure environment
cp .env.example .env
# Edit .env with your API keys and preferences
```

### Configuration
1. **Get Gemini API Key**: Visit [Google AI Studio](https://aistudio.google.com/apikey)
2. **Edit `.env` file**: Add your API key and configuration preferences
3. **Browser Setup**: Ensure Chrome/Firefox is installed for web automation
4. **Optional**: Install [Ollama](https://ollama.ai/) for local LLM support

## 🎮 Usage

### Interactive Mode (Recommended)
```bash
# Using the run script
./run_assistant.sh --interactive

# Or directly with Python
python personal_assistant.py --interactive
```

### Single Command Mode
```bash
# Execute a single instruction
python personal_assistant.py --instruction "find all python files in current directory"

# With configuration file
python personal_assistant.py --config config.yaml --instruction "check disk space"
```

### Example Commands
```bash
# File operations
"do we have report.pdf in documents?"
"list all image files in desktop"
"find files containing 'config'"

# System monitoring  
"show running processes"
"check memory usage"
"display disk space"

# Browser automation
"open chrome and go to gmail"
"navigate to github.com"
"check my emails"

# Development tasks
"find all python files with import errors"
"show git status and recent commits"
"check if port 8080 is in use"
```

## 🏗️ Architecture

### Agent System
```
PersonalAssistantOrchestrator
├── SystemAgent (Terminal & File Operations)
├── BrowserAgent (Web Automation)  
├── GeminiCLIClient (Enhanced AI Understanding)
└── EnhancedPromptEngine (Context-Aware Processing)
```

### Core Components

#### **SystemAgent**
- Safe command execution with whitelist approach
- File system navigation and search
- Process monitoring and system information
- Git integration for repository management

#### **BrowserAgent** 
- Multi-browser automation (Chrome, Firefox)
- Web navigation and interaction
- Secure login handling (requires credential setup)
- Email and web application automation

#### **GeminiCLIClient**
- Natural language instruction parsing
- Context-aware command generation
- Code analysis and generation
- Learning from execution patterns

#### **Learning System**
- Tracks user interaction patterns
- Adapts to frequently used commands
- Improves success rates over time
- Provides personalized suggestions

## ⚙️ Configuration

### Main Configuration (`config.yaml`)
```yaml
gemini:
  api_key: ${GEMINI_API_KEY}
  model: "gemini-pro"
  use_gemini_cli: true

browser:
  default_browser: "chrome"
  headless: false
  timeout: 30

system:
  safe_mode: true
  allowed_directories: ["~/Desktop", "~/Documents", "~/Downloads"]
  max_execution_time: 300

learning:
  enabled: true
  data_file: "/tmp/assistant_learning.json"
```

### Environment Variables (`.env`)
```bash
GEMINI_API_KEY=your_api_key_here
GOOGLE_CLOUD_PROJECT=your_project_id
OLLAMA_ENDPOINT=http://localhost:11434
DEFAULT_BROWSER=chrome
LOG_LEVEL=INFO
```

## 🔒 Security Features

### Safe Command Execution
- Whitelist-based command filtering
- Read-only operations by default
- Confirmation required for destructive actions
- Sandboxed execution environment

### Credential Management
- System keyring integration
- Encrypted credential storage
- OAuth flow support for web services
- No plaintext password storage

### Browser Security
- Isolated browser sessions
- Secure login handling
- User confirmation for sensitive operations
- Optional headless mode for automation

## 🧪 Testing & Examples

### Run Examples
```bash
# Show usage examples
python examples.py --examples

# Run specific demo
python examples.py --demo system
python examples.py --demo browser
python examples.py --demo learning

# Run all demonstrations
python examples.py --demo all
```

### Test Gemini Integration
```bash
# Test Gemini CLI availability
python gemini_integration.py

# Test with specific instruction
python -c "
import asyncio
from gemini_integration import GeminiCLIClient
client = GeminiCLIClient()
asyncio.run(client.chat('How can I automate my daily tasks?'))
"
```

## 🚀 Advanced Features

### CrewAI Integration (Coming Soon)
- Multi-agent task delegation
- Specialized agent roles
- Complex workflow orchestration
- Team collaboration patterns

### Local LLM Support
- Ollama integration for privacy
- Custom model fine-tuning
- Offline operation capabilities
- Reduced API dependencies

### Web Scraping & Automation
- Intelligent form filling
- Data extraction from web pages
- Scheduled task execution
- Multi-site workflow automation

### Voice Interface (Planned)
- Speech-to-text instruction input
- Text-to-speech responses
- Hands-free operation
- Voice command customization

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** with proper documentation
4. **Add tests** for new functionality
5. **Submit a pull request**

### Development Setup
```bash
# Clone your fork
git clone <your-fork-url>
cd personal-assistant

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Run linting
black . && flake8 .
```

## 📝 Roadmap

### Phase 1: Core Foundation ✅
- [x] Multi-agent architecture
- [x] System command execution
- [x] Browser automation basics
- [x] Gemini CLI integration

### Phase 2: Enhanced Intelligence 🔄
- [ ] Advanced natural language understanding
- [ ] Context-aware task planning
- [ ] Improved learning algorithms
- [ ] Voice interface integration

### Phase 3: Ecosystem Integration 📋
- [ ] n8n workflow integration
- [ ] Slack/Discord bot capabilities
- [ ] Calendar and email management
- [ ] Cloud service integrations

### Phase 4: Advanced Automation 📋
- [ ] Custom agent development framework
- [ ] Visual workflow builder
- [ ] Mobile app companion
- [ ] Enterprise deployment options

## 🐛 Troubleshooting

### Common Issues

#### Gemini CLI Not Found
```bash
# Install Gemini CLI
npm install -g @google/gemini-cli

# Verify installation
gemini --version

# Set up authentication
gemini  # Follow OAuth setup
```

#### Browser Driver Issues
```bash
# Update Chrome driver
pip install --upgrade webdriver-manager

# For manual ChromeDriver setup:
# Download from: https://chromedriver.chromium.org/
```

#### Permission Errors
```bash
# Make scripts executable
chmod +x setup.sh run_assistant.sh

# Fix Python path issues
which python3
export PATH="/usr/bin:$PATH"
```

#### Module Import Errors
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Debug Mode
```bash
# Run with debug logging
DEBUG=true python personal_assistant.py --interactive

# Check logs
tail -f /tmp/personal_assistant.log
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[Gemini CLI](https://github.com/google-gemini/gemini-cli)** - For providing excellent AI integration
- **[CrewAI](https://github.com/joaomdmoura/crewai)** - For multi-agent orchestration framework
- **[Selenium](https://selenium.dev/)** - For reliable browser automation
- **OpenAI Community** - For inspiration and best practices

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-username/personal-assistant/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/personal-assistant/discussions)
- **Documentation**: [Wiki](https://github.com/your-username/personal-assistant/wiki)

---

<div align="center">
<strong>Built with ❤️ for automating your daily tasks</strong>
<br>
<em>Making AI assistance accessible and powerful for everyone</em>
</div>