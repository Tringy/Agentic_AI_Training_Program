# Getting Started

Complete setup guide to prepare for the GenAI Engineering Training Program.

---

## 📋 Pre-Training Checklist

Before Day 1, ensure you have:

- [ ] System requirements met
- [ ] Required software installed
- [ ] API keys obtained
- [ ] Repository cloned
- [ ] Environment configured
- [ ] Setup verified

**Time Required:** 30-60 minutes

---

## 🖥️ System Requirements

### Minimum Specifications

| Component | Requirement |
|-----------|-------------|
| **OS** | macOS 10.15+, Windows 10+, or Linux (Ubuntu 20.04+) |
| **RAM** | 8 GB minimum, 16 GB recommended |
| **Storage** | 10 GB free space |
| **Internet** | Stable broadband connection |
| **Browser** | Chrome, Firefox, or Safari (latest version) |

### Recommended Setup

- **IDE/Editor:** VS Code, Cursor, or your preferred editor
- **Terminal:** iTerm2 (Mac), Windows Terminal, or built-in terminal
- **Git Client:** Command line or GitHub Desktop

---

## 🛠️ Software Installation

### 1. Install Python 3.10+

<details>
<summary><b>macOS</b></summary>

```bash
# Using Homebrew (recommended)
brew install python@3.11

# Verify installation
python3 --version
# Should show: Python 3.11.x or higher
```

</details>

<details>
<summary><b>Windows</b></summary>

1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run installer
3. **Important:** Check "Add Python to PATH"
4. Verify in PowerShell:

```powershell
python --version
# Should show: Python 3.11.x or higher
```

</details>

<details>
<summary><b>Linux (Ubuntu/Debian)</b></summary>

```bash
# Update package list
sudo apt update

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip

# Verify installation
python3 --version
```

</details>

### 2. Install Node.js 18+

<details>
<summary><b>macOS</b></summary>

```bash
# Using Homebrew
brew install node

# Verify installation
node --version  # Should show v18.x or higher
npm --version   # Should show 9.x or higher
```

</details>

<details>
<summary><b>Windows</b></summary>

1. Download Node.js from [nodejs.org](https://nodejs.org/)
2. Run installer (LTS version recommended)
3. Verify in PowerShell:

```powershell
node --version
npm --version
```

</details>

<details>
<summary><b>Linux (Ubuntu/Debian)</b></summary>

```bash
# Install Node.js 18.x
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version
npm --version
```

</details>

### 3. Install Git

<details>
<summary><b>macOS</b></summary>

```bash
# Using Homebrew
brew install git

# Or use Xcode Command Line Tools
xcode-select --install
```

</details>

<details>
<summary><b>Windows</b></summary>

Download and install from [git-scm.com](https://git-scm.com/download/win)

</details>

<details>
<summary><b>Linux</b></summary>

```bash
sudo apt install git
```

</details>

**Verify Git:**
```bash
git --version
# Should show git version 2.x or higher
```

---

## 🔑 API Keys Setup

You'll need at least ONE LLM API key. We recommend starting with free options.

### Option 1: Google AI Studio (RECOMMENDED - Most Generous Free Tier)

**Best for:** Students on a budget, generous rate limits

1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Sign in with Google account
3. Click "Get API Key"
4. Create a new API key
5. Copy and save securely

**Free Tier:**
- 60 requests per minute
- 1,500 requests per day
- No credit card required

### Option 2: Groq (RECOMMENDED - Fastest Inference)

**Best for:** Speed, experimentation

1. Visit [Groq Console](https://console.groq.com/)
2. Sign up for account
3. Navigate to API Keys section
4. Create new API key
5. Copy and save securely

**Free Tier:**
- 30 requests per minute
- 14,400 requests per day
- No credit card required

### Option 3: Ollama (Local - 100% Free)

**Best for:** Privacy, unlimited usage

1. Download from [ollama.ai](https://ollama.ai/)
2. Install application
3. Pull a model:

```bash
# Download Llama 3.1
ollama pull llama3.1

# Or download Mistral
ollama pull mistral
```

**Pros:**
- Completely free
- No rate limits
- Full privacy

**Cons:**
- Requires ~8GB RAM minimum
- Slower than cloud APIs
- Limited model selection

### Optional Paid Options

Only get these if you want access to specific models or higher rate limits.

<details>
<summary><b>Anthropic Claude (Optional)</b></summary>

1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Sign up and add payment method
3. Create API key
4. New accounts get $5 free credit

**Cost:** ~$3 per million input tokens

</details>

<details>
<summary><b>OpenAI GPT (Optional)</b></summary>

1. Visit [OpenAI Platform](https://platform.openai.com/signup)
2. Sign up and add payment method
3. Generate API key
4. New accounts may get free credits

**Cost:** ~$2.50 per million input tokens (GPT-4o)

</details>

---

## 📦 Repository Setup

### 1. Clone the Repository

```bash
# If you have access to the private repo
git clone <repository-url>
cd AI_Training

# Or if using a fork/download
cd /path/to/AI_Training
```

### 2. Verify Structure

```bash
ls -la

# You should see:
# curriculum/, guides/, labs/, templates/, etc.
```

---

## ⚙️ Environment Configuration

### 1. Create Environment File

```bash
# Copy the template
cp .env.example .env
```

### 2. Add Your API Keys

Open `.env` in your editor and add your keys:

```bash
# Google AI Studio (if using)
GOOGLE_API_KEY=your_google_api_key_here

# Groq (if using)
GROQ_API_KEY=your_groq_api_key_here

# Anthropic (optional)
ANTHROPIC_API_KEY=sk-ant-your_key_here

# OpenAI (optional)
OPENAI_API_KEY=sk-proj-your_key_here

# Ollama (if running locally)
OLLAMA_BASE_URL=http://localhost:11434
```

**Important:** Never commit your `.env` file to version control!

### 3. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
# macOS/Linux:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate

# Your prompt should now show (.venv)

# Install dependencies
pip install -r requirements.txt
```

### 4. Set Up Node.js Environment

```bash
# Install root dependencies
npm install

# This installs shared TypeScript configurations
```

---

## ✅ Verify Your Setup

### Automated Verification

Run our setup verification script:

```bash
# Make script executable (macOS/Linux)
chmod +x scripts/verify-setup.sh

# Run verification for both Python and TypeScript
./scripts/verify-setup.sh

# Or verify specific language only
./scripts/verify-setup.sh python
./scripts/verify-setup.sh typescript
```

### Manual Verification

If the script doesn't work, verify manually:

<details>
<summary><b>Check Python Setup</b></summary>

```bash
# Activate virtual environment
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Check Python version
python --version
# Expected: Python 3.10.x or higher

# Check installed packages
pip list | grep -E "anthropic|openai|langchain|fastapi"

# Test API connection (replace with your provider)
python -c "
from anthropic import Anthropic
import os
client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
print('✅ Anthropic API connection successful')
"
```

</details>

<details>
<summary><b>Check Node.js Setup</b></summary>

```bash
# Check versions
node --version  # Expected: v18.x or higher
npm --version   # Expected: 9.x or higher

# Check TypeScript
npx tsc --version

# Test a simple TypeScript compilation
echo "const x: number = 42; console.log(x);" > test.ts
npx tsc test.ts && node test.js
rm test.ts test.js
```

</details>

---

## 🎯 Choose Your Language Track

Before Day 1, decide whether you'll use **Python** or **TypeScript** for the labs.

### Decision Matrix

| Factor | Python | TypeScript |
|--------|--------|------------|
| **AI Ecosystem** | ⭐⭐⭐ Mature libraries | ⭐⭐ Growing ecosystem |
| **Type Safety** | ⭐⭐ Optional (type hints) | ⭐⭐⭐ Built-in |
| **Web Integration** | ⭐⭐ Good | ⭐⭐⭐ Excellent |
| **Learning Curve** | ⭐⭐⭐ Easier syntax | ⭐⭐ More boilerplate |
| **Performance** | ⭐⭐ Good | ⭐⭐⭐ Fast |
| **Job Market** | ⭐⭐⭐ High demand | ⭐⭐⭐ High demand |

### Recommendation

- **Choose Python if:** You're coming from ML/data science, want access to more AI libraries, or prefer simpler syntax
- **Choose TypeScript if:** You're building full-stack web apps, value type safety, or work primarily in frontend

> **Note:** You can switch languages between labs if you want to try both! Just use the appropriate directory (python/ or typescript/).

See [LANGUAGE-CHOICE-GUIDE.md](../docs/LANGUAGE-CHOICE-GUIDE.md) for detailed guidance.

---

## 🚨 Troubleshooting

### Common Issues

<details>
<summary><b>Issue: "python: command not found"</b></summary>

**Solution:**
Try `python3` instead of `python`:
```bash
python3 --version
```

Create an alias (optional):
```bash
# macOS/Linux: Add to ~/.bashrc or ~/.zshrc
alias python=python3

# Windows: Python should be added to PATH during installation
```

</details>

<details>
<summary><b>Issue: "pip: command not found"</b></summary>

**Solution:**
Try `pip3` or install pip:
```bash
# macOS/Linux
python3 -m ensurepip --upgrade

# Windows
python -m ensurepip --upgrade
```

</details>

<details>
<summary><b>Issue: Virtual environment won't activate</b></summary>

**Windows PowerShell:**
You may need to allow script execution:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**macOS/Linux:**
Ensure you're using the correct activation command:
```bash
source .venv/bin/activate
```

</details>

<details>
<summary><b>Issue: API key not working</b></summary>

**Checklist:**
- [ ] API key is correctly copied (no extra spaces)
- [ ] `.env` file is in the project root
- [ ] Environment variable name matches exactly
- [ ] You've restarted your terminal/loaded .env
- [ ] API key hasn't been revoked or rate-limited

**Test API key:**
```bash
# For Anthropic
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-3-5-sonnet-20241022","max_tokens":10,"messages":[{"role":"user","content":"Hi"}]}'
```

</details>

<details>
<summary><b>Issue: Permission denied on scripts</b></summary>

**Solution:**
Make scripts executable:
```bash
chmod +x scripts/*.sh
```

</details>

<details>
<summary><b>Issue: Port already in use</b></summary>

**Solution:**
Kill the process using the port:
```bash
# macOS/Linux
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

Or use a different port in your code.

</details>

---

## 📚 Pre-Training Reading (Optional)

Get a head start with these quick reads (30 minutes total):

### Must-Read (10 min)
- [What is an LLM?](https://www.anthropic.com/research) - Anthropic's intro
- [Prompt Engineering Basics](https://platform.openai.com/docs/guides/prompt-engineering) - OpenAI guide

### Recommended (20 min)
- [Attention is All You Need (summary)](https://blog.research.google/2017/08/transformer-novel-neural-network.html)
- [How to build an AI agent](https://www.anthropic.com/research/building-effective-agents)

**Don't stress:** These are optional! We'll cover everything during the training program.

---

## ✨ Test Your Setup

Before Day 1, run this simple test to confirm everything works:

### Python Test

Create `test_setup.py`:

```python
import os
from anthropic import Anthropic

def test_setup():
    print("🔍 Testing setup...")

    # Check API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("⚠️  ANTHROPIC_API_KEY not found in environment")
        return False

    # Test API call
    try:
        client = Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=10,
            messages=[{"role": "user", "content": "Hi"}]
        )
        print("✅ Setup successful! API is working.")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_setup()
```

Run it:
```bash
python test_setup.py
```

### TypeScript Test

Create `test-setup.ts`:

```typescript
import Anthropic from "@anthropic-ai/sdk";

async function testSetup() {
  console.log("🔍 Testing setup...");

  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    console.log("⚠️  ANTHROPIC_API_KEY not found in environment");
    return false;
  }

  try {
    const client = new Anthropic({ apiKey });
    const message = await client.messages.create({
      model: "claude-3-5-sonnet-20241022",
      max_tokens: 10,
      messages: [{ role: "user", content: "Hi" }],
    });
    console.log("✅ Setup successful! API is working.");
    return true;
  } catch (error) {
    console.log("❌ Error:", error);
    return false;
  }
}

testSetup();
```

Run it:
```bash
npx tsx test-setup.ts
```

---

## 🎯 You're Ready!

If you've completed all the steps above, you're ready for Day 1!

### Final Checklist

- [ ] All software installed and versions verified
- [ ] At least one API key obtained and tested
- [ ] Repository cloned and dependencies installed
- [ ] Environment file configured with API keys
- [ ] Test script runs successfully
- [ ] Language track chosen (Python or TypeScript)

### Next Steps

1. **Join the Community:** See [community.md](./community.md) for resources
2. **Review Day 1 Agenda:** Check [curriculum/day1-foundations.md](../curriculum/day1-foundations.md)
3. **Prepare Questions:** Think about what you want to learn
4. **Get Excited:** You're about to become an AI engineer! 🚀

---

## 📞 Need Help?

- **Technical Issues:** Check the documentation and community forums
- **API Key Problems:** Check provider's documentation
- **General Questions:** Post in community forums (see [community.md](./community.md))

---

## 🎓 Optional: Install AI Coding Assistants

These are optional but recommended for Day 1:

### Cursor IDE
- Download: [cursor.sh](https://cursor.sh/)
- Best for: Full IDE experience with AI pair programming

### Claude Code CLI
- Installation: See [Claude Code documentation](https://github.com/anthropics/claude-code)
- Best for: Terminal-based development

### GitHub Copilot
- Setup: [GitHub Copilot setup](https://github.com/features/copilot)
- Best for: Inline code completions in VS Code

We'll explore these tools on Day 1, so don't worry if you don't install them beforehand.

---

**Navigation:** [← Back to Guides](./README.md) | [View Curriculum →](../curriculum/) | [Day 1 Preview →](../curriculum/day1-foundations.md)
