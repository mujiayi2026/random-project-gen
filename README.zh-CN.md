# 🎲 随机项目生成器

<p align="center">
  <a href="https://github.com/mujiayi2026/random-project-gen/blob/main/README.md"><img src="https://img.shields.io/badge/Lang-English-lightgrey?style=for-the-badge" alt="English"></a>
  <a href="https://github.com/mujiayi2026/random-project-gen/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/版本-v3.7-orange?style=for-the-badge" alt="Version">
</p>

一个**AI 驱动的命令行工具**，用于生成随机项目创意。当你需要灵感、练习新技术或构建作品集时，它会是完美的帮手。

---

## ✨ 核心功能

| 功能 | 说明 |
|------|------|
| 🎲 **随机生成** | 技术栈 + 项目类型 + 领域 + 创意转折的智能组合 |
| 🤖 **AI 描述** | 使用 AI 生成详细的项目描述 |
| 📊 **项目评分** | 四维评分：创新度、实用性、挑战度、趣味性 |
| 📦 **依赖推荐** | 根据技术栈智能推荐常用库 |
| 📖 **API 文档** | 生成 OpenAPI 3.0 规范文档 |
| 🧪 **测试框架** | 自动初始化测试（pytest/Jest/cargo test/Go testing） |
| ⚙️ **CI/CD 配置** | GitHub Actions 工作流模板 |
| 📖 **README 模板** | 带徽章和目录结构的精美 README |
| 🧠 **智能推荐** | 基于历史偏好的 5 种推荐策略 |
| 🧩 **插件系统** | 自定义技术栈、项目类型、主题和创意转折 |
| 🎨 **Rich 终端 UI** | 彩色输出、加载动画和精美排版 |
| 📜 **历史与统计** | 跟踪生成记录和使用统计 |

---

## 🚀 快速开始

### 安装

```bash
git clone https://github.com/mujiayi2026/random-project-gen.git
cd random-project-gen
pip install rich  # 可选：美化终端输出
```

### 基本用法

```bash
# 生成随机项目
python3 gen.py

# 生成 AI 描述
python3 gen.py --ai

# 显示评分
python3 gen.py --score

# 生成多个项目
python3 gen.py -n 5

# 基于历史偏好获取推荐
python3 gen.py --recommend

# 导出为不同格式
python3 gen.py --export json
python3 gen.py --export csv
python3 gen.py --export md
```

---

## 📖 完整参数

```bash
python3 gen.py [OPTIONS]

生成选项：
  -n, --num N           生成 N 个项目（默认：1）
  --ai                  生成 AI 描述
  --score               显示四维评分
  --deps                显示依赖推荐
  --api-doc             生成 API 文档（OpenAPI 3.0）
  --test-init           生成测试框架配置
  --cicd                生成 CI/CD 配置
  --readme              生成 README 模板

推荐：
  --recommend [N]       获取智能推荐（默认：5 个）

导出：
  --export FORMAT       导出格式：json、csv、md

统计：
  --stats               显示使用统计
  --history             显示生成历史

插件：
  --plugin-show         显示当前插件
  --plugin-add TYPE NAME EMOJI TAGS   添加自定义插件
  --plugin-remove TYPE NAME           移除插件
  --plugin-reset        重置所有插件

显示：
  --no-animation        禁用动画
  --no-color            禁用颜色
  --completion SHELL    生成 shell 补全（bash/zsh）
```

---

## 🧩 插件系统

用自定义数据扩展生成器：

```bash
# 添加自定义技术栈
python3 gen.py --plugin-add tech "Django" "🐍" "backend,web,mvc"

# 添加自定义项目类型
python3 gen.py --plugin-add project "物联网项目" "📡" "hardware,sensors"

# 添加自定义主题
python3 gen.py --plugin-add theme "区块链" "⛓️" "Web3/DeFi/NFT"

# 添加自定义转折
python3 gen.py --plugin-add twist "支持语音交互" "_" "_"

# 查看插件
python3 gen.py --plugin-show
```

---

## 📊 评分系统

每个项目在 4 个维度上评分（1-10）：

| 维度 | 说明 |
|------|------|
| 💡 **创新度** | 想法有多新颖和创意？ |
| 🔧 **实用性** | 有多实用和可应用？ |
| 🔥 **挑战度** | 实现难度有多大？ |
| 🎮 **趣味性** | 构建过程有多有趣？ |

---

## 🧠 推荐策略

推荐系统分析你的历史记录，使用 5 种策略推荐项目：

1. 🔍 **深度探索** — 最爱技术栈 + 未尝试的领域
2. 🌐 **跨界发现** — 最爱领域 + 较少使用的技术栈
3. 🔥 **升级挑战** — 最爱组合 + 高难度版本
4. ✨ **全新冒险** — 完全未被使用的组合
5. 🎯 **偏好变体** — 最爱项目类型/领域 + 新技术栈

---

## 📁 项目结构

```
random-project-gen/
├── gen.py              # 主程序（4,585 行）
├── .gen_history.json   # 生成历史
├── .gen_config.json    # 用户偏好（自动生成）
├── .gen_plugins.json   # 自定义插件（自动生成）
├── .gitignore
└── README.md
```

---

## 🛠️ 技术栈

- **Python 3.8+**
- **Rich** — 终端格式化和 UI
- **JSON** — 数据存储
- **argparse** — 命令行接口

---

## 📝 示例

```bash
# 快速获取项目灵感
$ python3 gen.py

🎲 随机项目：任务管理 CLI
├── 技术：Python + Click
├── 类型：CLI 工具
├── 领域：生产力
├── 转折：游戏化 XP 系统
└── 评分：💡8 🔧9 🔥6 🎮8

# 获取 5 个推荐
$ python3 gen.py --recommend

# 导出历史
$ python3 gen.py --export md > my_projects.md
```

---

## 🙏 致谢

- 为需要灵感的开发者用 ❤️ 构建
- 由 Python 和 Rich 驱动

---

<p align="center">
  <i>🎲 掷出骰子，构建精彩项目！</i>
</p>
