import sys
import os
import re
import atexit
import tempfile

# ==========================================
# 1. 影子模块代理 (Shadow Module Proxy)
# ==========================================
if 'tqdm' in sys.modules:
    del sys.modules['tqdm']

cwd = os.path.abspath(os.getcwd())
original_sys_path = sys.path[:]
sys.path = [p for p in sys.path if os.path.abspath(p) != cwd]
import tqdm as _real_tqdm
sys.path = original_sys_path

for _attr in dir(_real_tqdm):
    if not _attr.startswith('_'):
        globals()[_attr] = getattr(_real_tqdm, _attr)

# ==========================================
# 2. 工业级深度去重引擎 (终极完全体)
# ==========================================
_target_file = "ADBLOCK_RULE_COLLECTION.txt"
_readme_file = "README.md"

def _is_covered_by_parent(domain, block_set):
    """检查域名是否被其父域名覆盖"""
    parts = domain.split('.')
    # 从一级父域开始检查，例如 sub.example.com -> example.com -> com
    for i in range(1, len(parts)):
        parent = '.'.join(parts[i:])
        if parent in block_set:
            return True
    return False

def _ultimate_dedup_engine():
    # 只在 dns_cleaner.py 执行完毕后触发
    current_script = os.path.basename(sys.argv[0])
    if current_script != "dns_cleaner.py":
        return

    print("\n🚀 [Auto-Hook] 拦截到进程退出，启动工业级深度去重与原子同步...")
    if not os.path.exists(_target_file):
        return

    try:
        with open(_target_file, "r", encoding="utf-8") as f:
            raw_lines = f.readlines()

        comments = []
        rules_set = set()
        
        for line in raw_lines:
            stripped = line.strip()
            if not stripped or stripped.startswith('!') or stripped.startswith('['):
                comments.append(line)
            else:
                rules_set.add(stripped)
                
        original_count = len(rules_set)
        
        # ================= 核心算法阶段 =================
        
        # 阶段 A：提取所有无修饰符的纯拦截域名，用于层级剪枝
        pure_block_domains = set()
        for r in rules_set:
            if r.startswith('||') and r.endswith('^') and '$' not in r and not r.startswith('@@'):
                pure_block_domains.add(r[2:-1])
                
        # 阶段 B：执行域名层级剪枝 (Subdomain Pruning)
        pruned_rules = set()
        pruned_count = 0
        for r in rules_set:
            if r.startswith('||') and r.endswith('^') and '$' not in r and not r.startswith('@@'):
                domain = r[2:-1]
                if _is_covered_by_parent(domain, pure_block_domains):
                    pruned_count += 1
                    continue # 被父域覆盖，安全剔除
            pruned_rules.add(r)
            
        # 阶段 C：修饰符智能合并 (带安全白名单)
        pattern_base = re.compile(r'^(@@)?\|\|([a-zA-Z0-9\.\-]+\.[a-zA-Z]{2,})\^$')
        pattern_mod = re.compile(r'^(@@)?\|\|([a-zA-Z0-9\.\-]+\.[a-zA-Z]{2,})\^\$([a-zA-Z0-9_,]+)$')
        
        base_rules_map = {}
        standalone_set = set()
        merged_count = 0
        
        # 不安全关键字：遇到这些修饰符绝对不合并
        unsafe_keywords = ['~', '=', 'redirect', 'csp', 'important', 'rewrite', 'badfilter', 'removeparam', 'popup']
        
        for rule in pruned_rules:
            m = pattern_mod.match(rule)
            if m:
                prefix, domain, mods = m.group(1) or '', m.group(2), m.group(3)
                
                # 安全检查：如果包含任何不安全关键字，放弃合并
                if any(keyword in mods for keyword in unsafe_keywords):
                    standalone_set.add(rule)
                    continue
                    
                base = f"{prefix}||{domain}^"
                if base not in base_rules_map:
                    base_rules_map[base] = set()
                base_rules_map[base].update(mods.split(','))
                continue
                
            m = pattern_base.match(rule)
            if m:
                prefix, domain = m.group(1) or '', m.group(2)
                base = f"{prefix}||{domain}^"
                if base not in base_rules_map:
                    base_rules_map[base] = set()
                base_rules_map[base].add(None)
                continue
                
            standalone_set.add(rule)
            
        # 阶段 D：重建规则库
        final_rules = set(standalone_set)
        for base, mods in base_rules_map.items():
            if None in mods:
                final_rules.add(base)
            else:
                if len(mods) > 1:
                    merged_count += (len(mods) - 1) # 统计合并掉的行数
                sorted_mods = ",".join(sorted(list(mods)))
                final_rules.add(f"{base}${sorted_mods}")
                
        # 阶段 E：强制排序
        sorted_final = sorted(list(final_rules))
        
        # ================= 原子写入阶段 =================
        # 使用临时文件进行原子替换，防止 CI 中断导致文件损坏
        dir_name = os.path.dirname(os.path.abspath(_target_file))
        with tempfile.NamedTemporaryFile('w', encoding='utf-8', delete=False, dir=dir_name) as tmp:
            tmp.writelines(comments)
            for r in sorted_final:
                tmp.write(r + "\n")
            tmp_path = tmp.name
            
        os.replace(tmp_path, _target_file)
        
        final_count = len(sorted_final)
        print(f"📊 [审计报告] 原始规则: {original_count} | 层级剪枝: -{pruned_count} | 修饰符合并: -{merged_count} | 最终保留: {final_count}")
        
        # ================= README 强制兜底同步 =================
        if os.path.exists(_readme_file):
            try:
                with open(_readme_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                pattern = r'(\| 📏 规则总数 \| )([\d,]+)( 条 \|)'
                def replacer(match):
                    return f"{match.group(1)}{final_count:,}{match.group(3)}"
                    
                new_content = re.sub(pattern, replacer, content)
                if new_content != content:
                    with open(_readme_file, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"📝 [Auto-Hook] 已强制校准 README.md 规则总数为: {final_count:,}")
            except Exception as e:
                print(f"❌ [Auto-Hook] README 同步失败: {e}")
                
    except Exception as e:
        print(f"❌ [Auto-Hook] 智能去重引擎发生异常 (已跳过): {e}")

atexit.register(_ultimate_dedup_engine)
