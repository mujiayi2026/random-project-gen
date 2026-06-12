#!/usr/bin/env python3
"""
🎲 Random Project Generator v3.0
随机组合技术栈 + 项目类型 + 领域，帮你找灵感！

Usage:
    python3 gen.py                    # 基础模式
    python3 gen.py --ai               # AI 生成详细描述
    python3 gen.py -n 3 --ai          # 生成 3 个 + AI 描述
    python3 gen.py --save             # 保存到 ideas.md
    python3 gen.py --hard             # 只生成高难度项目
    python3 gen.py --tech python,node # 只用指定技术栈
    python3 gen.py --scaffold         # 生成项目骨架代码
    python3 gen.py --reroll tech      # 重新生成技术栈（交互模式）
    python3 gen.py --history          # 查看历史记录
    python3 gen.py --stats            # 查看使用统计
    python3 gen.py -n 3 --export      # 导出为 JSON (默认)
    python3 gen.py --export csv       # 导出为 CSV
    python3 gen.py --export md        # 导出为 Markdown
    python3 gen.py --export json --export-file my_ideas.json  # 指定文件名
"""

import random
import argparse
import json
import csv
import os
import sys
from datetime import datetime
from collections import Counter

HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".gen_history.json")

# ═══════════════════════════════════════════
# 历史记录
# ═══════════════════════════════════════════

def load_history():
    """加载历史记录"""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def save_to_history(idea, ai_desc=None):
    """保存一条生成记录到历史"""
    history = load_history()
    record = {
        "timestamp": datetime.now().isoformat(),
        "tech": idea["tech"]["name"],
        "project": idea["project"]["name"],
        "theme": idea["theme"]["name"],
        "difficulty": idea["difficulty"]["name"],
        "twist": idea["twist"],
    }
    if ai_desc:
        record["project_name"] = ai_desc.get("project_name", "")
        record["tagline"] = ai_desc.get("tagline", "")
    history.append(record)
    # 保留最近 500 条
    if len(history) > 500:
        history = history[-500:]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def print_history(limit=20):
    """打印最近的历史记录"""
    history = load_history()
    if not history:
        print("\n  📜 暂无历史记录，快去生成一些创意吧！\n")
        return

    print()
    print("  ╔══════════════════════════════════════╗")
    print("  ║       📜 历史记录 (最近生成)          ║")
    print("  ╚══════════════════════════════════════╝")
    print()

    recent = history[-limit:][::-1]  # 最新的在前
    for i, rec in enumerate(recent, 1):
        ts = rec.get("timestamp", "?")
        # 只显示日期时间的简短形式
        try:
            dt = datetime.fromisoformat(ts)
            ts_str = dt.strftime("%m-%d %H:%M")
        except Exception:
            ts_str = ts[:16]
        name = rec.get("project_name", "")
        name_str = f" 📦 {name}" if name else ""
        print(f"  {i:>3}. [{ts_str}] {rec['tech']} + {rec['project']} + {rec['theme']}{name_str}")

    print(f"\n  共 {len(history)} 条记录 (显示最近 {len(recent)} 条)")
    print()

def print_stats():
    """打印使用统计"""
    history = load_history()
    if not history:
        print("\n  📊 暂无统计数据，快去生成一些创意吧！\n")
        return

    print()
    print("  ╔══════════════════════════════════════╗")
    print("  ║         📊 使用统计                  ║")
    print("  ╚══════════════════════════════════════╝")
    print()

    tech_counts = Counter(r["tech"] for r in history)
    project_counts = Counter(r["project"] for r in history)
    theme_counts = Counter(r["theme"] for r in history)
    diff_counts = Counter(r["difficulty"] for r in history)

    def print_bar(label, count, total, width=20):
        filled = int(width * count / total) if total else 0
        bar = "█" * filled + "░" * (width - filled)
        pct = count / total * 100 if total else 0
        print(f"    {label:<12} {bar} {count:>4} ({pct:>5.1f}%)")

    total = len(history)
    print(f"  📈 总计生成 {total} 个创意\n")

    print("  🔧 技术栈 TOP 10:")
    for name, cnt in tech_counts.most_common(10):
        print_bar(name, cnt, total)

    print("\n  📁 项目类型 TOP 10:")
    for name, cnt in project_counts.most_common(10):
        print_bar(name, cnt, total)

    print("\n  🎨 领域 TOP 10:")
    for name, cnt in theme_counts.most_common(10):
        print_bar(name, cnt, total)

    print("\n  ⚡ 难度分布:")
    for name, cnt in diff_counts.most_common():
        print_bar(name, cnt, total)

    # 显示重复创意
    combos = Counter((r["tech"], r["project"], r["theme"]) for r in history)
    duplicates = [(k, v) for k, v in combos.items() if v > 1]
    if duplicates:
        print(f"\n  ⚠️  重复组合 ({len(duplicates)} 组):")
        for (tech, proj, theme), cnt in sorted(duplicates, key=lambda x: -x[1])[:5]:
            print(f"    {tech} + {proj} + {theme} × {cnt}")

    print()

# ═══════════════════════════════════════════
# 数据库
# ═══════════════════════════════════════════

TECH_STACKS = [
    {"name": "Python", "emoji": "🐍", "tags": ["backend", "data", "ai"]},
    {"name": "Node.js", "emoji": "💚", "tags": ["backend", "frontend", "fullstack"]},
    {"name": "Rust", "emoji": "🦀", "tags": ["systems", "performance", "cli"]},
    {"name": "Go", "emoji": "🐹", "tags": ["backend", "systems", "cli"]},
    {"name": "TypeScript", "emoji": "🔷", "tags": ["frontend", "fullstack", "backend"]},
    {"name": "React", "emoji": "⚛️", "tags": ["frontend", "web"]},
    {"name": "Vue", "emoji": "💚", "tags": ["frontend", "web"]},
    {"name": "Svelte", "emoji": "🔥", "tags": ["frontend", "web"]},
    {"name": "Flutter", "emoji": "📱", "tags": ["mobile", "cross-platform"]},
    {"name": "Swift", "emoji": "🍎", "tags": ["mobile", "ios"]},
    {"name": "Kotlin", "emoji": "🟣", "tags": ["mobile", "android", "backend"]},
    {"name": "C++", "emoji": "⚡", "tags": ["systems", "performance", "game"]},
    {"name": "Lua", "emoji": "🌙", "tags": ["game", "scripting"]},
    {"name": "Elixir", "emoji": "💧", "tags": ["backend", "concurrent"]},
    {"name": "Zig", "emoji": "⚡", "tags": ["systems", "performance"]},
]

PROJECT_TYPES = [
    {"name": "CLI 工具", "emoji": "💻", "desc": "命令行工具"},
    {"name": "Web 应用", "emoji": "🌐", "desc": "浏览器端应用"},
    {"name": "API 服务", "emoji": "🔌", "desc": "RESTful/GraphQL API"},
    {"name": "桌面应用", "emoji": "🖥️", "desc": "本地桌面程序"},
    {"name": "移动应用", "emoji": "📱", "desc": "iOS/Android 应用"},
    {"name": "游戏", "emoji": "🎮", "desc": "小游戏"},
    {"name": "浏览器扩展", "emoji": "🧩", "desc": "Chrome/Firefox 扩展"},
    {"name": "Telegram Bot", "emoji": "🤖", "desc": "Telegram 机器人"},
    {"name": "VS Code 扩展", "emoji": "📝", "desc": "编辑器扩展"},
    {"name": "终端 UI", "emoji": "🎨", "desc": "终端可视化界面"},
    {"name": "数据管道", "emoji": "🔄", "desc": "ETL/数据处理"},
    {"name": "微服务", "emoji": "🔧", "desc": "分布式微服务"},
]

THEMES = [
    {"name": "效率工具", "emoji": "⚡", "desc": "提升开发/工作效率"},
    {"name": "健康健身", "emoji": "💪", "desc": "运动、饮食、睡眠"},
    {"name": "音乐", "emoji": "🎵", "desc": "播放、生成、可视化"},
    {"name": "游戏化", "emoji": "🏆", "desc": "积分、排行榜、成就"},
    {"name": "AI/ML", "emoji": "🧠", "desc": "机器学习、NLP、CV"},
    {"name": "社交", "emoji": "👥", "desc": "聊天、分享、社区"},
    {"name": "学习教育", "emoji": "📚", "desc": "教程、练习、考试"},
    {"name": "创意工具", "emoji": "🎨", "desc": "设计、绘图、生成"},
    {"name": "自动化", "emoji": "🤖", "desc": "流程自动化、爬虫"},
    {"name": "安全", "emoji": "🔒", "desc": "加密、认证、扫描"},
    {"name": "DevOps", "emoji": "🚀", "desc": "部署、监控、CI/CD"},
    {"name": "金融", "emoji": "💰", "desc": "记账、投资、支付"},
    {"name": "天气环境", "emoji": "🌤️", "desc": "天气、气候、环保"},
    {"name": "美食", "emoji": "🍜", "desc": "食谱、推荐、外卖"},
    {"name": "宠物", "emoji": "🐱", "desc": "宠物管理、社交"},
]

DIFFICULTIES = [
    {"name": "入门", "emoji": "🟢", "hours": "2-4h", "stars": 1},
    {"name": "进阶", "emoji": "🟡", "hours": "4-8h", "stars": 2},
    {"name": "挑战", "emoji": "🔴", "hours": "1-3天", "stars": 3},
    {"name": "地狱", "emoji": "💀", "hours": "1周+", "stars": 4},
]

TWISTS = [
    "但要支持离线使用",
    "而且要完全用 CLI 完成",
    "加上实时协作功能",
    "用 AI 来增强核心体验",
    "做一个极简风格的版本",
    "支持插件/扩展系统",
    "加上暗黑模式（必须的）",
    "用 TUI 而不是 GUI",
    "支持多语言国际化",
    "加入 gamification 元素",
    "做成开源项目",
    "加上 WebSocket 实时通信",
    "支持 Docker 一键部署",
    "做一个 mobile-first 的版本",
    "加上完善的测试覆盖",
]

# ═══════════════════════════════════════════
# 项目骨架模板
# ═══════════════════════════════════════════

SCAFFOLD_TEMPLATES = {
    "Python": {
        "files": {
            "README.md": """# {project_name}

{tagline}

## 安装

```bash
pip install -r requirements.txt
```

## 使用

```bash
python main.py
```

## 功能

{features_list}
""",
            "requirements.txt": "# 项目依赖\n",
            "main.py": """#!/usr/bin/env python3
\"\"\"
{project_name} - {tagline}
\"\"\"

def main():
    print("Hello from {project_name}!")

if __name__ == "__main__":
    main()
""",
            "config.py": """# 配置文件

CONFIG = {{
    "app_name": "{project_name}",
    "version": "0.1.0",
    "debug": True,
}}
""",
            ".gitignore": """__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
.env
*.egg-info/
dist/
build/
""",
        },
        "dirs": ["src", "tests", "docs"],
    },
    "Node.js": {
        "files": {
            "README.md": """# {project_name}

{tagline}

## 安装

```bash
npm install
```

## 使用

```bash
npm start
```

## 功能

{features_list}
""",
            "package.json": """{{
  "name": "{project_slug}",
  "version": "0.1.0",
  "description": "{tagline}",
  "main": "index.js",
  "scripts": {{
    "start": "node index.js",
    "dev": "nodemon index.js",
    "test": "jest"
  }},
  "keywords": [],
  "author": "",
  "license": "MIT"
}}
""",
            "index.js": """/**
 * {project_name} - {tagline}
 */

function main() {{
  console.log('Hello from {project_name}!');
}}

main();
""",
            ".gitignore": """node_modules/
.env
dist/
*.log
""",
        },
        "dirs": ["src", "tests", "docs"],
    },
    "default": {
        "files": {
            "README.md": """# {project_name}

{tagline}

## 功能

{features_list}
""",
        },
        "dirs": ["src", "tests", "docs"],
    },
}

# ═══════════════════════════════════════════
# AI 生成
# ═══════════════════════════════════════════

def get_ai_description(idea):
    """用 AI 生成详细的项目描述"""
    try:
        from openai import OpenAI
        
        client = OpenAI(
            api_key="tp-clsya4dpckssktasruy67rtgkok2hgz40ni91gima67amar8",
            base_url="https://token-plan-cn.xiaomimimo.com/v1"
        )
        
        t = idea["tech"]
        p = idea["project"]
        th = idea["theme"]
        d = idea["difficulty"]
        w = idea["twist"]
        
        prompt = f"我在做一个{t['name']}项目，类型是{p['name']}，主题是{th['name']}，难度{d['name']}（{d['hours']}），特色是{w}。请给我：1)一个有创意的项目名称 2)一句话介绍 3)4个主要功能 4)2个技术亮点 5)快速开始步骤。简洁回答，用编号列表。"

        response = client.chat.completions.create(
            model="mimo-v2.5-pro",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=400
        )
        
        content = response.choices[0].message.content
        if not content or content.strip() == "":
            return None
        
        # 手动解析结构化内容
        result = {
            "project_name": f"{t['name']}{th['name']}{p['name'].replace(' ', '')}",
            "tagline": th['desc'],
            "description": "",
            "features": [],
            "tech_highlights": [],
            "getting_started": ""
        }
        
        lines = content.strip().split("\n")
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if "项目名称" in line or line.startswith("1"):
                name = line.split("：")[-1].split(":")[-1].strip()
                name = name.replace("**", "").strip()
                if name:
                    result["project_name"] = name
                current_section = "name"
            elif "一句话" in line or "介绍" in line or line.startswith("2"):
                tagline = line.split("：")[-1].split(":")[-1].strip()
                tagline = tagline.replace("**", "").strip()
                if tagline:
                    result["tagline"] = tagline
                current_section = "tagline"
            elif "功能" in line or line.startswith("3"):
                current_section = "features"
                if "：" in line or ":" in line:
                    feat = line.split("：")[-1].split(":")[-1].strip()
                    feat = feat.replace("**", "").replace("-", "").strip()
                    if feat and len(feat) > 3:
                        result["features"].append(feat)
            elif "亮点" in line or line.startswith("4"):
                current_section = "highlights"
                if "：" in line or ":" in line:
                    highlight = line.split("：")[-1].split(":")[-1].strip()
                    highlight = highlight.replace("**", "").replace("-", "").strip()
                    if highlight and len(highlight) > 3:
                        result["tech_highlights"].append(highlight)
            elif "开始" in line or "步骤" in line or line.startswith("5"):
                current_section = "start"
                start = line.split("：")[-1].split(":")[-1].strip()
                start = start.replace("**", "").strip()
                if start and len(start) > 3:
                    result["getting_started"] = start
            elif current_section == "features" and (line.startswith("-") or line.startswith("•") or line.startswith("*")):
                feat = line.lstrip("-•* ").replace("**", "").strip()
                if feat and len(feat) > 3:
                    result["features"].append(feat)
            elif current_section == "highlights" and (line.startswith("-") or line.startswith("•") or line.startswith("*")):
                highlight = line.lstrip("-•* ").replace("**", "").strip()
                if highlight and len(highlight) > 3:
                    result["tech_highlights"].append(highlight)
            elif current_section == "start" and not result["getting_started"]:
                start = line.replace("**", "").strip()
                if start and len(start) > 5:
                    result["getting_started"] = start
        
        # 确保有足够的功能和亮点
        if len(result["features"]) < 3:
            result["features"] = ["核心功能模块", "用户交互界面", "配置管理系统", "数据持久化"]
        if len(result["tech_highlights"]) < 2:
            result["tech_highlights"] = ["模块化设计", "跨平台支持"]
        if not result["getting_started"]:
            result["getting_started"] = f"pip install依赖, 编辑配置文件, 运行程序"
        
        # 生成描述
        result["description"] = f"一个基于{t['name']}的{p['name']}，专注于{th['name']}领域。{result['tagline']}适合{d['name']}级别的开发者，预计{d['hours']}完成。"
        
        return result
        
    except Exception as e:
        print(f"  ⚠️  AI 生成失败: {e}")
        return None

# ═══════════════════════════════════════════
# 核心功能
# ═══════════════════════════════════════════

def get_tech_stacks_by_filter(tech_filter):
    """根据过滤条件筛选技术栈"""
    if not tech_filter:
        return TECH_STACKS
    
    filter_names = [t.strip().lower() for t in tech_filter.split(",")]
    filtered = []
    
    for tech in TECH_STACKS:
        if tech["name"].lower() in filter_names:
            filtered.append(tech)
    
    return filtered if filtered else TECH_STACKS

def generate_idea(hard_mode=False, tech_filter=None):
    """生成一个随机项目创意"""
    available_techs = get_tech_stacks_by_filter(tech_filter)
    tech = random.choice(available_techs)
    proj = random.choice(PROJECT_TYPES)
    theme = random.choice(THEMES)
    
    if hard_mode:
        diff = random.choice(DIFFICULTIES[2:])
    else:
        diff = random.choice(DIFFICULTIES)
    
    twist = random.choice(TWISTS)
    
    return {
        "tech": tech,
        "project": proj,
        "theme": theme,
        "difficulty": diff,
        "twist": twist,
    }

def reroll_component(idea, component):
    """重新生成指定组件"""
    if component == "tech":
        idea["tech"] = random.choice(TECH_STACKS)
    elif component == "project":
        idea["project"] = random.choice(PROJECT_TYPES)
    elif component == "theme":
        idea["theme"] = random.choice(THEMES)
    elif component == "difficulty":
        idea["difficulty"] = random.choice(DIFFICULTIES)
    elif component == "twist":
        idea["twist"] = random.choice(TWISTS)
    return idea

def format_idea(idea, index=None):
    """格式化基础创意"""
    t = idea["tech"]
    p = idea["project"]
    th = idea["theme"]
    d = idea["difficulty"]
    w = idea["twist"]
    stars = "⭐" * d["stars"]
    prefix = f"#{index}  " if index else ""
    
    lines = [
        f"  {prefix}{'─' * 40}",
        f"  {t['emoji']} 技术栈: {t['name']}",
        f"  {p['emoji']} 项目类型: {p['name']} — {p['desc']}",
        f"  {th['emoji']} 领域: {th['name']} — {th['desc']}",
        f"  {d['emoji']} 难度: {d['name']} {stars} (预计 {d['hours']})",
        f"  ✨ Twist: {w}",
        f"  {'─' * 40}",
    ]
    
    name_ideas = [
        f"{t['name']}{th['name']}{p['name'].replace(' ', '')}",
        f"{th['name']}Hub",
        f"{p['name'].replace(' ', '')}X",
        f"Vibe{th['name']}",
    ]
    suggested_name = random.choice(name_ideas)
    lines.append(f"  📦 建议项目名: {suggested_name}")
    
    return "\n".join(lines)

def format_ai_idea(idea, ai_desc, index=None):
    """格式化带 AI 描述的创意"""
    t = idea["tech"]
    p = idea["project"]
    th = idea["theme"]
    d = idea["difficulty"]
    w = idea["twist"]
    stars = "⭐" * d["stars"]
    prefix = f"#{index}  " if index else ""
    
    lines = []
    lines.append(f"  {prefix}{'═' * 44}")
    lines.append(f"  📦 {ai_desc['project_name']}")
    lines.append(f"  💬 {ai_desc['tagline']}")
    lines.append(f"  {'─' * 44}")
    lines.append(f"  {t['emoji']} 技术栈: {t['name']}")
    lines.append(f"  {p['emoji']} 项目类型: {p['name']}")
    lines.append(f"  {th['emoji']} 领域: {th['name']}")
    lines.append(f"  {d['emoji']} 难度: {d['name']} {stars} (预计 {d['hours']})")
    lines.append(f"  ✨ Twist: {w}")
    lines.append(f"  {'─' * 44}")
    lines.append(f"  📝 项目描述:")
    
    desc = ai_desc['description']
    for i in range(0, len(desc), 40):
        lines.append(f"     {desc[i:i+40]}")
    
    lines.append(f"  {'─' * 44}")
    lines.append(f"  🎯 核心功能:")
    for feat in ai_desc['features']:
        lines.append(f"     • {feat}")
    
    lines.append(f"  {'─' * 44}")
    lines.append(f"  🔧 技术亮点:")
    for highlight in ai_desc['tech_highlights']:
        lines.append(f"     • {highlight}")
    
    lines.append(f"  {'─' * 44}")
    lines.append(f"  🚀 快速开始:")
    lines.append(f"     {ai_desc['getting_started']}")
    lines.append(f"  {'═' * 44}")
    
    return "\n".join(lines)

def save_ideas(ideas, ai_descriptions=None, filename="ideas.md"):
    """保存创意到 markdown 文件"""
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"\n## 💡 Ideas — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        for i, idea in enumerate(ideas, 1):
            t = idea["tech"]
            p = idea["project"]
            th = idea["theme"]
            d = idea["difficulty"]
            w = idea["twist"]
            
            if ai_descriptions and i-1 < len(ai_descriptions) and ai_descriptions[i-1]:
                ai = ai_descriptions[i-1]
                f.write(f"### {i}. 📦 {ai['project_name']}\n")
                f.write(f"> {ai['tagline']}\n\n")
                f.write(f"**技术栈**: {t['name']} | **类型**: {p['name']} | **领域**: {th['name']} | **难度**: {d['name']}\n\n")
                f.write(f"**描述**: {ai['description']}\n\n")
                f.write(f"**核心功能**:\n")
                for feat in ai['features']:
                    f.write(f"- {feat}\n")
                f.write(f"\n**Twist**: {w}\n\n")
                f.write(f"---\n\n")
            else:
                f.write(f"### {i}. {t['emoji']} {t['name']} + {p['name']} + {th['name']}\n")
                f.write(f"- **技术栈**: {t['name']}\n")
                f.write(f"- **类型**: {p['name']} — {p['desc']}\n")
                f.write(f"- **领域**: {th['name']} — {th['desc']}\n")
                f.write(f"- **难度**: {d['name']} ({d['hours']})\n")
                f.write(f"- **Twist**: {w}\n\n")
    
    print(f"\n  💾 已保存到 {filename}")

def export_json(ideas, ai_descriptions=None, filename=None):
    """导出创意为 JSON 格式"""
    if not filename:
        filename = f"ideas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    data = []
    for i, idea in enumerate(ideas):
        entry = {
            "index": i + 1,
            "tech": idea["tech"]["name"],
            "tech_tags": idea["tech"]["tags"],
            "project_type": idea["project"]["name"],
            "project_desc": idea["project"]["desc"],
            "theme": idea["theme"]["name"],
            "theme_desc": idea["theme"]["desc"],
            "difficulty": idea["difficulty"]["name"],
            "difficulty_hours": idea["difficulty"]["hours"],
            "difficulty_stars": idea["difficulty"]["stars"],
            "twist": idea["twist"],
            "generated_at": datetime.now().isoformat(),
        }
        if ai_descriptions and i < len(ai_descriptions) and ai_descriptions[i]:
            ai = ai_descriptions[i]
            entry["ai"] = {
                "project_name": ai.get("project_name", ""),
                "tagline": ai.get("tagline", ""),
                "description": ai.get("description", ""),
                "features": ai.get("features", []),
                "tech_highlights": ai.get("tech_highlights", []),
                "getting_started": ai.get("getting_started", ""),
            }
        data.append(entry)
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n  💾 已导出 JSON: {filename} ({len(data)} 条)")
    return filename


def export_csv(ideas, ai_descriptions=None, filename=None):
    """导出创意为 CSV 格式"""
    if not filename:
        filename = f"ideas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    fieldnames = [
        "index", "tech", "project_type", "theme", "difficulty",
        "difficulty_hours", "difficulty_stars", "twist",
        "ai_project_name", "ai_tagline", "ai_features", "generated_at",
    ]
    
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for i, idea in enumerate(ideas):
            row = {
                "index": i + 1,
                "tech": idea["tech"]["name"],
                "project_type": idea["project"]["name"],
                "theme": idea["theme"]["name"],
                "difficulty": idea["difficulty"]["name"],
                "difficulty_hours": idea["difficulty"]["hours"],
                "difficulty_stars": idea["difficulty"]["stars"],
                "twist": idea["twist"],
                "ai_project_name": "",
                "ai_tagline": "",
                "ai_features": "",
                "generated_at": datetime.now().isoformat(),
            }
            if ai_descriptions and i < len(ai_descriptions) and ai_descriptions[i]:
                ai = ai_descriptions[i]
                row["ai_project_name"] = ai.get("project_name", "")
                row["ai_tagline"] = ai.get("tagline", "")
                row["ai_features"] = " | ".join(ai.get("features", []))
            writer.writerow(row)
    
    print(f"\n  💾 已导出 CSV: {filename} ({len(ideas)} 条)")
    return filename


def export_markdown(ideas, ai_descriptions=None, filename=None):
    """导出创意为独立 Markdown 文件（覆盖而非追加）"""
    if not filename:
        filename = f"ideas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# 🎲 Random Project Ideas\n\n")
        f.write(f"> Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"Total: **{len(ideas)}** ideas\n\n---\n\n")
        
        for i, idea in enumerate(ideas):
            t = idea["tech"]
            p = idea["project"]
            th = idea["theme"]
            d = idea["difficulty"]
            w = idea["twist"]
            stars = "⭐" * d["stars"]
            
            if ai_descriptions and i < len(ai_descriptions) and ai_descriptions[i]:
                ai = ai_descriptions[i]
                f.write(f"## {i+1}. 📦 {ai['project_name']}\n\n")
                f.write(f"> {ai['tagline']}\n\n")
                f.write(f"| 属性 | 值 |\n|---|---|\n")
                f.write(f"| 技术栈 | {t['emoji']} {t['name']} |\n")
                f.write(f"| 项目类型 | {p['emoji']} {p['name']} |\n")
                f.write(f"| 领域 | {th['emoji']} {th['name']} |\n")
                f.write(f"| 难度 | {d['emoji']} {d['name']} {stars} ({d['hours']}) |\n")
                f.write(f"| Twist | {w} |\n\n")
                f.write(f"**描述**: {ai['description']}\n\n")
                if ai.get("features"):
                    f.write(f"**核心功能**:\n")
                    for feat in ai["features"]:
                        f.write(f"- {feat}\n")
                    f.write("\n")
                if ai.get("tech_highlights"):
                    f.write(f"**技术亮点**:\n")
                    for hl in ai["tech_highlights"]:
                        f.write(f"- {hl}\n")
                    f.write("\n")
            else:
                f.write(f"## {i+1}. {t['emoji']} {t['name']} + {p['name']} + {th['name']}\n\n")
                f.write(f"| 属性 | 值 |\n|---|---|\n")
                f.write(f"| 技术栈 | {t['emoji']} {t['name']} |\n")
                f.write(f"| 项目类型 | {p['emoji']} {p['name']} — {p['desc']} |\n")
                f.write(f"| 领域 | {th['emoji']} {th['name']} — {th['desc']} |\n")
                f.write(f"| 难度 | {d['emoji']} {d['name']} {stars} ({d['hours']}) |\n")
                f.write(f"| Twist | {w} |\n\n")
            
            f.write("---\n\n")
    
    print(f"\n  💾 已导出 Markdown: {filename} ({len(ideas)} 条)")
    return filename


def generate_scaffold(idea, ai_desc=None):
    """生成项目骨架"""
    t = idea["tech"]
    project_name = ai_desc["project_name"] if ai_desc else f"{t['name']}Project"
    tagline = ai_desc["tagline"] if ai_desc else idea["theme"]["desc"]
    features = ai_desc["features"] if ai_desc else ["功能1", "功能2", "功能3", "功能4"]
    
    # 创建项目目录
    project_slug = project_name.lower().replace(" ", "-").replace("(", "").replace(")", "")
    project_dir = f"projects/{project_slug}"
    
    if os.path.exists(project_dir):
        print(f"  ⚠️  目录已存在: {project_dir}")
        return project_dir
    
    # 获取模板
    template = SCAFFOLD_TEMPLATES.get(t["name"], SCAFFOLD_TEMPLATES["default"])
    
    # 创建目录
    os.makedirs(project_dir, exist_ok=True)
    for d in template["dirs"]:
        os.makedirs(f"{project_dir}/{d}", exist_ok=True)
    
    # 创建文件
    features_list = "\n".join([f"- {f}" for f in features])
    
    for filename, content in template["files"].items():
        filepath = f"{project_dir}/{filename}"
        formatted_content = content.format(
            project_name=project_name,
            project_slug=project_slug,
            tagline=tagline,
            features_list=features_list,
        )
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(formatted_content)
    
    # 初始化 git
    os.system(f"cd {project_dir} && git init -q 2>/dev/null")
    
    return project_dir

# ═══════════════════════════════════════════
# 主程序
# ═══════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="🎲 Random Project Generator")
    parser.add_argument("-n", "--count", type=int, default=1, help="生成数量 (默认 1)")
    parser.add_argument("--save", action="store_true", help="保存到 ideas.md")
    parser.add_argument("--hard", action="store_true", help="只生成高难度项目")
    parser.add_argument("--ai", action="store_true", help="用 AI 生成详细描述")
    parser.add_argument("--tech", type=str, help="指定技术栈 (逗号分隔，如 python,node)")
    parser.add_argument("--scaffold", action="store_true", help="生成项目骨架代码")
    parser.add_argument("--reroll", type=str, choices=["tech", "project", "theme", "difficulty", "twist"],
                       help="重新生成指定组件 (交互模式)")
    parser.add_argument("--history", action="store_true", help="查看历史记录")
    parser.add_argument("--stats", action="store_true", help="查看使用统计")
    parser.add_argument("--export", type=str, nargs="?", const="json", default=None,
                       metavar="FORMAT",
                       help="导出为文件 (json/csv/md, 默认 json)")
    parser.add_argument("--export-file", type=str, default=None,
                       help="指定导出文件名 (配合 --export 使用)")
    args = parser.parse_args()

    if args.history:
        print_history()
        return
    if args.stats:
        print_stats()
        return
    
    print()
    print("  ╔══════════════════════════════════════╗")
    print("  ║   🎲 Random Project Generator v3.0   ║")
    print("  ║   帮你找到下一个 vibecoding 项目!     ║")
    if args.ai:
        print("  ║   ✨ AI 增强模式已启用                ║")
    if args.tech:
        print(f"  ║   🎯 技术栈过滤: {args.tech:<19}║")
    if args.scaffold:
        print("  ║   🏗️  骨架生成模式已启用              ║")
    print("  ╚══════════════════════════════════════╝")
    print()
    
    ideas = []
    ai_descriptions = []
    
    # 如果是 reroll 模式，先生成一个基础创意
    if args.reroll:
        idea = generate_idea(hard_mode=args.hard, tech_filter=args.tech)
        idea = reroll_component(idea, args.reroll)
        ideas.append(idea)
        
        if args.ai:
            print(f"  🤖 正在生成 AI 描述...")
            ai_desc = get_ai_description(idea)
            ai_descriptions.append(ai_desc)
            if ai_desc:
                print(format_ai_idea(idea, ai_desc))
            else:
                print(format_idea(idea))
            save_to_history(idea, ai_desc)
        else:
            print(format_idea(idea))
            save_to_history(idea)
    else:
        for i in range(args.count):
            idea = generate_idea(hard_mode=args.hard, tech_filter=args.tech)
            ideas.append(idea)
            
            if args.ai:
                print(f"  🤖 正在为第 {i+1} 个项目生成 AI 描述...")
                ai_desc = get_ai_description(idea)
                ai_descriptions.append(ai_desc)
                if ai_desc:
                    print(format_ai_idea(idea, ai_desc, index=i+1 if args.count > 1 else None))
                else:
                    print(format_idea(idea, index=i+1 if args.count > 1 else None))
                save_to_history(idea, ai_desc)
            else:
                print(format_idea(idea, index=i+1 if args.count > 1 else None))
                save_to_history(idea)
            
            print()
    
    # 生成骨架
    if args.scaffold:
        print("  🏗️  正在生成项目骨架...")
        for i, idea in enumerate(ideas):
            ai_desc = ai_descriptions[i] if i < len(ai_descriptions) and ai_descriptions[i] else None
            project_dir = generate_scaffold(idea, ai_desc)
            print(f"  ✅ 项目骨架已生成: {project_dir}")
        print()
    
    if args.save:
        save_ideas(ideas, ai_descriptions if args.ai else None)
    
    # 导出功能
    if args.export is not None:
        fmt = args.export.lower()
        ai_descs = ai_descriptions if args.ai else None
        if fmt == "json":
            export_json(ideas, ai_descs, args.export_file)
        elif fmt == "csv":
            export_csv(ideas, ai_descs, args.export_file)
        elif fmt in ("md", "markdown"):
            export_markdown(ideas, ai_descs, args.export_file)
        else:
            print(f"\n  ⚠️  不支持的导出格式: {fmt} (支持: json, csv, md)")
    
    encouragements = [
        "去吧，写点有意思的东西！🚀",
        "别想了，开搞！💻",
        "这个看起来很酷，试试看！✨",
        "Vibe coding time! 🎵",
        "代码写起来，咖啡泡起来！☕",
        "今天就从这个开始！🔥",
    ]
    print(f"  {random.choice(encouragements)}")
    print()

if __name__ == "__main__":
    main()
