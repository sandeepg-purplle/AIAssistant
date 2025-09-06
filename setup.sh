#!/bin/bash
# Personal Assistant Setup Script
# Installs dependencies and sets up the personal assistant system

set -e  # Exit on any error

echo "🚀 Personal Assistant Setup"
echo "========================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if Python 3.8+ is installed
print_step "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    print_status "Python $PYTHON_VERSION found"
    
    # Check if version is 3.8 or higher
    if python3 -c 'import sys; exit(not (sys.version_info >= (3, 8)))'; then
        print_status "Python version is compatible"
    else
        print_error "Python 3.8+ is required. Please upgrade Python."
        exit 1
    fi
else
    print_error "Python 3 is not installed. Please install Python 3.8+"
    exit 1
fi

# Check if Node.js is installed (for Gemini CLI)
print_step "Checking Node.js for Gemini CLI..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_status "Node.js $NODE_VERSION found"
else
    print_warning "Node.js not found. Gemini CLI integration will not be available."
    print_warning "Install Node.js 20+ from: https://nodejs.org/"
fi

# Create virtual environment
print_step "Creating Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_status "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
print_step "Activating virtual environment..."
source venv/bin/activate
print_status "Virtual environment activated"

# Upgrade pip
print_step "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
print_status "Pip upgraded"

# Install Python dependencies
print_step "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt > /dev/null 2>&1
    print_status "Python dependencies installed"
else
    print_error "requirements.txt not found"
    exit 1
fi

# Install Gemini CLI if Node.js is available
if command -v npm &> /dev/null; then
    print_step "Installing Gemini CLI..."
    npm install -g @google/gemini-cli > /dev/null 2>&1 || print_warning "Failed to install Gemini CLI globally. You may need sudo."
    
    # Check if installation was successful
    if command -v gemini &> /dev/null; then
        print_status "Gemini CLI installed successfully"
    else
        print_warning "Gemini CLI installation may have failed"
    fi
fi

# Install browser drivers
print_step "Setting up browser drivers..."

# Install ChromeDriver
if command -v google-chrome &> /dev/null || command -v chromium-browser &> /dev/null; then
    pip install webdriver-manager > /dev/null 2>&1
    print_status "Chrome WebDriver manager installed"
else
    print_warning "Chrome browser not found. Browser automation may be limited."
fi

# Check for Firefox
if command -v firefox &> /dev/null; then
    print_status "Firefox browser found"
else
    print_warning "Firefox browser not found"
fi

# Create necessary directories
print_step "Creating directories..."
mkdir -p logs
mkdir -p data
mkdir -p config
print_status "Directories created"

# Create default environment file
print_step "Creating environment configuration..."
if [ ! -f ".env" ]; then
    cat > .env << EOL
# Personal Assistant Environment Configuration

# Gemini API Configuration
# Get your API key from: https://aistudio.google.com/apikey
GEMINI_API_KEY=your_gemini_api_key_here

# Google Cloud Configuration (optional)
# GOOGLE_CLOUD_PROJECT=your_project_id

# Local LLM Configuration (Ollama)
OLLAMA_ENDPOINT=http://localhost:11434
OLLAMA_MODEL=llama2

# Security and Authentication
USE_SYSTEM_KEYRING=true
ENCRYPT_CREDENTIALS=true

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/personal_assistant.log

# Browser Configuration
DEFAULT_BROWSER=chrome
BROWSER_HEADLESS=false

# Development
DEBUG=false
EOL
    print_status "Environment file created (.env)"
    print_warning "Please edit .env file to add your API keys and configuration"
else
    print_status "Environment file already exists"
fi

# Create a simple run script
print_step "Creating run script..."
cat > run_assistant.sh << 'EOL'
#!/bin/bash
# Personal Assistant Launcher

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | xargs)
fi

# Run the assistant
python personal_assistant.py "$@"
EOL

chmod +x run_assistant.sh
print_status "Run script created (run_assistant.sh)"

# Test installation
print_step "Testing installation..."
if python -c "import personal_assistant" 2>/dev/null; then
    print_status "Personal assistant module loads successfully"
else
    print_error "Failed to load personal assistant module"
fi

# Create desktop shortcut (Linux)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    print_step "Creating desktop shortcut..."
    DESKTOP_FILE="$HOME/Desktop/Personal-Assistant.desktop"
    CURRENT_DIR=$(pwd)
    
    cat > "$DESKTOP_FILE" << EOL
[Desktop Entry]
Version=1.0
Type=Application
Name=Personal Assistant
Comment=AI-powered personal assistant
Exec=$CURRENT_DIR/run_assistant.sh
Icon=applications-utilities
Terminal=true
Categories=Utility;
EOL
    
    chmod +x "$DESKTOP_FILE"
    print_status "Desktop shortcut created"
fi

echo ""
echo "✅ Setup completed successfully!"
echo ""
print_status "Next steps:"
echo "  1. Edit .env file to add your Gemini API key"
echo "  2. Run: ./run_assistant.sh --interactive"
echo "  3. Or run: python examples.py --examples (to see usage examples)"
echo ""
print_status "For Gemini CLI authentication:"
echo "  Run: gemini (and follow the OAuth setup)"
echo "  Or set GEMINI_API_KEY in your .env file"
echo ""
print_status "Optional: Install Ollama for local LLM support:"
echo "  Visit: https://ollama.ai/"
echo ""
print_warning "Make sure to configure your browser drivers if you plan to use browser automation"
echo ""
echo "🎉 Your personal assistant is ready to use!"