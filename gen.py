#!/usr/bin/env python3
"""
🎲 Random Project Generator
随机组合技术栈 + 项目类型 + 领域，帮你找灵感！

Usage:
    python gen.py              # 生成 1 个项目创意
    python gen.py -n 5         # 生成 5 个
    python gen.py --save       # 生成并保存到 ideas.md
    python gen.py --hard       # 只生成高难度项目
"""

import random
import argparse
from datetime import datetime

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
# 生成逻辑
# ═══════════════════════════════════════════

def generate_idea(hard_mode=False):
    """生成一个随机项目创意"""
    tech = random.choice(TECH_STACKS)
    proj = random.choice(PROJECT_TYPES)
    theme = random.choice(THEMES)
    
    if hard_mode:
        diff = random.choice(DIFFICULTIES[2:])  # 只选高难度
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

def format_idea(idea, index=None):
    """格式化输出一个创意"""
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
    
    # 生成项目名称建议
    name_ideas = [
        f"{t['name']}{th['name']}{p['name'].replace(' ', '')}",
        f"{th['name']}Hub",
        f"{p['name'].replace(' ', '')}X",
        f"Vibe{th['name']}",
    ]
    suggested_name = random.choice(name_ideas)
    lines.append(f"  📦 建议项目名: {suggested_name}")
    
    return "\n".join(lines)

def save_ideas(ideas, filename="ideas.md"):
    """保存创意到 markdown 文件"""
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"\n## 💡 Ideas — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        for i, idea in enumerate(ideas, 1):
            t = idea["tech"]
            p = idea["project"]
            th = idea["theme"]
            d = idea["difficulty"]
            w = idea["twist"]
            f.write(f"### {i}. {t['emoji']} {t['name']} + {p['name']} + {th['name']}\n")
            f.write(f"- **技术栈**: {t['name']}\n")
            f.write(f"- **类型**: {p['name']} — {p['desc']}\n")
            f.write(f"- **领域**: {th['name']} — {th['desc']}\n")
            f.write(f"- **难度**: {d['name']} ({d['hours']})\n")
            f.write(f"- **Twist**: {w}\n\n")
    
    print(f"\n  💾 已保存到 {filename}")

# ═══════════════════════════════════════════
# 主程序
# ═══════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="🎲 Random Project Generator")
    parser.add_argument("-n", "--count", type=int, default=1, help="生成数量 (默认 1)")
    parser.add_argument("--save", action="store_true", help="保存到 ideas.md")
    parser.add_argument("--hard", action="store_true", help="只生成高难度项目")
    args = parser.parse_args()
    
    print()
    print("  ╔══════════════════════════════════════╗")
    print("  ║   🎲 Random Project Generator        ║")
    print("  ║   帮你找到下一个 vibecoding 项目!     ║")
    print("  ╚══════════════════════════════════════╝")
    print()
    
    ideas = []
    for i in range(args.count):
        idea = generate_idea(hard_mode=args.hard)
        ideas.append(idea)
        print(format_idea(idea, index=i+1 if args.count > 1 else None))
        print()
    
    if args.save:
        save_ideas(ideas)
    
    # 彩蛋：随机鼓励语
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
