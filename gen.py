#!/usr/bin/env python3
"""
🎲 Random Project Generator v3.1
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
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None
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
    parser.add_argument("--score", action="store_true", help="显示项目评分 (创新/实用/挑战/趣味)")
    parser.add_argument("--deps", action="store_true", help="显示推荐依赖库 (根据技术栈+主题智能推荐)")
    args = parser.parse_args()

    if args.history:
        print_history()
        return
    if args.stats:
        print_stats()
        return
    
    if RICH_AVAILABLE:
        # Rich 美化头部
        title_text = Text("🎲 Random Project Generator v3.1", style="bold bright_white")
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
        
        from rich.console import Group
        header_group = Group(*header_parts)
        console.print()
        console.print(Panel(header_group, border_style="bright_blue", expand=False, padding=(1, 3)))
        console.print()
    else:
        print()
        print("  ╔══════════════════════════════════════╗")
        print("  ║   🎲 Random Project Generator v3.1   ║")
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
                print(f"  🤖 正在生成 AI 描述...")
            ai_desc = get_ai_description(idea)
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
            save_to_history(idea, score=idea_score)
    else:
        for i in range(args.count):
            idea = generate_idea(hard_mode=args.hard, tech_filter=args.tech)
            ideas.append(idea)
            
            if args.ai:
                if RICH_AVAILABLE:
                    console.print(f"  [dim]🤖 正在为第 {i+1} 个项目生成 AI 描述...[/dim]")
                else:
                    print(f"  🤖 正在为第 {i+1} 个项目生成 AI 描述...")
                ai_desc = get_ai_description(idea)
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
            project_dir = generate_scaffold(idea, ai_desc)
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
