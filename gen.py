#!/usr/bin/env python3
"""
🎲 Random Project Generator v3.3
随机组合技术栈 + 项目类型 + 领域，帮你找灵感！
✨ 终端美化：自动检测 Rich 库，提供彩色输出和精美面板

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
    python3 gen.py --score             # 显示项目评分
    python3 gen.py -n 3 --score --ai   # AI + 评分组合
    python3 gen.py --deps              # 显示推荐依赖库
    python3 gen.py --deps --score      # 依赖推荐 + 评分组合
    python3 gen.py --config-show       # 查看当前配置
    python3 gen.py --config-set count 3   # 设置默认生成数量为 3
    python3 gen.py --config-set ai true   # 默认开启 AI 描述
    python3 gen.py --config-set preferred_tech python,rust  # 设置偏好技术栈
    python3 gen.py --config-reset      # 重置为默认配置
    python3 gen.py --no-animation       # 禁用加载动画
    python3 gen.py --config-set animation false  # 禁用加载动画
    python3 gen.py --deploy             # 显示部署指南 (Docker/云平台)
    python3 gen.py --deps --deploy      # 依赖推荐 + 部署指南组合
    python3 gen.py --cicd               # 生成 CI/CD 配置 (GitHub Actions)
    python3 gen.py --cicd --deploy      # CI/CD + 部署指南组合
    python3 gen.py --scaffold --cicd    # 骨架 + CI/CD 一步到位
"""

import random
import argparse
import json
import csv
import os
import sys
import time
import hashlib
from datetime import datetime
from collections import Counter

# ═══════════════════════════════════════════
# Rich 终端美化 (可选依赖)
# ═══════════════════════════════════════════
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich.columns import Columns
    from rich import box
    from rich.status import Status
    from rich.live import Live
    from rich.spinner import Spinner
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None
HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".gen_history.json")
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".gen_config.json")

# 全局动画开关覆盖（命令行 --no-animation 使用，不持久化）
_ANIMATION_OVERRIDE = None  # None = 使用配置, True/False = 强制覆盖

# 默认配置
DEFAULT_CONFIG = {
    "count": 1,
    "hard": False,
    "ai": False,
    "score": False,
    "deps": False,
    "scaffold": False,
    "deploy": False,
    "export_format": None,
    "preferred_tech": [],
    "theme": "auto",  # auto / dark / light (预留)
    "animation": True,  # 是否显示加载动画
}




# ═══════════════════════════════════════════
# 动画效果
# ═══════════════════════════════════════════

# 有趣的加载消息（随机显示，增加趣味性）
ANIMATION_MESSAGES = [
    "🎲 掷骰子中...",
    "🔮 水晶球占卜中...",
    "🧠 灵感生成中...",
    "⚡ 量子纠缠计算中...",
    "🎯 正在瞄准好创意...",
    "🌀 打开脑洞中...",
    "✨ 魔法粉末调配中...",
    "🎰 创意老虎机转转转...",
    "🧬 组合基因序列中...",
    "🚀 发射灵感火箭...",
    "🎨 调色板混色中...",
    "💡 灯泡正在点亮...",
    "🔥 灵感引擎预热中...",
    "🎪 创意马戏团开场...",
    "🌟 星光闪烁中...",
]

# AI 专用加载消息
AI_ANIMATION_MESSAGES = [
    "🤖 AI 正在深度思考...",
    "🧠 神经网络推理中...",
    "💬 AI 助手构思中...",
    "🔮 AI 预测最佳方案...",
    "✨ AI 创意工坊运转中...",
    "📝 AI 正在撰写描述...",
    "🎯 AI 分析最佳组合...",
    "⚡ AI 加速推理中...",
]

# Scaffold 专用加载消息
SCAFFOLD_ANIMATION_MESSAGES = [
    "🏗️  脚手架搭建中...",
    "📂 文件目录结构生成中...",
    "📝 模板文件填充中...",
    "🔧 项目骨架组装中...",
    "🎨 工程脚手架绘制中...",
]


def animated_operation(message_type, func, *args, **kwargs):
    """带动画的操作包装器

    Args:
        message_type: 消息类型 (default/ai/scaffold)
        func: 要执行的函数
        *args, **kwargs: 传递给函数的参数

    Returns:
        函数返回值
    """
    cfg = load_config()
    use_animation = (_ANIMATION_OVERRIDE if _ANIMATION_OVERRIDE is not None else cfg.get("animation", True)) and RICH_AVAILABLE

    if not use_animation:
        return func(*args, **kwargs)

    # 选择消息列表
    if message_type == "ai":
        messages = AI_ANIMATION_MESSAGES
        spinner = "dots12"
    elif message_type == "scaffold":
        messages = SCAFFOLD_ANIMATION_MESSAGES
        spinner = "bouncingBar"
    else:
        messages = ANIMATION_MESSAGES
        spinner = "dots"

    msg = random.choice(messages)

    with Status(msg, console=console, spinner=spinner, spinner_style="bright_cyan"):
        result = func(*args, **kwargs)

    return result


def show_brief_animation(message_type="default", duration=0.8):
    """显示短暂的加载动画（不需要执行函数时使用）

    Args:
        message_type: 消息类型
        duration: 动画持续时间（秒）
    """
    cfg = load_config()
    use_animation = (_ANIMATION_OVERRIDE if _ANIMATION_OVERRIDE is not None else cfg.get("animation", True)) and RICH_AVAILABLE
    if not use_animation:
        return

    if message_type == "ai":
        messages = AI_ANIMATION_MESSAGES
        spinner = "dots12"
    elif message_type == "scaffold":
        messages = SCAFFOLD_ANIMATION_MESSAGES
        spinner = "bouncingBar"
    else:
        messages = ANIMATION_MESSAGES
        spinner = "dots"

    msg = random.choice(messages)

    with Status(msg, console=console, spinner=spinner, spinner_style="bright_cyan"):
        time.sleep(duration)


# ═══════════════════════════════════════════
# 配置文件管理
# ═══════════════════════════════════════════

def load_config():
    """加载用户配置，不存在则返回默认配置"""
    if not os.path.exists(CONFIG_FILE):
        return dict(DEFAULT_CONFIG)
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            user_cfg = json.load(f)
        # 合并：用户配置覆盖默认值，但忽略未知键
        cfg = dict(DEFAULT_CONFIG)
        for key in DEFAULT_CONFIG:
            if key in user_cfg:
                cfg[key] = user_cfg[key]
        return cfg
    except (json.JSONDecodeError, IOError):
        return dict(DEFAULT_CONFIG)


def save_config(cfg):
    """保存配置到文件"""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def set_config_value(key, value):
    """设置单个配置项"""
    if key not in DEFAULT_CONFIG:
        return False, f"未知配置项: {key}"
    cfg = load_config()
    # 类型校验
    expected = DEFAULT_CONFIG[key]
    if isinstance(expected, bool):
        value = str(value).lower() in ("true", "1", "yes", "on")
    elif isinstance(expected, int):
        try:
            value = int(value)
        except ValueError:
            return False, f"{key} 需要整数值"
    elif key == "preferred_tech":
        # 逗号分隔列表
        value = [t.strip() for t in str(value).split(",") if t.strip()]
    elif key == "export_format":
        if value and value not in ("json", "csv", "md", "markdown"):
            return False, f"不支持的导出格式: {value} (支持: json, csv, md)"
        value = value if value else None

    cfg[key] = value
    save_config(cfg)
    return True, f"✅ {key} = {value!r}"


def reset_config():
    """重置为默认配置"""
    save_config(dict(DEFAULT_CONFIG))


def print_config():
    """打印当前配置"""
    cfg = load_config()
    is_default = not os.path.exists(CONFIG_FILE)

    if RICH_AVAILABLE:
        table = Table(title="⚙️  当前配置", box=box.ROUNDED,
                      border_style="bright_blue", show_lines=False, expand=False)
        table.add_column("配置项", style="bold cyan", width=18)
        table.add_column("当前值", style="bright_white", width=20)
        table.add_column("默认值", style="dim", width=20)
        table.add_column("说明", style="white", width=28)

        descriptions = {
            "count": "默认生成数量",
            "hard": "默认开启高难度模式",
            "ai": "默认开启 AI 描述",
            "score": "默认显示项目评分",
            "deps": "默认显示依赖推荐",
            "scaffold": "默认生成项目骨架",
            "deploy": "默认显示部署指南",
            "export_format": "默认导出格式",
            "preferred_tech": "偏好技术栈",
            "theme": "界面主题 (预留)",
            "animation": "加载动画效果",
        }
        for key in DEFAULT_CONFIG:
            cur = cfg[key]
            def_val = DEFAULT_CONFIG[key]
            changed = "🔴" if cur != def_val else "🟢"
            desc = descriptions.get(key, "")
            table.add_row(
                f"{changed} {key}",
                str(cur),
                str(def_val),
                desc,
            )

        console.print()
        console.print(table)
        if is_default:
            console.print("  [dim]📂 配置文件尚未创建，使用默认值。使用 --config-set 设置偏好。[/dim]")
        else:
            console.print(f"  [dim]📂 配置文件: {CONFIG_FILE}[/dim]")
        console.print()
    else:
        print()
        print("  ╔══════════════════════════════════════╗")
        print("  ║         ⚙️  当前配置                  ║")
        print("  ╚══════════════════════════════════════╝")
        print()
        for key in DEFAULT_CONFIG:
            cur = cfg[key]
            def_val = DEFAULT_CONFIG[key]
            changed = " 🔴" if cur != def_val else " 🟢"
            print(f"  {changed} {key:<18} = {cur!r:<16} (默认: {def_val!r})")
        if is_default:
            print(f"\n  📂 配置文件尚未创建，使用默认值。")
        else:
            print(f"\n  📂 配置文件: {CONFIG_FILE}")
        print()


def apply_config_defaults(args):
    """将配置文件中的默认值应用到未明确指定的 CLI 参数上。
    返回修改后的 args 对象。"""
    cfg = load_config()
    # 只对用户没在命令行显式指定的参数应用配置默认值
    # argparse 不提供 easy way 检测"是否显式传入"，所以我们比较默认值

    global _ANIMATION_OVERRIDE
    if args.no_animation:
        _ANIMATION_OVERRIDE = False

    if args.count == 1 and cfg["count"] != 1:
        args.count = cfg["count"]
    if not args.hard and cfg["hard"]:
        args.hard = True
    if not args.ai and cfg["ai"]:
        args.ai = True
    if not args.score and cfg["score"]:
        args.score = True
    if not args.deps and cfg["deps"]:
        args.deps = True
    if not args.scaffold and cfg["scaffold"]:
        args.scaffold = True
    if not args.deploy and cfg["deploy"]:
        args.deploy = True
    if args.export is None and cfg.get("export_format"):
        args.export = cfg["export_format"]
    # preferred_tech 仅在 --tech 未指定时使用
    if not args.tech and cfg.get("preferred_tech"):
        args.tech = ",".join(cfg["preferred_tech"])
    return args


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

def save_to_history(idea, ai_desc=None, score=None):
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
    if score:
        record["score"] = score["total"]
        record["grade"] = score["grade"]
    history.append(record)
    # 保留最近 500 条
    if len(history) > 500:
        history = history[-500:]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def print_history(limit=20):
    """打印最近的历史记录（支持 Rich 美化）"""
    history = load_history()
    if not history:
        if RICH_AVAILABLE:
            console.print(Panel("[italic]暂无历史记录，快去生成一些创意吧！[/italic]",
                                title="📜 历史记录", border_style="yellow"))
        else:
            print("\n  📜 暂无历史记录，快去生成一些创意吧！\n")
        return

    recent = history[-limit:][::-1]  # 最新的在前
    
    if RICH_AVAILABLE:
        table = Table(title="📜 历史记录 (最近生成)", box=box.ROUNDED,
                      border_style="bright_yellow", show_lines=False)
        table.add_column("#", style="dim", width=4, justify="right")
        table.add_column("时间", style="cyan", width=12)
        table.add_column("技术栈", style="green", width=10)
        table.add_column("项目类型", style="yellow", width=12)
        table.add_column("领域", style="magenta", width=10)
        table.add_column("项目名", style="bright_white", width=20)
        
        for i, rec in enumerate(recent, 1):
            ts = rec.get("timestamp", "?")
            try:
                dt = datetime.fromisoformat(ts)
                ts_str = dt.strftime("%m-%d %H:%M")
            except Exception:
                ts_str = ts[:16]
            name = rec.get("project_name", "")
            table.add_row(str(i), ts_str, rec["tech"], rec["project"], rec["theme"], name or "—")
        
        console.print()
        console.print(table)
        console.print(f"\n  [dim]共 {len(history)} 条记录 (显示最近 {len(recent)} 条)[/dim]\n")
    else:
        print()
        print("  ╔══════════════════════════════════════╗")
        print("  ║       📜 历史记录 (最近生成)          ║")
        print("  ╚══════════════════════════════════════╝")
        print()

        for i, rec in enumerate(recent, 1):
            ts = rec.get("timestamp", "?")
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
    """打印使用统计（支持 Rich 美化）"""
    history = load_history()
    if not history:
        if RICH_AVAILABLE:
            console.print(Panel("[italic]暂无统计数据，快去生成一些创意吧！[/italic]",
                                title="📊 使用统计", border_style="bright_green"))
        else:
            print("\n  📊 暂无统计数据，快去生成一些创意吧！\n")
        return

    tech_counts = Counter(r["tech"] for r in history)
    project_counts = Counter(r["project"] for r in history)
    theme_counts = Counter(r["theme"] for r in history)
    diff_counts = Counter(r["difficulty"] for r in history)
    total = len(history)

    # 显示重复创意
    combos = Counter((r["tech"], r["project"], r["theme"]) for r in history)
    duplicates = [(k, v) for k, v in combos.items() if v > 1]

    if RICH_AVAILABLE:
        from rich.progress_bar import ProgressBar
        from rich.measure import Measurement
        
        console.print()
        console.print(Panel(f"[bold bright_white]📈 总计生成 {total} 个创意[/bold bright_white]",
                            title="📊 使用统计", border_style="bright_green", expand=False))
        
        def make_stat_table(title, counts, top_n=10, color="cyan"):
            table = Table(title=title, box=box.SIMPLE_HEAVY, border_style=color, 
                          show_lines=False, expand=False)
            table.add_column("", style="dim", width=3, justify="right")
            table.add_column("名称", style=f"bold {color}", width=14)
            table.add_column("频率", justify="right", width=6)
            table.add_column("分布", width=25)
            table.add_column("%", justify="right", width=7)
            
            for rank, (name, cnt) in enumerate(counts.most_common(top_n), 1):
                pct = cnt / total * 100
                bar_len = int(20 * cnt / total)
                bar = "█" * bar_len + "░" * (20 - bar_len)
                table.add_row(str(rank), name, str(cnt), f"[{color}]{bar}[/{color}]", f"{pct:.1f}%")
            return table
        
        console.print()
        console.print(make_stat_table("🔧 技术栈 TOP 10", tech_counts, color="green"))
        console.print()
        console.print(make_stat_table("📁 项目类型 TOP 10", project_counts, color="yellow"))
        console.print()
        console.print(make_stat_table("🎨 领域 TOP 10", theme_counts, color="magenta"))
        console.print()
        
        # 难度分布
        diff_table = Table(title="⚡ 难度分布", box=box.SIMPLE_HEAVY, border_style="red",
                           show_lines=False, expand=False)
        diff_table.add_column("", style="dim", width=3, justify="right")
        diff_table.add_column("难度", style="bold red", width=14)
        diff_table.add_column("频率", justify="right", width=6)
        diff_table.add_column("分布", width=25)
        diff_table.add_column("%", justify="right", width=7)
        for rank, (name, cnt) in enumerate(diff_counts.most_common(), 1):
            pct = cnt / total * 100
            bar_len = int(20 * cnt / total)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            diff_table.add_row(str(rank), name, str(cnt), f"[red]{bar}[/red]", f"{pct:.1f}%")
        console.print()
        console.print(diff_table)
        
        if duplicates:
            console.print()
            dup_table = Table(title=f"⚠️ 重复组合 ({len(duplicates)} 组)", box=box.SIMPLE_HEAVY,
                              border_style="bright_yellow", show_lines=False, expand=False)
            dup_table.add_column("技术栈", style="green")
            dup_table.add_column("项目类型", style="yellow")
            dup_table.add_column("领域", style="magenta")
            dup_table.add_column("次数", style="bold red", justify="right")
            for (tech, proj, theme), cnt in sorted(duplicates, key=lambda x: -x[1])[:5]:
                dup_table.add_row(tech, proj, theme, str(cnt))
            console.print(dup_table)
        
        console.print()
    else:
        def print_bar(label, count, total_val, width=20):
            filled = int(width * count / total_val) if total_val else 0
            bar = "█" * filled + "░" * (width - filled)
            pct = count / total_val * 100 if total_val else 0
            print(f"    {label:<12} {bar} {count:>4} ({pct:>5.1f}%)")

        print()
        print("  ╔══════════════════════════════════════╗")
        print("  ║         📊 使用统计                  ║")
        print("  ╚══════════════════════════════════════╝")
        print()
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
# 依赖推荐库
# ═══════════════════════════════════════════

DEP_RECOMMENDATIONS = {
    "Python": [
        {"name": "requests", "desc": "HTTP 请求库", "category": "网络"},
        {"name": "fastapi", "desc": "高性能 Web 框架", "category": "Web"},
        {"name": "pydantic", "desc": "数据验证与序列化", "category": "数据"},
        {"name": "rich", "desc": "终端美化输出", "category": "CLI"},
        {"name": "click", "desc": "命令行框架", "category": "CLI"},
        {"name": "sqlalchemy", "desc": "ORM 数据库工具", "category": "数据库"},
        {"name": "pytest", "desc": "测试框架", "category": "测试"},
        {"name": "pandas", "desc": "数据处理分析", "category": "数据"},
        {"name": "pillow", "desc": "图像处理", "category": "多媒体"},
        {"name": "celery", "desc": "异步任务队列", "category": "异步"},
        {"name": "httpx", "desc": "异步 HTTP 客户端", "category": "网络"},
        {"name": "typer", "desc": "类型安全 CLI 框架", "category": "CLI"},
    ],
    "Node.js": [
        {"name": "express", "desc": "Web 框架", "category": "Web"},
        {"name": "axios", "desc": "HTTP 请求库", "category": "网络"},
        {"name": "prisma", "desc": "现代化 ORM", "category": "数据库"},
        {"name": "zod", "desc": "数据验证库", "category": "数据"},
        {"name": "chalk", "desc": "终端颜色", "category": "CLI"},
        {"name": "commander", "desc": "命令行框架", "category": "CLI"},
        {"name": "jest", "desc": "测试框架", "category": "测试"},
        {"name": "socket.io", "desc": "实时通信", "category": "实时"},
        {"name": "bull", "desc": "任务队列", "category": "异步"},
        {"name": "winston", "desc": "日志框架", "category": "工具"},
        {"name": "dotenv", "desc": "环境变量管理", "category": "配置"},
        {"name": "lodash", "desc": "工具函数库", "category": "工具"},
    ],
    "Rust": [
        {"name": "tokio", "desc": "异步运行时", "category": "异步"},
        {"name": "serde", "desc": "序列化框架", "category": "数据"},
        {"name": "clap", "desc": "命令行解析", "category": "CLI"},
        {"name": "reqwest", "desc": "HTTP 客户端", "category": "网络"},
        {"name": "axum", "desc": "Web 框架", "category": "Web"},
        {"name": "sqlx", "desc": "异步数据库", "category": "数据库"},
        {"name": "anyhow", "desc": "错误处理", "category": "工具"},
        {"name": "tracing", "desc": "日志追踪", "category": "工具"},
        {"name": "crossterm", "desc": "终端操作", "category": "CLI"},
        {"name": "rayon", "desc": "并行计算", "category": "性能"},
    ],
    "Go": [
        {"name": "gin", "desc": "Web 框架", "category": "Web"},
        {"name": "cobra", "desc": "命令行框架", "category": "CLI"},
        {"name": "gorm", "desc": "ORM 框架", "category": "数据库"},
        {"name": "zap", "desc": "高性能日志", "category": "工具"},
        {"name": "viper", "desc": "配置管理", "category": "配置"},
        {"name": "testify", "desc": "测试工具集", "category": "测试"},
        {"name": "fiber", "desc": "Express 风格 Web 框架", "category": "Web"},
        {"name": "pgx", "desc": "PostgreSQL 驱动", "category": "数据库"},
        {"name": "go-redis", "desc": "Redis 客户端", "category": "数据库"},
        {"name": "wire", "desc": "依赖注入", "category": "架构"},
    ],
    "TypeScript": [
        {"name": "zod", "desc": "类型安全验证", "category": "数据"},
        {"name": "trpc", "desc": "类型安全 RPC", "category": "API"},
        {"name": "next", "desc": "React 全栈框架", "category": "Web"},
        {"name": "prisma", "desc": "现代化 ORM", "category": "数据库"},
        {"name": "vitest", "desc": "Vite 测试框架", "category": "测试"},
        {"name": "effect", "desc": "函数式效果系统", "category": "架构"},
        {"name": "drizzle-orm", "desc": "轻量 TypeScript ORM", "category": "数据库"},
        {"name": "hono", "desc": "轻量 Web 框架", "category": "Web"},
    ],
    "React": [
        {"name": "zustand", "desc": "轻量状态管理", "category": "状态"},
        {"name": "tanstack-query", "desc": "数据请求管理", "category": "数据"},
        {"name": "react-hook-form", "desc": "表单管理", "category": "表单"},
        {"name": "framer-motion", "desc": "动画库", "category": "UI"},
        {"name": "shadcn/ui", "desc": "组件库", "category": "UI"},
        {"name": "tailwindcss", "desc": "原子化 CSS", "category": "样式"},
        {"name": "react-router", "desc": "路由", "category": "路由"},
        {"name": "react-query", "desc": "异步状态管理", "category": "数据"},
    ],
    "Vue": [
        {"name": "pinia", "desc": "状态管理", "category": "状态"},
        {"name": "vue-router", "desc": "路由管理", "category": "路由"},
        {"name": "nuxt", "desc": "全栈框架", "category": "Web"},
        {"name": "vuetify", "desc": "Material 组件库", "category": "UI"},
        {"name": "vueuse", "desc": "组合式工具集", "category": "工具"},
        {"name": "element-plus", "desc": "企业级组件库", "category": "UI"},
    ],
    "Svelte": [
        {"name": "sveltekit", "desc": "全栈框架", "category": "Web"},
        {"name": "svelte-routing", "desc": "路由", "category": "路由"},
        {"name": "skeleton", "desc": "UI 组件库", "category": "UI"},
        {"name": "mdsvex", "desc": "Markdown 预处理", "category": "内容"},
    ],
    "Flutter": [
        {"name": "riverpod", "desc": "状态管理", "category": "状态"},
        {"name": "dio", "desc": "HTTP 客户端", "category": "网络"},
        {"name": "go_router", "desc": "声明式路由", "category": "路由"},
        {"name": "flutter_bloc", "desc": "BLoC 状态管理", "category": "状态"},
        {"name": "hive", "desc": "轻量数据库", "category": "存储"},
        {"name": "freezed", "desc": "不可变数据类", "category": "数据"},
    ],
    "Swift": [
        {"name": "Alamofire", "desc": "网络请求", "category": "网络"},
        {"name": "SwiftUI", "desc": "声明式 UI", "category": "UI"},
        {"name": "Combine", "desc": "响应式编程", "category": "异步"},
        {"name": "Kingfisher", "desc": "图片加载缓存", "category": "多媒体"},
        {"name": "SwiftyJSON", "desc": "JSON 解析", "category": "数据"},
    ],
    "Kotlin": [
        {"name": "ktor", "desc": "Web 框架", "category": "Web"},
        {"name": "koin", "desc": "依赖注入", "category": "架构"},
        {"name": "retrofit", "desc": "类型安全 HTTP", "category": "网络"},
        {"name": "room", "desc": "数据库 ORM", "category": "数据库"},
        {"name": "jetpack-compose", "desc": "声明式 UI", "category": "UI"},
        {"name": "coroutines", "desc": "协程", "category": "异步"},
    ],
    "C++": [
        {"name": "fmt", "desc": "格式化库", "category": "工具"},
        {"name": "spdlog", "desc": "日志库", "category": "工具"},
        {"name": "nlohmann-json", "desc": "JSON 库", "category": "数据"},
        {"name": "catch2", "desc": "测试框架", "category": "测试"},
        {"name": "cmake", "desc": "构建系统", "category": "构建"},
        {"name": "conan", "desc": "包管理", "category": "工具"},
        {"name": "qt", "desc": "GUI 框架", "category": "UI"},
        {"name": "boost", "desc": "通用工具库", "category": "工具"},
    ],
    "Lua": [
        {"name": "luarocks", "desc": "包管理器", "category": "工具"},
        {"name": "penlight", "desc": "标准库扩展", "category": "工具"},
        {"name": "luasocket", "desc": "网络库", "category": "网络"},
        {"name": "cjson", "desc": "JSON 解析", "category": "数据"},
        {"name": "openresty", "desc": "Nginx + Lua 平台", "category": "Web"},
    ],
    "Elixir": [
        {"name": "phoenix", "desc": "Web 框架", "category": "Web"},
        {"name": "ecto", "desc": "数据库框架", "category": "数据库"},
        {"name": "oban", "desc": "后台任务", "category": "异步"},
        {"name": "liveview", "desc": "实时 UI", "category": "实时"},
        {"name": "absinthe", "desc": "GraphQL", "category": "API"},
    ],
    "Zig": [
        {"name": "zap", "desc": "Web 框架", "category": "Web"},
        {"name": "ziglyph", "desc": "Unicode 处理", "category": "文本"},
        {"name": "zigzag", "desc": "SDL2 绑定", "category": "多媒体"},
        {"name": "zon", "desc": "配置格式", "category": "配置"},
    ],
}

# 主题到推荐依赖类别的映射（用于智能排序）
THEME_DEP_CATEGORIES = {
    "效率工具": ["CLI", "工具", "数据", "配置"],
    "健康健身": ["数据", "UI", "存储", "网络"],
    "音乐": ["多媒体", "UI", "网络", "数据"],
    "游戏化": ["UI", "数据库", "实时", "状态"],
    "AI/ML": ["数据", "异步", "网络", "工具"],
    "社交": ["实时", "网络", "数据库", "UI"],
    "学习教育": ["数据", "UI", "存储", "Web"],
    "创意工具": ["UI", "多媒体", "数据", "Web"],
    "自动化": ["异步", "网络", "CLI", "工具"],
    "安全": ["网络", "数据", "CLI", "工具"],
    "DevOps": ["CLI", "网络", "配置", "异步"],
    "金融": ["数据", "数据库", "网络", "UI"],
    "天气环境": ["网络", "数据", "UI", "Web"],
    "美食": ["UI", "数据", "网络", "存储"],
    "宠物": ["UI", "数据", "网络", "存储"],
}


def get_dep_recommendations(idea, top_n=6):
    """根据技术栈和主题智能推荐依赖库"""
    tech_name = idea["tech"]["name"]
    theme_name = idea["theme"]["name"]

    deps = DEP_RECOMMENDATIONS.get(tech_name, [])
    if not deps:
        return []

    # 获取主题偏好的依赖类别
    preferred_cats = THEME_DEP_CATEGORIES.get(theme_name, ["工具", "数据", "Web", "UI"])

    # 按类别匹配度排序
    def sort_key(dep):
        cat = dep["category"]
        if cat in preferred_cats:
            return preferred_cats.index(cat)
        return len(preferred_cats)  # 不匹配的排后面

    sorted_deps = sorted(deps, key=sort_key)
    return sorted_deps[:top_n]


def format_dep_recommendations(idea, top_n=6):
    """格式化依赖推荐输出（支持 Rich 美化）"""
    deps = get_dep_recommendations(idea, top_n)
    if not deps:
        return ""

    tech_name = idea["tech"]["name"]

    if RICH_AVAILABLE:
        table = Table(
            title=f"📦 {tech_name} 推荐依赖库",
            box=box.ROUNDED,
            border_style="bright_green",
            show_lines=False,
            expand=False,
        )
        table.add_column("#", style="dim", width=3, justify="right")
        table.add_column("包名", style="bold bright_cyan", width=18)
        table.add_column("描述", style="white", width=24)
        table.add_column("分类", style="bright_yellow", width=8)

        for i, dep in enumerate(deps, 1):
            table.add_row(str(i), dep["name"], dep["desc"], dep["category"])

        return Panel(
            table,
            title=f"🔧 依赖推荐 — {tech_name}",
            border_style="bright_green",
            expand=False,
        )
    else:
        lines = []
        lines.append(f"  📦 {tech_name} 推荐依赖库:")
        lines.append(f"  {'─' * 40}")
        for i, dep in enumerate(deps, 1):
            lines.append(f"  {i}. {dep['name']:<16} — {dep['desc']} [{dep['category']}]")
        lines.append(f"  {'─' * 40}")
        return "\n".join(lines)

# ═══════════════════════════════════════════
# 部署指南
# ═══════════════════════════════════════════

# 每种技术栈的 Docker 部署模板
DEPLOY_TEMPLATES = {
    "Python": {
        "dockerfile": """FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["python", "main.py"]
""",
        "compose": """version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    environment:
      - ENV=production
""",
        "platforms": ["Heroku", "Railway", "Fly.io", "AWS Lambda"],
        "steps": [
            "创建 Dockerfile 和 docker-compose.yml",
            "构建镜像: docker build -t {project_slug} .",
            "本地测试: docker-compose up",
            "推送镜像: docker push registry/{project_slug}",
            "选择云平台部署 (推荐 Railway 或 Fly.io)",
        ],
    },
    "Node.js": {
        "dockerfile": """FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 3000
CMD ["node", "index.js"]
""",
        "compose": """version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    volumes:
      - .:/app
      - /app/node_modules
    environment:
      - NODE_ENV=production
""",
        "platforms": ["Vercel", "Railway", "Render", "AWS ECS"],
        "steps": [
            "创建 Dockerfile 和 docker-compose.yml",
            "构建镜像: docker build -t {project_slug} .",
            "本地测试: docker-compose up",
            "推送镜像: docker push registry/{project_slug}",
            "选择云平台部署 (推荐 Vercel 或 Railway)",
        ],
    },
    "Rust": {
        "dockerfile": """FROM rust:1.78 as builder

WORKDIR /app
COPY . .
RUN cargo build --release

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*
COPY --from=builder /app/target/release/{project_slug} /usr/local/bin/

EXPOSE 8080
CMD ["{project_slug}"]
""",
        "compose": """version: '3.8'

services:
  app:
    build: .
    ports:
      - "8080:8080"
""",
        "platforms": ["Fly.io", "Railway", "AWS ECS", "DigitalOcean"],
        "steps": [
            "创建多阶段 Dockerfile (减小镜像体积)",
            "构建镜像: docker build -t {project_slug} .",
            "本地测试: docker-compose up",
            "推送镜像: docker push registry/{project_slug}",
            "选择云平台部署 (推荐 Fly.io)",
        ],
    },
    "Go": {
        "dockerfile": """FROM golang:1.22-alpine AS builder

WORKDIR /app
COPY go.* ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o {project_slug} .

FROM alpine:latest
RUN apk --no-cache add ca-certificates
COPY --from=builder /app/{project_slug} /usr/local/bin/

EXPOSE 8080
CMD ["{project_slug}"]
""",
        "compose": """version: '3.8'

services:
  app:
    build: .
    ports:
      - "8080:8080"
""",
        "platforms": ["Fly.io", "Railway", "Google Cloud Run", "AWS Lambda"],
        "steps": [
            "创建多阶段 Dockerfile",
            "构建镜像: docker build -t {project_slug} .",
            "本地测试: docker-compose up",
            "推送镜像: docker push registry/{project_slug}",
            "选择云平台部署 (推荐 Fly.io 或 Google Cloud Run)",
        ],
    },
    "TypeScript": {
        "dockerfile": """FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
COPY tsconfig.json ./
RUN npm ci

COPY . .
RUN npm run build

EXPOSE 3000
CMD ["node", "dist/index.js"]
""",
        "compose": """version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
""",
        "platforms": ["Vercel", "Railway", "Render", "Fly.io"],
        "steps": [
            "创建 Dockerfile (先编译 TS 再运行)",
            "构建镜像: docker build -t {project_slug} .",
            "本地测试: docker-compose up",
            "推送镜像: docker push registry/{project_slug}",
            "选择云平台部署 (推荐 Vercel)",
        ],
    },
    "default": {
        "dockerfile": """FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \\
    build-essential \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

EXPOSE 8080
CMD ["./run.sh"]
""",
        "compose": """version: '3.8'

services:
  app:
    build: .
    ports:
      - "8080:8080"
    volumes:
      - .:/app
""",
        "platforms": ["Railway", "Fly.io", "DigitalOcean", "AWS"],
        "steps": [
            "根据技术栈创建 Dockerfile",
            "构建镜像: docker build -t {project_slug} .",
            "本地测试: docker-compose up",
            "推送镜像: docker push registry/{project_slug}",
            "选择云平台部署",
        ],
    },
}


def format_deploy_guide(idea, ai_desc=None):
    """格式化部署指南输出（支持 Rich 美化）"""
    tech_name = idea["tech"]["name"]
    project_slug = (ai_desc["project_name"] if ai_desc else f"{tech_name}Project").lower().replace(" ", "-")

    template = DEPLOY_TEMPLATES.get(tech_name, DEPLOY_TEMPLATES["default"])

    if RICH_AVAILABLE:
        dockerfile_content = template["dockerfile"].replace("{project_slug}", project_slug)
        compose_content = template["compose"].replace("{project_slug}", project_slug)

        from rich.syntax import Syntax

        parts = []
        parts.append(f"[bold bright_white]🐳 Docker 部署指南 — {tech_name}[/bold bright_white]\n")

        # 部署步骤
        steps_text = ""
        for i, step in enumerate(template["steps"], 1):
            step_fmt = step.replace("{project_slug}", project_slug)
            steps_text += f"  {i}. {step_fmt}\n"
        parts.append(f"[bold bright_cyan]📋 部署步骤:[/bold bright_cyan]\n{steps_text}")

        # 推荐平台
        platforms = " | ".join(f"[bold]{p}[/bold]" for p in template["platforms"])
        parts.append(f"[bold bright_green]☁️  推荐平台:[/bold bright_green] {platforms}\n")

        # Dockerfile
        parts.append("[bold bright_yellow]📄 Dockerfile:[/bold bright_yellow]")
        parts.append(Syntax(dockerfile_content.rstrip(), "docker", theme="monokai", line_numbers=False))

        # docker-compose.yml
        parts.append("[bold bright_yellow]📄 docker-compose.yml:[/bold bright_yellow]")
        parts.append(Syntax(compose_content.rstrip(), "yaml", theme="monokai", line_numbers=False))

        from rich.console import Group
        renderable = Group(*parts)
        return Panel(renderable, title=f"🚀 部署指南 — {tech_name}",
                      border_style="bright_blue", expand=False, padding=(1, 2))
    else:
        lines = []
        lines.append(f"  🐳 Docker 部署指南 — {tech_name}")
        lines.append(f"  {'═' * 44}")

        # 部署步骤
        lines.append(f"\n  📋 部署步骤:")
        for i, step in enumerate(template["steps"], 1):
            step_fmt = step.replace("{project_slug}", project_slug)
            lines.append(f"    {i}. {step_fmt}")

        # 推荐平台
        platforms = " | ".join(template["platforms"])
        lines.append(f"\n  ☁️  推荐平台: {platforms}")

        # Dockerfile
        dockerfile_content = template["dockerfile"].replace("{project_slug}", project_slug)
        lines.append(f"\n  📄 Dockerfile:")
        lines.append(f"  {'─' * 40}")
        for line in dockerfile_content.strip().split("\n"):
            lines.append(f"    {line}")

        # docker-compose.yml
        compose_content = template["compose"].replace("{project_slug}", project_slug)
        lines.append(f"\n  📄 docker-compose.yml:")
        lines.append(f"  {'─' * 40}")
        for line in compose_content.strip().split("\n"):
            lines.append(f"    {line}")

        lines.append(f"\n  {'═' * 44}")
        return "\n".join(lines)


# ═══════════════════════════════════════════
# CI/CD 配置模板 (GitHub Actions)
# ═══════════════════════════════════════════

CICD_TEMPLATES = {
    "Python": {
        "filename": ".github/workflows/ci.yml",
        "content": (
            "name: CI\n"
            "\n"
            "on:\n"
            "  push:\n"
            "    branches: [main, develop]\n"
            "  pull_request:\n"
            "    branches: [main]\n"
            "\n"
            "jobs:\n"
            "  test:\n"
            "    runs-on: ubuntu-latest\n"
            "    strategy:\n"
            "      matrix:\n"
            '        python-version: ["3.10", "3.11", "3.12"]\n'
            "\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "\n"
            "      - name: Set up Python ${{{{ matrix.python-version }}}}\n"
            "        uses: actions/setup-python@v5\n"
            "        with:\n"
            "          python-version: ${{{{ matrix.python-version }}}}\n"
            "\n"
            "      - name: Install dependencies\n"
            "        run: |\n"
            "          python -m pip install --upgrade pip\n"
            "          pip install -r requirements.txt\n"
            "          pip install pytest pytest-cov flake8\n"
            "\n"
            "      - name: Lint\n"
            "        run: flake8 . --max-line-length=120 --exclude=venv\n"
            "\n"
            "      - name: Test\n"
            "        run: pytest --cov=. --cov-report=xml\n"
            "\n"
            "  deploy:\n"
            "    needs: test\n"
            "    runs-on: ubuntu-latest\n"
            "    if: github.ref == 'refs/heads/main' && github.event_name == 'push'\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "      - name: Build Docker image\n"
            "        run: docker build -t {project_slug} .\n"
        ),
        "platform": "GitHub Actions",
        "features": ["多版本 Python 矩阵测试", "Flake8 代码检查", "Pytest 覆盖率报告", "自动 Docker 构建"],
    },
    "Node.js": {
        "filename": ".github/workflows/ci.yml",
        "content": (
            "name: CI\n"
            "\n"
            "on:\n"
            "  push:\n"
            "    branches: [main, develop]\n"
            "  pull_request:\n"
            "    branches: [main]\n"
            "\n"
            "jobs:\n"
            "  test:\n"
            "    runs-on: ubuntu-latest\n"
            "    strategy:\n"
            "      matrix:\n"
            "        node-version: [18, 20, 22]\n"
            "\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "\n"
            "      - name: Use Node.js ${{{{ matrix.node-version }}}}\n"
            "        uses: actions/setup-node@v4\n"
            "        with:\n"
            "          node-version: ${{{{ matrix.node-version }}}}\n"
            "          cache: npm\n"
            "\n"
            "      - name: Install\n"
            "        run: npm ci\n"
            "\n"
            "      - name: Lint\n"
            "        run: npm run lint --if-present\n"
            "\n"
            "      - name: Test\n"
            "        run: npm test -- --coverage\n"
            "\n"
            "  deploy:\n"
            "    needs: test\n"
            "    runs-on: ubuntu-latest\n"
            "    if: github.ref == 'refs/heads/main' && github.event_name == 'push'\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "      - name: Build Docker image\n"
            "        run: docker build -t {project_slug} .\n"
        ),
        "platform": "GitHub Actions",
        "features": ["多版本 Node.js 矩阵测试", "npm 缓存加速", "Lint + 测试", "自动 Docker 构建"],
    },
    "Rust": {
        "filename": ".github/workflows/ci.yml",
        "content": (
            "name: CI\n"
            "\n"
            "on:\n"
            "  push:\n"
            "    branches: [main, develop]\n"
            "  pull_request:\n"
            "    branches: [main]\n"
            "\n"
            "env:\n"
            "  CARGO_TERM_COLOR: always\n"
            "\n"
            "jobs:\n"
            "  test:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "\n"
            "      - name: Install Rust\n"
            "        uses: dtolnay/rust-toolchain@stable\n"
            "        with:\n"
            "          components: rustfmt, clippy\n"
            "\n"
            "      - name: Cache cargo\n"
            "        uses: actions/cache@v4\n"
            "        with:\n"
            "          path: |\n"
            "            ~/.cargo/bin\n"
            "            ~/.cargo/registry\n"
            "            target\n"
            "          key: ${{{{ runner.os }}}}-cargo-${{{{ hashFiles('**/Cargo.lock') }}}}\n"
            "\n"
            "      - name: Format check\n"
            "        run: cargo fmt --check\n"
            "\n"
            "      - name: Clippy lint\n"
            "        run: cargo clippy -- -D warnings\n"
            "\n"
            "      - name: Test\n"
            "        run: cargo test --verbose\n"
            "\n"
            "      - name: Build release\n"
            "        run: cargo build --release\n"
            "\n"
            "  deploy:\n"
            "    needs: test\n"
            "    runs-on: ubuntu-latest\n"
            "    if: github.ref == 'refs/heads/main' && github.event_name == 'push'\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "      - name: Build Docker image\n"
            "        run: docker build -t {project_slug} .\n"
        ),
        "platform": "GitHub Actions",
        "features": ["Cargo 缓存加速", "Rustfmt 格式检查", "Clippy 静态分析", "Release 构建"],
    },
    "Go": {
        "filename": ".github/workflows/ci.yml",
        "content": (
            "name: CI\n"
            "\n"
            "on:\n"
            "  push:\n"
            "    branches: [main, develop]\n"
            "  pull_request:\n"
            "    branches: [main]\n"
            "\n"
            "jobs:\n"
            "  test:\n"
            "    runs-on: ubuntu-latest\n"
            "    strategy:\n"
            "      matrix:\n"
            '        go-version: ["1.21", "1.22"]\n'
            "\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "\n"
            "      - name: Set up Go ${{{{ matrix.go-version }}}}\n"
            "        uses: actions/setup-go@v5\n"
            "        with:\n"
            "          go-version: ${{{{ matrix.go-version }}}}\n"
            "\n"
            "      - name: Vet\n"
            "        run: go vet ./...\n"
            "\n"
            "      - name: Test\n"
            "        run: go test -v -race -coverprofile=coverage.out ./...\n"
            "\n"
            "      - name: Build\n"
            "        run: go build -v -o {project_slug} .\n"
            "\n"
            "  deploy:\n"
            "    needs: test\n"
            "    runs-on: ubuntu-latest\n"
            "    if: github.ref == 'refs/heads/main' && github.event_name == 'push'\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "      - name: Build Docker image\n"
            "        run: docker build -t {project_slug} .\n"
        ),
        "platform": "GitHub Actions",
        "features": ["多版本 Go 矩阵测试", "Go Vet 静态检查", "Race detector 竞态检测", "交叉编译构建"],
    },
    "TypeScript": {
        "filename": ".github/workflows/ci.yml",
        "content": (
            "name: CI\n"
            "\n"
            "on:\n"
            "  push:\n"
            "    branches: [main, develop]\n"
            "  pull_request:\n"
            "    branches: [main]\n"
            "\n"
            "jobs:\n"
            "  test:\n"
            "    runs-on: ubuntu-latest\n"
            "    strategy:\n"
            "      matrix:\n"
            "        node-version: [18, 20, 22]\n"
            "\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "\n"
            "      - name: Use Node.js ${{{{ matrix.node-version }}}}\n"
            "        uses: actions/setup-node@v4\n"
            "        with:\n"
            "          node-version: ${{{{ matrix.node-version }}}}\n"
            "          cache: npm\n"
            "\n"
            "      - name: Install\n"
            "        run: npm ci\n"
            "\n"
            "      - name: Type check\n"
            "        run: npx tsc --noEmit\n"
            "\n"
            "      - name: Lint\n"
            "        run: npm run lint --if-present\n"
            "\n"
            "      - name: Test\n"
            "        run: npm test -- --coverage\n"
            "\n"
            "      - name: Build\n"
            "        run: npm run build\n"
            "\n"
            "  deploy:\n"
            "    needs: test\n"
            "    runs-on: ubuntu-latest\n"
            "    if: github.ref == 'refs/heads/main' && github.event_name == 'push'\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "      - name: Build Docker image\n"
            "        run: docker build -t {project_slug} .\n"
        ),
        "platform": "GitHub Actions",
        "features": ["TypeScript 类型检查", "多版本 Node.js 矩阵", "ESLint 代码规范", "构建产物验证"],
    },
    "default": {
        "filename": ".github/workflows/ci.yml",
        "content": (
            "name: CI\n"
            "\n"
            "on:\n"
            "  push:\n"
            "    branches: [main, develop]\n"
            "  pull_request:\n"
            "    branches: [main]\n"
            "\n"
            "jobs:\n"
            "  build:\n"
            "    runs-on: ubuntu-latest\n"
            "\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "\n"
            "      - name: Build\n"
            '        run: echo "Add your build commands here"\n'
            "\n"
            "      - name: Test\n"
            '        run: echo "Add your test commands here"\n'
            "\n"
            "  deploy:\n"
            "    needs: build\n"
            "    runs-on: ubuntu-latest\n"
            "    if: github.ref == 'refs/heads/main' && github.event_name == 'push'\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "      - name: Build Docker image\n"
            "        run: docker build -t {project_slug} .\n"
        ),
        "platform": "GitHub Actions",
        "features": ["自动构建", "自动测试", "main 分支自动部署", "Docker 镜像构建"],
    },
}


def format_cicd_config(idea, ai_desc=None):
    """格式化 CI/CD 配置输出（支持 Rich 美化）"""
    tech_name = idea["tech"]["name"]
    project_slug = (ai_desc["project_name"] if ai_desc else f"{tech_name}Project").lower().replace(" ", "-")

    template = CICD_TEMPLATES.get(tech_name, CICD_TEMPLATES["default"])
    content = template["content"].replace("{project_slug}", project_slug)

    if RICH_AVAILABLE:
        from rich.syntax import Syntax

        parts = []
        parts.append(f"[bold bright_white]⚙️  CI/CD 配置 — {tech_name}[/bold bright_white]\n")

        # 特性列表
        features_text = ""
        for feat in template["features"]:
            features_text += f"  ✅ {feat}\n"
        parts.append(f"[bold bright_cyan]🔧 CI 特性:[/bold bright_cyan]\n{features_text}")

        parts.append(f"[bold bright_green]📂 文件路径:[/bold bright_green] [cyan]{template['filename']}[/cyan]")
        parts.append(f"[bold bright_green]🏗️  CI 平台:[/bold bright_green] [cyan]{template['platform']}[/cyan]\n")

        # 配置文件内容
        parts.append("[bold bright_yellow]📄 Workflow 配置:[/bold bright_yellow]")
        parts.append(Syntax(content.rstrip(), "yaml", theme="monokai", line_numbers=False))

        from rich.console import Group
        renderable = Group(*parts)
        return Panel(renderable, title=f"⚙️  CI/CD — {tech_name}",
                      border_style="bright_green", expand=False, padding=(1, 2))
    else:
        lines = []
        lines.append(f"  ⚙️  CI/CD 配置 — {tech_name}")
        lines.append(f"  {'═' * 44}")
        lines.append(f"\n  🔧 CI 特性:")
        for feat in template["features"]:
            lines.append(f"    ✅ {feat}")
        lines.append(f"\n  📂 文件路径: {template['filename']}")
        lines.append(f"  🏗️  CI 平台: {template['platform']}")
        lines.append(f"\n  📄 Workflow 配置:")
        lines.append(f"  {'─' * 40}")
        for line in content.strip().split("\n"):
            lines.append(f"    {line}")
        lines.append(f"\n  {'═' * 44}")
        return "\n".join(lines)


# ═══════════════════════════════════════════
# 项目评分系统
# ═══════════════════════════════════════════

# 技术栈创新度权重（新兴/小众技术得分更高）
TECH_INNOVATION = {
    "Zig": 95, "Elixir": 85, "Rust": 80, "Svelte": 75, "Flutter": 70,
    "Kotlin": 65, "Go": 60, "Swift": 55, "TypeScript": 50, "Vue": 50,
    "React": 40, "C++": 40, "Python": 35, "Node.js": 30, "Lua": 70,
}

# 项目类型实用性权重
PROJECT_PRACTICALITY = {
    "CLI 工具": 90, "API 服务": 85, "Web 应用": 80, "桌面应用": 75,
    "移动应用": 75, "数据管道": 80, "微服务": 70, "浏览器扩展": 65,
    "Telegram Bot": 60, "VS Code 扩展": 65, "终端 UI": 55, "游戏": 45,
}

# 主题市场潜力
THEME_POTENTIAL = {
    "AI/ML": 95, "DevOps": 85, "安全": 85, "效率工具": 80, "金融": 80,
    "自动化": 75, "学习教育": 70, "健康健身": 65, "社交": 60, "游戏化": 60,
    "创意工具": 65, "音乐": 55, "美食": 50, "天气环境": 55, "宠物": 45,
}

# Twist 趣味性评分
TWIST_FUN_SCORES = {
    "用 AI 来增强核心体验": 90,
    "加入 gamification 元素": 80,
    "加上 WebSocket 实时通信": 75,
    "支持插件/扩展系统": 75,
    "加上实时协作功能": 80,
    "做一个极简风格的版本": 65,
    "支持 Docker 一键部署": 70,
    "做成开源项目": 70,
    "用 TUI 而不是 GUI": 75,
    "支持多语言国际化": 65,
    "加上暗黑模式（必须的）": 55,
    "但要支持离线使用": 70,
    "而且要完全用 CLI 完成": 60,
    "做一个 mobile-first 的版本": 60,
    "加上完善的测试覆盖": 65,
}


def _seeded_random(idea, salt=""):
    """基于创意内容生成确定性随机数（0-100），确保相同创意得分稳定"""
    key = f"{idea['tech']['name']}|{idea['project']['name']}|{idea['theme']['name']}|{idea['twist']}|{salt}"
    h = hashlib.md5(key.encode()).hexdigest()
    return int(h[:4], 16) % 101  # 0-100


def score_idea(idea):
    """为一个创意打分，返回各维度分数和总分"""
    tech_name = idea["tech"]["name"]
    proj_name = idea["project"]["name"]
    theme_name = idea["theme"]["name"]
    diff_stars = idea["difficulty"]["stars"]
    twist = idea["twist"]

    # 创新度：技术栈创新 + 一点随机波动
    innovation_base = TECH_INNOVATION.get(tech_name, 50)
    innovation_noise = _seeded_random(idea, "innov") % 21 - 10  # -10 ~ +10
    innovation = max(10, min(100, innovation_base + innovation_noise))

    # 实用性：项目类型实用性 + 主题潜力
    practical_base = PROJECT_PRACTICALITY.get(proj_name, 50)
    theme_base = THEME_POTENTIAL.get(theme_name, 50)
    practical_noise = _seeded_random(idea, "pract") % 11 - 5
    practicality = max(10, min(100, int((practical_base * 0.6 + theme_base * 0.4) + practical_noise)))

    # 挑战度：难度星星 * 20 + twist 难度加成
    diff_score = diff_stars * 20
    twist_bonus = TWIST_FUN_SCORES.get(twist, 50) // 5  # 0-18
    challenge_noise = _seeded_random(idea, "chall") % 11 - 5
    challenge = max(10, min(100, diff_score + twist_bonus + challenge_noise))

    # 趣味性：主题 + twist 组合
    theme_fun = THEME_POTENTIAL.get(theme_name, 50)
    twist_fun = TWIST_FUN_SCORES.get(twist, 50)
    fun_noise = _seeded_random(idea, "fun") % 11 - 5
    fun = max(10, min(100, int((theme_fun * 0.4 + twist_fun * 0.6) + fun_noise)))

    # 综合得分（加权平均）
    total = int(innovation * 0.25 + practicality * 0.30 + challenge * 0.20 + fun * 0.25)

    return {
        "innovation": innovation,
        "practicality": practicality,
        "challenge": challenge,
        "fun": fun,
        "total": total,
        "grade": _score_to_grade(total),
    }


def _score_to_grade(score):
    """将分数转为等级"""
    if score >= 90:
        return "S"
    elif score >= 80:
        return "A"
    elif score >= 70:
        return "B"
    elif score >= 60:
        return "C"
    elif score >= 50:
        return "D"
    else:
        return "E"


def _score_bar(value, width=15):
    """生成分数条"""
    filled = int(width * value / 100)
    return "█" * filled + "░" * (width - filled)


def format_score(score_data):
    """格式化评分（支持 Rich）"""
    if RICH_AVAILABLE:
        table = Table(show_header=False, box=box.SIMPLE, padding=(0, 1), expand=False)
        table.add_column("维度", style="bold cyan", no_wrap=True, width=10)
        table.add_column("分数", justify="right", width=4)
        table.add_column("分布", width=18)

        dims = [
            ("💡 创新度", score_data["innovation"], "bright_yellow"),
            ("🎯 实用性", score_data["practicality"], "bright_green"),
            ("🔥 挑战度", score_data["challenge"], "bright_red"),
            ("🎮 趣味性", score_data["fun"], "bright_magenta"),
        ]

        for label, val, color in dims:
            bar = _score_bar(val)
            table.add_row(label, f"[bold]{val}[/bold]", f"[{color}]{bar}[/{color}]")

        # 总分
        grade = score_data["grade"]
        grade_colors = {"S": "bright_yellow", "A": "bright_green", "B": "cyan", "C": "yellow", "D": "red", "E": "dim red"}
        grade_color = grade_colors.get(grade, "white")
        total_bar = _score_bar(score_data["total"])
        table.add_row("⭐ 综合", f"[bold bright_white]{score_data['total']}[/bold bright_white]",
                       f"[bright_blue]{total_bar}[/bright_blue]")
        table.add_row("🏆 评级", f"[bold {grade_color}]{grade}[/bold {grade_color}]", "")

        return Panel(table, title="📊 项目评分", border_style="bright_cyan", expand=False, padding=(0, 1))
    else:
        lines = []
        lines.append("  ┌─────────────────────────────────────┐")
        lines.append("  │          📊 项目评分                 │")
        lines.append("  ├─────────────────────────────────────┤")
        dims = [
            ("💡 创新度", score_data["innovation"]),
            ("🎯 实用性", score_data["practicality"]),
            ("🔥 挑战度", score_data["challenge"]),
            ("🎮 趣味性", score_data["fun"]),
        ]
        for label, val in dims:
            bar = _score_bar(val, 12)
            lines.append(f"  │  {label}  {bar} {val:>3}  │")
        lines.append("  ├─────────────────────────────────────┤")
        lines.append(f"  │  ⭐ 综合   {_score_bar(score_data['total'], 12)} {score_data['total']:>3}  │")
        lines.append(f"  │  🏆 评级   {score_data['grade']:<28}│")
        lines.append("  └─────────────────────────────────────┘")
        return "\n".join(lines)


# ═══════════════════════════════════════════
# 项目骨架模板
# ═══════════════════════════════════════════

SCAFFOLD_TEMPLATES = {
    "Python": {
        "files": {
            "README.md": """# {project_name}

> {tagline}

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

**Tech Stack**: {tech_name} | **Type**: {project_type} | **Domain**: {theme_name} | **Difficulty**: {difficulty_name}

## 📋 目录

- [功能](#-功能)
- [快速开始](#-快速开始)
- [项目结构](#-项目结构)
- [开发](#-开发)
- [贡献](#-贡献)
- [许可证](#-许可证)

## 🎯 功能

{features_list}

## 🚀 快速开始

### 前置要求

- Python 3.10+
- pip

### 安装

```bash
# 克隆项目
git clone https://github.com/yourusername/{project_slug}.git
cd {project_slug}

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate

# 安装依赖
pip install -r requirements.txt
```

### 运行

```bash
python main.py
```

### 运行测试

```bash
pytest
```

## 📁 项目结构

```
{project_slug}/
├── src/              # 源代码
├── tests/            # 测试文件
├── docs/             # 文档
├── main.py           # 入口文件
├── config.py         # 配置文件
├── requirements.txt  # 依赖清单
└── README.md         # 本文件
```

## 🔧 开发

```bash
# 安装开发依赖
pip install -r requirements.txt
pip install pytest flake8 black

# 代码格式化
black .

# 代码检查
flake8 .

# 运行测试
pytest -v
```

## 🤝 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何参与项目开发。

## 📄 许可证

本项目基于 MIT 许可证开源 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

*Generated with 🎲 Random Project Generator*
""",
            "requirements.txt": "# 项目依赖\n",
            "CONTRIBUTING.md": """# 贡献指南

感谢你对 {project_name} 的关注！🎉

## 如何贡献

### 报告 Bug

1. 确保 Bug 尚未在 [Issues](../../issues) 中报告
2. 创建一个新 Issue，包含：
   - 清晰的标题和描述
   - 复现步骤
   - 期望行为 vs 实际行为
   - 环境信息

### 提交功能建议

1. 在 [Issues](../../issues) 中创建功能请求
2. 描述你想要的功能和使用场景
3. 等待讨论和反馈

### 提交代码

1. Fork 本仓库
2. 创建功能分支: `git checkout -b feature/amazing-feature`
3. 提交更改: `git commit -m 'feat: add amazing feature'`
4. 推送分支: `git push origin feature/amazing-feature`
5. 创建 Pull Request

### 代码规范

- 保持代码简洁可读
- 添加必要的注释
- 编写测试覆盖新功能
- 确保所有测试通过

### Commit 消息格式

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```
feat: 添加新功能
fix: 修复 Bug
docs: 更新文档
style: 代码格式调整
refactor: 代码重构
test: 添加测试
chore: 构建/工具变更
```

## 问题反馈

如有任何问题，欢迎在 [Issues](../../issues) 中提出。

---

感谢你的贡献！🚀
""",
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

> {tagline}

[![Node.js](https://img.shields.io/badge/Node.js-18%2B-green?logo=node.js&logoColor=white)](https://nodejs.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

**Tech Stack**: {tech_name} | **Type**: {project_type} | **Domain**: {theme_name} | **Difficulty**: {difficulty_name}

## 📋 目录

- [功能](#-功能)
- [快速开始](#-快速开始)
- [项目结构](#-项目结构)
- [开发](#-开发)
- [贡献](#-贡献)
- [许可证](#-许可证)

## 🎯 功能

{features_list}

## 🚀 快速开始

### 前置要求

- Node.js 18+
- npm 或 yarn

### 安装

```bash
# 克隆项目
git clone https://github.com/yourusername/{project_slug}.git
cd {project_slug}

# 安装依赖
npm install
```

### 运行

```bash
# 开发模式
npm run dev

# 生产模式
npm start
```

### 运行测试

```bash
npm test
```

## 📁 项目结构

```
{project_slug}/
├── src/              # 源代码
├── tests/            # 测试文件
├── docs/             # 文档
├── index.js          # 入口文件
├── package.json      # 项目配置
└── README.md         # 本文件
```

## 🔧 开发

```bash
# 安装开发依赖
npm install

# 代码检查
npm run lint

# 运行测试（带覆盖率）
npm test -- --coverage

# 构建
npm run build
```

## 🤝 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何参与项目开发。

## 📄 许可证

本项目基于 MIT 许可证开源 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

*Generated with 🎲 Random Project Generator*
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
            "CONTRIBUTING.md": """# 贡献指南

感谢你对 {project_name} 的关注！🎉

## 如何贡献

### 报告 Bug

1. 确保 Bug 尚未在 [Issues](../../issues) 中报告
2. 创建一个新 Issue，包含：
   - 清晰的标题和描述
   - 复现步骤
   - 期望行为 vs 实际行为
   - 环境信息

### 提交功能建议

1. 在 [Issues](../../issues) 中创建功能请求
2. 描述你想要的功能和使用场景
3. 等待讨论和反馈

### 提交代码

1. Fork 本仓库
2. 创建功能分支: `git checkout -b feature/amazing-feature`
3. 提交更改: `git commit -m 'feat: add amazing feature'`
4. 推送分支: `git push origin feature/amazing-feature`
5. 创建 Pull Request

### 代码规范

- 保持代码简洁可读
- 添加必要的注释
- 编写测试覆盖新功能
- 确保所有测试通过

### Commit 消息格式

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```
feat: 添加新功能
fix: 修复 Bug
docs: 更新文档
style: 代码格式调整
refactor: 代码重构
test: 添加测试
chore: 构建/工具变更
```

## 问题反馈

如有任何问题，欢迎在 [Issues](../../issues) 中提出。

---

感谢你的贡献！🚀
""",
        },
        "dirs": ["src", "tests", "docs"],
    },
    "default": {
        "files": {
            "README.md": """# {project_name}

> {tagline}

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

**Tech Stack**: {tech_name} | **Type**: {project_type} | **Domain**: {theme_name} | **Difficulty**: {difficulty_name}

## 📋 目录

- [功能](#-功能)
- [快速开始](#-快速开始)
- [项目结构](#-项目结构)
- [贡献](#-贡献)
- [许可证](#-许可证)

## 🎯 功能

{features_list}

## 🚀 快速开始

### 前置要求

- 根据技术栈安装相应运行环境

### 安装

```bash
# 克隆项目
git clone https://github.com/yourusername/{project_slug}.git
cd {project_slug}

# 安装依赖（根据技术栈选择）
# Python: pip install -r requirements.txt
# Node.js: npm install
# Rust: cargo build
# Go: go mod download
```

### 运行

```bash
# 根据技术栈运行项目
# 参考 docs/ 目录下的详细文档
```

## 📁 项目结构

```
{project_slug}/
├── src/              # 源代码
├── tests/            # 测试文件
├── docs/             # 文档
└── README.md         # 本文件
```

## 🤝 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何参与项目开发。

## 📄 许可证

本项目基于 MIT 许可证开源 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

*Generated with 🎲 Random Project Generator*
""",
            "CONTRIBUTING.md": """# 贡献指南

感谢你对 {project_name} 的关注！🎉

## 如何贡献

### 报告 Bug

1. 确保 Bug 尚未在 [Issues](../../issues) 中报告
2. 创建一个新 Issue，包含：
   - 清晰的标题和描述
   - 复现步骤
   - 期望行为 vs 实际行为
   - 环境信息

### 提交功能建议

1. 在 [Issues](../../issues) 中创建功能请求
2. 描述你想要的功能和使用场景
3. 等待讨论和反馈

### 提交代码

1. Fork 本仓库
2. 创建功能分支: `git checkout -b feature/amazing-feature`
3. 提交更改: `git commit -m 'feat: add amazing feature'`
4. 推送分支: `git push origin feature/amazing-feature`
5. 创建 Pull Request

### 代码规范

- 保持代码简洁可读
- 添加必要的注释
- 编写测试覆盖新功能
- 确保所有测试通过

### Commit 消息格式

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```
feat: 添加新功能
fix: 修复 Bug
docs: 更新文档
style: 代码格式调整
refactor: 代码重构
test: 添加测试
chore: 构建/工具变更
```

## 问题反馈

如有任何问题，欢迎在 [Issues](../../issues) 中提出。

---

感谢你的贡献！🚀
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
        if RICH_AVAILABLE:
            console.print(f"  [bold yellow]⚠️  AI 生成失败:[/bold yellow] [dim]{e}[/dim]")
        else:
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
    """格式化基础创意（支持 Rich 美化）"""
    t = idea["tech"]
    p = idea["project"]
    th = idea["theme"]
    d = idea["difficulty"]
    w = idea["twist"]
    stars = "⭐" * d["stars"]
    prefix = f"#{index}  " if index else ""
    
    name_ideas = [
        f"{t['name']}{th['name']}{p['name'].replace(' ', '')}",
        f"{th['name']}Hub",
        f"{p['name'].replace(' ', '')}X",
        f"Vibe{th['name']}",
    ]
    suggested_name = random.choice(name_ideas)
    
    if RICH_AVAILABLE:
        table = Table(show_header=False, box=box.ROUNDED, padding=(0, 1), 
                      border_style="bright_blue", expand=False)
        table.add_column("key", style="bold cyan", no_wrap=True)
        table.add_column("value", style="white")
        
        idx_str = f"[bold magenta]{prefix}[/bold magenta]" if prefix else ""
        table.add_row(f"{t['emoji']} 技术栈", f"[bold green]{t['name']}[/bold green]")
        table.add_row(f"{p['emoji']} 项目类型", f"[bold yellow]{p['name']}[/bold yellow] — {p['desc']}")
        table.add_row(f"{th['emoji']} 领域", f"[bold magenta]{th['name']}[/bold magenta] — {th['desc']}")
        table.add_row(f"{d['emoji']} 难度", f"[bold red]{d['name']}[/bold red] {stars} (预计 {d['hours']})")
        table.add_row("✨ Twist", f"[italic bright_white]{w}[/italic bright_white]")
        table.add_row("📦 建议名", f"[bold bright_cyan]{suggested_name}[/bold bright_cyan]")
        
        title = f"🎲 创意卡片 {idx_str}" if prefix else "🎲 创意卡片"
        panel = Panel(table, title=title, border_style="bright_blue", expand=False)
        console.print()
        console.print(panel)
        return ""  # Rich already printed
    else:
        lines = [
            f"  {prefix}{'─' * 40}",
            f"  {t['emoji']} 技术栈: {t['name']}",
            f"  {p['emoji']} 项目类型: {p['name']} — {p['desc']}",
            f"  {th['emoji']} 领域: {th['name']} — {th['desc']}",
            f"  {d['emoji']} 难度: {d['name']} {stars} (预计 {d['hours']})",
            f"  ✨ Twist: {w}",
            f"  {'─' * 40}",
            f"  📦 建议项目名: {suggested_name}",
        ]
        return "\n".join(lines)

def format_ai_idea(idea, ai_desc, index=None):
    """格式化带 AI 描述的创意（支持 Rich 美化）"""
    t = idea["tech"]
    p = idea["project"]
    th = idea["theme"]
    d = idea["difficulty"]
    w = idea["twist"]
    stars = "⭐" * d["stars"]
    prefix = f"#{index}  " if index else ""
    
    if RICH_AVAILABLE:
        # 用 Rich 构建精美面板
        title_line = f"📦 {ai_desc['project_name']}"
        if prefix:
            title_line = f"{prefix}{title_line}"
        
        info_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 1), expand=True)
        info_table.add_column("key", style="bold cyan", no_wrap=True)
        info_table.add_column("value", style="white")
        info_table.add_row(f"{t['emoji']} 技术栈", f"[bold green]{t['name']}[/bold green]")
        info_table.add_row(f"{p['emoji']} 项目类型", f"[bold yellow]{p['name']}[/bold yellow]")
        info_table.add_row(f"{th['emoji']} 领域", f"[bold magenta]{th['name']}[/bold magenta]")
        info_table.add_row(f"{d['emoji']} 难度", f"[bold red]{d['name']}[/bold red] {stars} (预计 {d['hours']})")
        info_table.add_row("✨ Twist", f"[italic]{w}[/italic]")
        
        # 核心功能
        features_text = ""
        for feat in ai_desc['features']:
            features_text += f"  • {feat}\n"
        
        highlights_text = ""
        for hl in ai_desc['tech_highlights']:
            highlights_text += f"  • {hl}\n"
        
        content_parts = [
            f"[bold]💬 {ai_desc['tagline']}[/bold]\n",
            info_table,
            f"\n[bold bright_white]📝 项目描述:[/bold bright_white]\n  {ai_desc['description']}",
            f"\n[bold bright_yellow]🎯 核心功能:[/bold bright_yellow]\n{features_text}",
            f"[bold bright_green]🔧 技术亮点:[/bold bright_green]\n{highlights_text}",
            f"[bold bright_cyan]🚀 快速开始:[/bold bright_cyan]\n  {ai_desc['getting_started']}",
        ]
        
        from rich.console import Group
        renderable = Group(*content_parts)
        panel = Panel(renderable, title=title_line, title_align="left",
                      border_style="bright_magenta", expand=False, padding=(1, 2))
        console.print()
        console.print(panel)
        return ""  # Rich already printed
    else:
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
    
    if RICH_AVAILABLE:
        console.print(f"\n  [bold bright_green]💾 已保存到 {filename}[/bold bright_green]")
    else:
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
    
    if RICH_AVAILABLE:
        console.print(f"\n  [bold bright_green]💾 已导出 JSON:[/bold bright_green] [cyan]{filename}[/cyan] [dim]({len(data)} 条)[/dim]")
    else:
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
    
    if RICH_AVAILABLE:
        console.print(f"\n  [bold bright_green]💾 已导出 CSV:[/bold bright_green] [cyan]{filename}[/cyan] [dim]({len(ideas)} 条)[/dim]")
    else:
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
    
    if RICH_AVAILABLE:
        console.print(f"\n  [bold bright_green]💾 已导出 Markdown:[/bold bright_green] [cyan]{filename}[/cyan] [dim]({len(ideas)} 条)[/dim]")
    else:
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
        if RICH_AVAILABLE:
            console.print(f"  [bold yellow]⚠️  目录已存在:[/bold yellow] [cyan]{project_dir}[/cyan]")
        else:
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
    tech_name = t["name"]
    theme_name = idea["theme"]["name"]
    project_type = idea["project"]["name"]
    difficulty_name = idea["difficulty"]["name"]
    
    for filename, content in template["files"].items():
        filepath = f"{project_dir}/{filename}"
        formatted_content = content.format(
            project_name=project_name,
            project_slug=project_slug,
            tagline=tagline,
            features_list=features_list,
            tech_name=tech_name,
            theme_name=theme_name,
            project_type=project_type,
            difficulty_name=difficulty_name,
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
    parser.add_argument("--score", action="store_true", help="显示项目评分 (创新/实用/挑战/趣味)")
    parser.add_argument("--deps", action="store_true", help="显示推荐依赖库 (根据技术栈+主题智能推荐)")
    # 配置管理
    parser.add_argument("--config-show", action="store_true", help="显示当前配置")
    parser.add_argument("--config-set", nargs=2, metavar=("KEY", "VALUE"),
                       help="设置配置项 (如: --config-set count 3)")
    parser.add_argument("--config-reset", action="store_true", help="重置为默认配置")
    parser.add_argument("--deploy", action="store_true", help="显示部署指南 (Docker/云平台)")
    parser.add_argument("--cicd", action="store_true", help="生成 CI/CD 配置 (GitHub Actions)")
    parser.add_argument("--no-animation", action="store_true", help="禁用加载动画效果")
    args = parser.parse_args()

    # ── 配置管理命令（优先处理，不生成创意）──
    if args.config_show:
        print_config()
        return
    if args.config_set:
        key, value = args.config_set
        ok, msg = set_config_value(key, value)
        if RICH_AVAILABLE:
            console.print(f"  [bold {'green' if ok else 'red'}]{msg}[/bold {'green' if ok else 'red'}]")
        else:
            print(f"  {msg}")
        return
    if args.config_reset:
        reset_config()
        if RICH_AVAILABLE:
            console.print("  [bold green]✅ 配置已重置为默认值[/bold green]")
        else:
            print("  ✅ 配置已重置为默认值")
        return

    # 应用配置文件默认值到未指定的参数
    args = apply_config_defaults(args)

    if args.history:
        print_history()
        return
    if args.stats:
        print_stats()
        return
    
    if RICH_AVAILABLE:
        # Rich 美化头部
        title_text = Text("🎲 Random Project Generator v3.3", style="bold bright_white")
        subtitle = Text("帮你找到下一个 vibecoding 项目!", style="bright_cyan")
        header_parts = [title_text, "\n", subtitle]
        if args.ai:
            header_parts.append("\n")
            header_parts.append(Text("✨ AI 增强模式已启用", style="bright_yellow"))
        if args.tech:
            header_parts.append("\n")
            header_parts.append(Text(f"🎯 技术栈过滤: {args.tech}", style="bright_green"))
        if args.scaffold:
            header_parts.append("\n")
            header_parts.append(Text("🏗️  骨架生成模式已启用", style="bright_magenta"))
        if args.score:
            header_parts.append("\n")
            header_parts.append(Text("📊 项目评分模式已启用", style="bright_cyan"))
        if args.deps:
            header_parts.append("\n")
            header_parts.append(Text("🔧 依赖推荐模式已启用", style="bright_green"))
        if args.deploy:
            header_parts.append("\n")
            header_parts.append(Text("🚀 部署指南模式已启用", style="bright_blue"))
        if args.cicd:
            header_parts.append("\n")
            header_parts.append(Text("⚙️  CI/CD 配置模式已启用", style="bright_green"))
        
        from rich.console import Group
        header_group = Group(*header_parts)
        console.print()
        console.print(Panel(header_group, border_style="bright_blue", expand=False, padding=(1, 3)))
        console.print()
    else:
        print()
        print("  ╔══════════════════════════════════════╗")
        print("  ║   🎲 Random Project Generator v3.3   ║")
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
            if RICH_AVAILABLE:
                console.print("  [dim]🤖 正在生成 AI 描述...[/dim]")
            else:
                print("  🤖 正在生成 AI 描述...")
            ai_desc = animated_operation("ai", get_ai_description, idea)
            ai_descriptions.append(ai_desc)
            result = format_ai_idea(idea, ai_desc) if ai_desc else format_idea(idea)
            if result:
                print(result)
            idea_score = score_idea(idea) if args.score else None
            if idea_score:
                score_output = format_score(idea_score)
                if RICH_AVAILABLE:
                    console.print(score_output)
                else:
                    print(score_output)
            if args.deps:
                dep_output = format_dep_recommendations(idea)
                if dep_output:
                    if RICH_AVAILABLE:
                        console.print(dep_output)
                    else:
                        print(dep_output)
            if args.deploy:
                deploy_output = format_deploy_guide(idea, ai_desc if args.ai else None)
                if RICH_AVAILABLE:
                    console.print(deploy_output)
                else:
                    print(deploy_output)
            if args.cicd:
                cicd_output = format_cicd_config(idea, ai_desc if args.ai else None)
                if RICH_AVAILABLE:
                    console.print(cicd_output)
                else:
                    print(cicd_output)
            save_to_history(idea, ai_desc, idea_score)
        else:
            result = format_idea(idea)
            if result:
                print(result)
            idea_score = score_idea(idea) if args.score else None
            if idea_score:
                score_output = format_score(idea_score)
                if RICH_AVAILABLE:
                    console.print(score_output)
                else:
                    print(score_output)
            if args.deps:
                dep_output = format_dep_recommendations(idea)
                if dep_output:
                    if RICH_AVAILABLE:
                        console.print(dep_output)
                    else:
                        print(dep_output)
            if args.deploy:
                deploy_output = format_deploy_guide(idea)
                if RICH_AVAILABLE:
                    console.print(deploy_output)
                else:
                    print(deploy_output)
            if args.cicd:
                cicd_output = format_cicd_config(idea)
                if RICH_AVAILABLE:
                    console.print(cicd_output)
                else:
                    print(cicd_output)
            save_to_history(idea, score=idea_score)
    else:
        for i in range(args.count):
            show_brief_animation("default", duration=0.4)
            idea = generate_idea(hard_mode=args.hard, tech_filter=args.tech)
            ideas.append(idea)
            
            if args.ai:
                if RICH_AVAILABLE:
                    console.print(f"  [dim]🤖 正在为第 {i+1} 个项目生成 AI 描述...[/dim]")
                else:
                    print(f"  🤖 正在为第 {i+1} 个项目生成 AI 描述...")
                ai_desc = animated_operation("ai", get_ai_description, idea)
                ai_descriptions.append(ai_desc)
                if ai_desc:
                    result = format_ai_idea(idea, ai_desc, index=i+1 if args.count > 1 else None)
                else:
                    result = format_idea(idea, index=i+1 if args.count > 1 else None)
                if result:
                    print(result)
                idea_score = score_idea(idea) if args.score else None
                if idea_score:
                    score_output = format_score(idea_score)
                    if RICH_AVAILABLE:
                        console.print(score_output)
                    else:
                        print(score_output)
                if args.deps:
                    dep_output = format_dep_recommendations(idea)
                    if dep_output:
                        if RICH_AVAILABLE:
                            console.print(dep_output)
                        else:
                            print(dep_output)
                if args.deploy:
                    deploy_output = format_deploy_guide(idea, ai_desc)
                    if RICH_AVAILABLE:
                        console.print(deploy_output)
                    else:
                        print(deploy_output)
                if args.cicd:
                    cicd_output = format_cicd_config(idea, ai_desc)
                    if RICH_AVAILABLE:
                        console.print(cicd_output)
                    else:
                        print(cicd_output)
                save_to_history(idea, ai_desc, idea_score)
            else:
                result = format_idea(idea, index=i+1 if args.count > 1 else None)
                if result:
                    print(result)
                idea_score = score_idea(idea) if args.score else None
                if idea_score:
                    score_output = format_score(idea_score)
                    if RICH_AVAILABLE:
                        console.print(score_output)
                    else:
                        print(score_output)
                if args.deps:
                    dep_output = format_dep_recommendations(idea)
                    if dep_output:
                        if RICH_AVAILABLE:
                            console.print(dep_output)
                        else:
                            print(dep_output)
                if args.deploy:
                    deploy_output = format_deploy_guide(idea)
                    if RICH_AVAILABLE:
                        console.print(deploy_output)
                    else:
                        print(deploy_output)
                if args.cicd:
                    cicd_output = format_cicd_config(idea)
                    if RICH_AVAILABLE:
                        console.print(cicd_output)
                    else:
                        print(cicd_output)
                save_to_history(idea, score=idea_score)
            
            print()
    
    # 生成骨架
    if args.scaffold:
        if RICH_AVAILABLE:
            console.print("  [bold bright_magenta]🏗️  正在生成项目骨架...[/bold bright_magenta]")
        else:
            print("  🏗️  正在生成项目骨架...")
        for i, idea in enumerate(ideas):
            ai_desc = ai_descriptions[i] if i < len(ai_descriptions) and ai_descriptions[i] else None
            project_dir = animated_operation("scaffold", generate_scaffold, idea, ai_desc)
            if RICH_AVAILABLE:
                console.print(f"  [bold bright_green]✅ 项目骨架已生成:[/bold bright_green] [cyan]{project_dir}[/cyan]")
            else:
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
            if RICH_AVAILABLE:
                console.print(f"\n  [bold red]⚠️  不支持的导出格式:[/bold red] [yellow]{fmt}[/yellow] [dim](支持: json, csv, md)[/dim]")
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
    msg = random.choice(encouragements)
    if RICH_AVAILABLE:
        console.print(f"  [bold bright_white]{msg}[/bold bright_white]")
    else:
        print(f"  {msg}")
    print()

if __name__ == "__main__":
    main()
