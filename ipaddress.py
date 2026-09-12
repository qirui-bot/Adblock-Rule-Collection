import sys
import os

# ==========================================
# 1. 首次运行拦截与自动注入逻辑
# ==========================================
# 只有在 GitHub Actions 运行 Adblock_Rule_Generator.py 时才执行注入
should_patch = not os.environ.get("PATCHED_UPSTREAM") and "Adblock_Rule_Generator.py" in sys.argv[0]

if should_patch:
    custom_file = "custom_sources.txt"
    injected = False
    if os.path.exists(custom_file):
        with open(custom_file, "r", encoding="utf-8") as f:
            # 忽略空行和 # 开头的注释
            extra_urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]
            
        if extra_urls:
            target = "Adblock_Rule_Generator.py"
            if os.path.exists(target):
                with open(target, "r", encoding="utf-8") as f:
                    content = f.read()
                
                import re
                # 使用正则精准定位 UPSTREAM_URLS 列表
                match = re.search(r'(UPSTREAM_URLS\s*=\s*\[.*?)(\s*\])', content, re.DOTALL)
                if match:
                    # 转义反斜杠和引号，防止语法错误
                    safe_urls = [u.replace('\\', '\\\\').replace('"', '\\"') for u in extra_urls]
                    extra_urls_str = ",\n    ".join(f'"{u}"' for u in safe_urls)
                    existing_content = match.group(1)
                    
                    # 确保原列表末尾有逗号
                    if not existing_content.rstrip().endswith(","):
                        existing_content += ","
                    
                    # 拼接新 URL 并替换原文件中的列表
                    new_list_content = existing_content + "\n    " + extra_urls_str
                    new_content = content[:match.start(0)] + new_list_content + match.group(2) + content[match.end(0):]
                    
                    # 将更新后的代码写入 CI 运行时的临时磁盘
                    with open(target, "w", encoding="utf-8") as f:
                        f.write(new_content)
                        
                    print(f"✅ [Auto-Inject] 成功将 {len(extra_urls)} 个自定义上游源注入到 {target}！")
                    injected = True
                        
    if injected:
        # 设置环境变量，防止重启后陷入死循环
        os.environ["PATCHED_UPSTREAM"] = "1"
        sys.stdout.flush()
        # 替换当前 Python 进程，重新启动脚本（此时磁盘上的文件已是最新）
        os.execv(sys.executable, [sys.executable] + sys.argv)


# ==========================================
# 2. 作为官方标准库的完美替身 (Proxy)
# ==========================================
# 从 sys.modules 中移除当前的占位符，防止循环导入
if 'ipaddress' in sys.modules:
    del sys.modules['ipaddress']

# 临时将当前项目目录从 sys.path 中剔除，以确保导入的是 Python 内置的真实 ipaddress 库
cwd = os.path.abspath(os.getcwd())
script_dir = os.path.abspath(os.path.dirname(__file__))
original_sys_path = sys.path[:]
sys.path = [p for p in sys.path if os.path.abspath(p) not in (cwd, script_dir)]

# 导入真实的官方模块
import ipaddress as _real_ipaddress

# 恢复系统路径
sys.path = original_sys_path

# 将真实模块的所有公开属性暴露给当前模块
# 这样原脚本后续调用 ipaddress.ip_address() 时能完美运行
for _attr in dir(_real_ipaddress):
    if not _attr.startswith('_'):
        globals()[_attr] = getattr(_real_ipaddress, _attr)
