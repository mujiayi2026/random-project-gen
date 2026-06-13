# 🎲 Random Project Generator

<p align="center">
  <a href="https://github.com/mujiayi2026/random-project-gen/blob/main/README.zh-CN.md"><img src="https://img.shields.io/badge/Lang-中文-red?style=for-the-badge" alt="中文文档"></a>
  <a href="https://github.com/mujiayi2026/random-project-gen/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Version-v3.7-orange?style=for-the-badge" alt="Version">
</p>

An **AI-powered CLI tool** that generates random project ideas for developers. Perfect for when you're looking for inspiration, practicing new technologies, or building your portfolio.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎲 **Random Generation** | Combine tech stack + project type + domain + creative twist |
| 🤖 **AI Descriptions** | Use AI to generate detailed project descriptions |
| 📊 **Project Scoring** | 4-dimensional scoring: Innovation, Practicality, Challenge, Fun |
| 📦 **Dependency Recommendations** | Smart library suggestions based on tech stack |
| 📖 **API Documentation** | Generate OpenAPI 3.0 specs for your project |
| 🧪 **Test Framework** | Auto-initialize testing (pytest/Jest/cargo test/Go testing) |
| ⚙️ **CI/CD Config** | GitHub Actions workflow templates |
| 📖 **README Templates** | Beautiful README with badges and structure |
| 🧠 **Smart Recommendations** | 5 strategies based on your history preferences |
| 🧩 **Plugin System** | Custom tech stacks, project types, themes, and twists |
| 🎨 **Rich Terminal UI** | Beautiful output with colors, spinners, and animations |
| 📜 **History & Stats** | Track your generated projects and usage statistics |

---

## 🚀 Quick Start

### Install

```bash
git clone https://github.com/mujiayi2026/random-project-gen.git
cd random-project-gen
pip install rich  # Optional: for beautiful terminal output
```

### Basic Usage

```bash
# Generate a random project
python3 gen.py

# Generate with AI description
python3 gen.py --ai

# Generate with scoring
python3 gen.py --score

# Generate multiple projects
python3 gen.py -n 5

# Get recommendations based on history
python3 gen.py --recommend

# Export to different formats
python3 gen.py --export json
python3 gen.py --export csv
python3 gen.py --export md
```

---

## 📖 Full Options

```bash
python3 gen.py [OPTIONS]

Generation:
  -n, --num N           Generate N projects (default: 1)
  --ai                  Generate AI-powered descriptions
  --score               Show project scoring (4 dimensions)
  --deps                Show dependency recommendations
  --api-doc             Generate API documentation (OpenAPI 3.0)
  --test-init           Generate test framework setup
  --cicd                Generate CI/CD configuration
  --readme              Generate README template

Recommendations:
  --recommend [N]       Get smart recommendations (default: 5)

Export:
  --export FORMAT       Export format: json, csv, md

Statistics:
  --stats               Show usage statistics
  --history             Show generation history

Plugins:
  --plugin-show         Show current plugins
  --plugin-add TYPE NAME EMOJI TAGS   Add custom plugin
  --plugin-remove TYPE NAME           Remove plugin
  --plugin-reset        Reset all plugins

Display:
  --no-animation        Disable animations
  --no-color            Disable colors
  --completion SHELL    Generate shell completion (bash/zsh)
```

---

## 🧩 Plugin System

Extend the generator with your own custom data:

```bash
# Add custom tech stack
python3 gen.py --plugin-add tech "Django" "🐍" "backend,web,mvc"

# Add custom project type
python3 gen.py --plugin-add project "IoT Project" "📡" "hardware,sensors"

# Add custom theme
python3 gen.py --plugin-add theme "Blockchain" "⛓️" "Web3/DeFi/NFT"

# Add custom twist
python3 gen.py --plugin-add twist "Support voice interaction" "_" "_"

# View plugins
python3 gen.py --plugin-show
```

---

## 📊 Scoring System

Each project gets scored on 4 dimensions (1-10):

| Dimension | Description |
|-----------|-------------|
| 💡 **Innovation** | How novel and creative is the idea? |
| 🔧 **Practicality** | How useful and applicable is it? |
| 🔥 **Challenge** | How difficult to implement? |
| 🎮 **Fun** | How enjoyable to build? |

---

## 🧠 Recommendation Strategies

The recommendation system analyzes your history and suggests projects using 5 strategies:

1. 🔍 **Deep Exploration** — Favorite tech + unexplored domains
2. 🌐 **Cross-Domain Discovery** — Favorite domain + less-used tech
3. 🔥 **Level Up Challenge** — Favorite combo + higher difficulty
4. ✨ **New Adventure** — Completely unused combinations
5. 🎯 **Preference Variants** — Favorite type/domain + new tech

---

## 📁 Project Structure

```
random-project-gen/
├── gen.py              # Main application (4,585 lines)
├── .gen_history.json   # Generation history
├── .gen_config.json    # User preferences (auto-generated)
├── .gen_plugins.json   # Custom plugins (auto-generated)
├── .gitignore
└── README.md
```

---

## 🛠️ Tech Stack

- **Python 3.8+**
- **Rich** — Terminal formatting and UI
- **JSON** — Data storage
- **argparse** — CLI interface

---

## 📝 Examples

```bash
# Quick project idea
$ python3 gen.py

🎲 Random Project: Task Management CLI
├── Tech: Python + Click
├── Type: CLI Tool
├── Domain: Productivity
├── Twist: Gamification with XP system
└── Score: 💡8 🔧9 🔥6 🎮8

# Get 5 recommendations
$ python3 gen.py --recommend

# Export history
$ python3 gen.py --export md > my_projects.md
```

---

## 🙏 Credits

- Built with ❤️ for developers who need inspiration
- Powered by Python and Rich

---

<p align="center">
  <i>🎲 Roll the dice, build something amazing!</i>
</p>
