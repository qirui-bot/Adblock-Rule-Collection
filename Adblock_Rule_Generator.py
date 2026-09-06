# -*- coding: utf-8 -*-
"""
双栈 Hosts 转 ABP 规则生成器 (Ultimate Clean & User-Friendly Edition)
功能：解析双栈 Hosts，提取域名，转化为 ABP 格式，并进行深度清洗、去重、优化。
特性：自动安装依赖、CI环境自适应、彩色日志、进度条、临时目录备份与清理、
SHA-256校验、数据漏斗统计、兼容高级ABP语法、后缀树深度去重、内置食用指南。
"""
import os
import sys
import re
import time
import shutil
import hashlib
import tempfile
import ipaddress
import subprocess
from datetime import datetime, timezone, timedelta

# =====================================================================
# 0. 环境预检与 CI (GitHub Actions) 自适应
# =====================================================================
if sys.version_info < (3, 8):
    print("❌ 错误: 本脚本需要 Python 3.8 或更高版本。请升级您的 Python 环境。")
    sys.exit(1)

IS_CI = os.getenv("GITHUB_ACTIONS") == "true"
if os.name == 'nt' and not IS_CI:
    os.system('')

class Colors:
    RESET =   "" if IS_CI else "\033[0m"
    BOLD =    "" if IS_CI else "\033[1m"
    RED =     "" if IS_CI else "\033[91m"
    GREEN =   "" if IS_CI else "\033[92m"
    YELLOW =  "" if IS_CI else "\033[93m"
    BLUE =    "" if IS_CI else "\033[94m"
    CYAN =    "" if IS_CI else "\033[96m"
    MAGENTA = "" if IS_CI else "\033[95m"

def log_info(msg): print(f"{Colors.BLUE}ℹ️  {msg}{Colors.RESET}")
def log_success(msg): print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")
def log_warning(msg):
    if IS_CI: print(f"::warning::{msg}")
    else: print(f"{Colors.YELLOW}⚠️  {msg}{Colors.RESET}")
def log_error(msg):
    if IS_CI: print(f"::error::{msg}")
    else: print(f"{Colors.RED}❌ {msg}{Colors.RESET}")

# =====================================================================
# 1. 依赖自动安装 (带权限容错)
# =====================================================================
def install_package(package):
    print(f"📦 正在自动安装缺失依赖: {package}... ")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", package])
    except subprocess.CalledProcessError:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "--user", package])
        except subprocess.CalledProcessError:
            log_error(f"无法安装 {package}，请手动执行: pip install {package}")
            sys.exit(1)

try: import requests
except ImportError: install_package("requests"); import requests
try: from tqdm import tqdm
except ImportError: install_package("tqdm"); from tqdm import tqdm

# =====================================================================
# 2. 核心配置区 (硬编码，保持仓库绝对整洁)
# =====================================================================
UPSTREAM_URLS = [
    "https://raw.githubusercontent.com/Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist/master/hosts/hosts0",
    "https://raw.githubusercontent.com/Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist/master/hosts/hosts1",
    "https://raw.githubusercontent.com/Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist/master/hosts/hosts2",
    "https://raw.githubusercontent.com/Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist/master/hosts/hosts3",
    "https://raw.githubusercontent.com/Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist/master/hosts/hosts4",
    "https://raw.githubusercontent.com/Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist/master/hosts/hosts5",
    "https://raw.githubusercontent.com/wansheng8/GZ/main/dist/adblock_collection_full.txt",
    "https://raw.githubusercontent.com/fynks/blocklists/main/blocklists/personal.txt",
    "https://raw.githubusercontent.com/elliottophellia/adlist/main/hosts",
    "https://raw.githubusercontent.com/bongochong/CombinedPrivacyBlockLists/master/cpbl-abp-list.txt",
    "https://raw.githubusercontent.com/badmojr/1Hosts/master/Lite/adblock.txt",
    "https://raw.githubusercontent.com/rentianyu/Ad-set-hosts/master/adguard",
    "https://raw.githubusercontent.com/lingeringsound/10007_auto/master/adb.txt",
    "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts",
    "https://raw.githubusercontent.com/vip592850-blip/ros-routing-rules/main/reject_adlist.txt",
    "https://raw.githubusercontent.com/2Gardon/SM-Ad-FuckU-hosts/master/SMAdHosts",
    "https://raw.githubusercontent.com/neodevpro/neodevhost/master/adblocker",
    "https://raw.githubusercontent.com/Sereinfy/Adrules/main/rules/adblockdns.txt",
]

WHITELIST_DOMAINS = {
    "adguard.com", "adguard-dns.io", "adguard.info",
    "fritz.box", "fritz.nas", "fritz.repeater", "router.asus.com", "miwifi.com",
    "change.org", "binance.com", "freshbooks.com", "freepik.com", "garmin.com",
    "leadpages.co", "clickfunnels.com", "wixsite.com", "weebly.com", "ck.page"
}
# =====================================================================
# 3. 正则表达式引擎 (清洗管道)
# =====================================================================
RE_HOSTS_PREFIX = re.compile(r'^(?:0.0.0.0|0.0.0|127.0.0.1|localhost)[.-]?(.*)$', re.IGNORECASE)
RE_FREE_HOSTING_HASH = re.compile(
    r'^[a-z0-9-]{12,}\.(netlify\.app|vercel\.app|web\.app|firebaseapp\.com|pages\.dev|000webhostapp\.com|github\.io|glitch\.me|repl\.co)$'
)
RE_PURE_NUMERIC_OR_IP = re.compile(r'^(\d+\.(com|net|org|xyz|top|club|info|biz)|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})$')
RE_MALFORMED_SUFFIX = re.compile(r'\.(domain\.name|local|lan|corp|internal|home|nas)$')
RE_DOMAIN_VALID = re.compile(r'^(?=.{1,253}$)(?:[A-Za-z0-9-]{1,63}\.)+[A-Za-z0-9-]{2,63}$')

# =====================================================================
# 4. 核心解析函数 (🔥 终极修复：精准剥离修饰符，绝对拦截路径特征)
# =====================================================================
_VALID_HASH_PREFIXES = ("##", "#@#", "#$#", "#$@#", "#?#", "#@?#", "#%#")

def is_comment_line(line: str) -> bool:
    if line.startswith('!') or line.startswith('['): return True
    if line.startswith('#') and not line.startswith(_VALID_HASH_PREFIXES): return True
    return False

def parse_line(line: str):
    """智能解析每一行：精准截断修饰符，保留通配符，坚决丢弃 DNS 无效规则"""
    stripped = line.strip()
    if not stripped or is_comment_line(stripped): return None
    
    # 🔥 策略 A: 识别并保留白名单规则
    if stripped.startswith('@@'): 
        return ('ABP_RULE', stripped)
        
    # 🔥 策略 B: 坚决丢弃正则表达式规则 (DNS 层面无法处理)
    if stripped.startswith('/'): 
        return None
        
    # 🔥 策略 C: 专门处理 || 开头的拦截规则 (核心修复)
    if stripped.startswith('||'):
        # 1. 精准剥离 $ 修饰符，只取域名部分
        base_rule = stripped.split('$')[0]
        
        # 2. 提取 || 和 ^ 之间的内容 (自动补全缺失的 ^)
        if base_rule.endswith('^'):
            domain_part = base_rule[2:-1]
        else:
            domain_part = base_rule[2:]
            
        # 🔥 3. 绝对防线：只要包含 / ? | ，直接判定为网络层/路径规则，坚决丢弃！
        if '/' in domain_part or '?' in domain_part or '|' in domain_part:
            return None
            
        # 4. 剩下的才可能是合法的域名或域名通配符
        if '*' in domain_part:
            return ('ABP_RULE', f"||{domain_part}^")
        elif RE_DOMAIN_VALID.match(domain_part):
            return ('DOMAIN', domain_part)
        else:
            return ('ABP_RULE', f"||{domain_part}^")

    # 🔥 策略 D: 其他高级 ABP 规则 (如 ## 美容规则，DNS 无法处理，坚决丢弃)
    if any(stripped.startswith(p) for p in _VALID_HASH_PREFIXES): 
        return None
        
    # 策略 E: 解析 Hosts 格式 (提取纯域名)
    parts = stripped.split()
    if len(parts) >= 2:
        ip_part, domain_part = parts[0], parts[1]
        try:
            ipaddress.ip_address(ip_part)
            reserved_domains = {
                'localhost', 'localhost.localdomain', 'broadcasthost',
                'ip6-localhost', 'ip6-loopback', 'ip6-localnet',
                'ip6-mcastprefix', 'ip6-allnodes', 'ip6-allrouters'
            }
            if domain_part.lower() in reserved_domains: return None
            return ('DOMAIN', domain_part)
        except ValueError:
            pass
    if len(parts) == 1:
        return ('DOMAIN', parts[0])
        
    return None

# =====================================================================
# 5. 深度清洗与去重管道
# =====================================================================
def clean_and_optimize_domains(raw_domains):
    log_info("🧹 启动深度清洗与优化管道...")
    stats = {'restored': 0, 'phishing': 0, 'whitelisted': 0, 'redundant': 0, 'malformed': 0}
    cleaned_domains = set()
    iterator = tqdm(raw_domains, desc="清洗域名", ncols=80, colour="cyan", disable=IS_CI)
    
    for domain in iterator:
        domain = domain.strip().lower()
        if not domain: continue
        
        match = RE_HOSTS_PREFIX.match(domain)
        if match:
            restored_domain = match.group(1)
            if restored_domain and RE_DOMAIN_VALID.match(restored_domain):
                domain = restored_domain
                stats['restored'] += 1
            else:
                stats['malformed'] += 1
                continue
                
        if not RE_DOMAIN_VALID.match(domain):
            stats['malformed'] += 1
            continue
        if RE_PURE_NUMERIC_OR_IP.match(domain) or RE_MALFORMED_SUFFIX.search(domain):
            stats['malformed'] += 1
            continue
            
        if any(domain == w or domain.endswith('.' + w) for w in WHITELIST_DOMAINS):
            cleaned_domains.add(domain)
            stats['whitelisted'] += 1
            continue
            
        if RE_FREE_HOSTING_HASH.match(domain):
            stats['phishing'] += 1
            continue
        cleaned_domains.add(domain)
        
    log_info("🔍 正在剔除冗余子域名...")
    sorted_domains = sorted(cleaned_domains, key=len)
    final_domains = set()
    for domain in sorted_domains:
        parts = domain.split('.')
        is_redundant = False
        for i in range(1, len(parts)):
            if '.'.join(parts[i:]) in final_domains:
                is_redundant = True
                break
        if not is_redundant:
            final_domains.add(domain)
        else:
            stats['redundant'] += 1
            
    return final_domains, stats

# =====================================================================
# 6. 后缀树 (Suffix Tree) 深度去重引擎
# =====================================================================
def suffix_tree_dedup(rules):
    """使用后缀树（反转 Trie 树）对 ABP 规则进行无损深度去重。"""
    log_info("🌳 启动后缀树 (Suffix Tree) 深度去重管道...")
    pure_domains, advanced_rules = set(), set()
    
    for rule in rules:
        if rule.startswith('||') and rule.endswith('^') and '$' not in rule and '*' not in rule:
            pure_domains.add(rule[2:-1])
        else:
            # 🔥 修改：允许 * 参与匹配，防止通配符规则被错误归类
            match = re.match(r'^\|\|([a-zA-Z0-9*.-]+)\^', rule)
            if match:
                advanced_rules.add((rule, match.group(1)))
            else:
                advanced_rules.add((rule, None))
                
    root = {}
    for domain in pure_domains:
        parts = domain.split('.')[::-1]
        node, is_redundant = root, False
        for part in parts:
            if node.get('is_end'):
                is_redundant = True
                break
            if part not in node:
                node[part] = {}
            node = node[part]
        if not is_redundant:
            node['is_end'] = True
            
    final_pure_domains = set()
    def extract_domains(node, current_parts):
        if node.get('is_end'):
            final_pure_domains.add('.'.join(current_parts[::-1]))
            return
        for part, child in node.items():
            if part != 'is_end':
                extract_domains(child, current_parts + [part])
    extract_domains(root, [])
    
    final_advanced_rules = set()
    for rule, domain in advanced_rules:
        if domain:
            parts, is_covered = domain.split('.'), False
            for i in range(len(parts)):
                if '.'.join(parts[i:]) in final_pure_domains:
                    is_covered = True
                    break
            if not is_covered:
                final_advanced_rules.add(rule)
        else:
            final_advanced_rules.add(rule)
            
    final_rules = set(f"||{d}^" for d in final_pure_domains)
    final_rules.update(final_advanced_rules)
    log_success(f"🌳 后缀树去重完成：剔除 {len(rules) - len(final_rules)} 条冗余规则。")
    return final_rules

# =====================================================================
# 7. 网络请求、备份与临时文件清理
# =====================================================================
def fetch_with_retry(url, retries=3, timeout=15):
    for i in range(retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except Exception as e:
            if i < retries - 1: time.sleep(2)
            else: log_warning(f"抓取失败 {url} -> {e}"); return None

def backup_to_temp_dir(file_path):
    if os.path.exists(file_path):
        temp_dir = tempfile.gettempdir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(temp_dir, f"ADBLOCK_RULE_{timestamp}.bak")
        shutil.copy2(file_path, backup_path)
        log_success(f"旧文件已备份至: {Colors.CYAN}{backup_path}{Colors.RESET}")

def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

# =====================================================================
# 8. 自动更新 README.md 状态 (🔥 终极修复：修复表格语法与文件写入参数)
# =====================================================================
def update_readme(timestamp, num_rules, upstream_urls):
    readme_path = "README.md"
    if not os.path.exists(readme_path): return
    try:
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()
        num_rules_str = f"{num_rules:,}"
        
        # 🔥 核心修复：在 <h3> 标签和表格第一行之间保留空行，且 | 两侧加空格
        status_block = f"""<!-- AUTO_STATUS_START -->
<h3 align="center">📊 仓库状态</h3>

| 项目 | 状态 |
| --- | --- |
| 🕐 最后更新时间 | {timestamp} (UTC+8) |
| 📏 规则总数 | {num_rules_str} 条 |
| 🔄 更新频率 | 每 6 小时自动更新 |
| 📦 文件格式 | ABP 兼容格式 (支持通配符/静默拦截，已剔除正则) |

<!-- AUTO_STATUS_END -->"""
        
        upstream_rows = []
        for i, url in enumerate(upstream_urls, 1):
            parts = url.replace("https://raw.githubusercontent.com/", "").split("/")
            source_name = f"{parts[0]}/{parts[1]}" if len(parts) >= 3 else url
            upstream_rows.append(f"| {i} | `{source_name}` | [链接]({url}) |")
            
        # 🔥 核心修复：在 <summary> 标签和表格第一行之间保留空行
        upstream_block = f"""<!-- AUTO_UPSTREAM_START -->
<details>
<summary>📋 点击展开完整上游源列表（共 {len(upstream_urls)} 个）</summary>

| 序号 | 上游源 | 链接 |
| --- | --- | --- |
{chr(10).join(upstream_rows)}

</details>
<!-- AUTO_UPSTREAM_END -->"""
        
        # 🔥 核心修复：移除正则表达式中多余的空格，确保精准匹配
        content = re.sub(r'<!-- AUTO_STATUS_START -->.*?<!-- AUTO_STATUS_END -->', status_block, content, flags=re.DOTALL)
        content = re.sub(r'<!-- AUTO_UPSTREAM_START -->.*?<!-- AUTO_UPSTREAM_END -->', upstream_block, content, flags=re.DOTALL)
        
        # 🔥 核心修复：移除 "w" 和 "utf-8" 尾部多余的空格
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(content)
        log_success(f"✅ README.md 状态已更新")
    except Exception as e:
        log_error(f"更新 README.md 失败: {e}")

# =====================================================================
# 9. 主流程 (🔥 终极修复：调整严格过滤的判断优先级)
# =====================================================================
def main():
    start_time = time.time()
    print(f"\n{Colors.BOLD}{Colors.CYAN}🚀 双栈 Hosts 转 ABP 规则生成器 (Ultimate Edition){Colors.RESET}\n")
    output_filename = "ADBLOCK_RULE_COLLECTION.txt"
    
    try:
        raw_domains, kept_abp_rules, failed_urls = set(), set(), []
        log_info(f"开始抓取并解析 {len(UPSTREAM_URLS)} 个上游源...")
        
        for url in tqdm(UPSTREAM_URLS, desc="抓取上游源", ncols=80, colour="green", disable=IS_CI):
            content = fetch_with_retry(url)
            if content:
                for line in content.splitlines():
                    result = parse_line(line)
                    if result:
                        if result[0] == 'DOMAIN': raw_domains.add(result[1])
                        elif result[0] == 'ABP_RULE': kept_abp_rules.add(result[1])
            else:
                failed_urls.append(url)
                
        final_domains, clean_stats = clean_and_optimize_domains(raw_domains)
        final_abp_rules = set()
        
        for domain in final_domains:
            is_whitelist = any(domain == w or domain.endswith('.' + w) for w in WHITELIST_DOMAINS)
            final_abp_rules.add(f"@@||{domain}^$important" if is_whitelist else f"||{domain}^")
        final_abp_rules.update(kept_abp_rules)
        
        pre_dedup_count = len(final_abp_rules)
        final_abp_rules = suffix_tree_dedup(final_abp_rules)
        suffix_tree_reduced = pre_dedup_count - len(final_abp_rules)
        
        # ================= 🔥 严格过滤：终极防线 =================
        strict_dns_rules = set()
        for rule in final_abp_rules:
            rule = rule.strip()
            if not rule: continue
                
            if rule.startswith('@@||'):
                match = re.match(r'^@@\|\|([a-zA-Z0-9*.-]+)\^', rule)
                if match and '/' not in match.group(1) and '?' not in match.group(1):
                    strict_dns_rules.add(f"@@||{match.group(1)}^$important")
                continue
                
            if rule.startswith('||') and rule.endswith('^'):
                domain_part = rule[2:-1] 
                
                # 🔥 第一道防线：绝对不允许出现路径、参数、管道符
                if '/' in domain_part or '?' in domain_part or '|' in domain_part:
                    continue

                # 🔥 第二道防线：处理通配符 '*'，并防范顶级域名误杀
                if '*' in domain_part:
                    if re.match(r'^\*\.[a-zA-Z]{2,6}$', domain_part): continue 
                    if re.match(r'^\*\.xn--[a-zA-Z0-9-]+$', domain_part): continue
                    # ✅ 修复：为通配符拦截规则也添加 $dnsrewrite=NOERROR 后缀
                    strict_dns_rules.add(f"{rule}$dnsrewrite=NOERROR")
                # 第三道防线：处理纯域名
                elif RE_DOMAIN_VALID.match(domain_part):
                    strict_dns_rules.add(f"{rule}$dnsrewrite=NOERROR")
                # 第四道防线：处理 IP 地址
                else:
                    try:
                        ipaddress.ip_address(domain_part)
                        strict_dns_rules.add(rule)
                    except ValueError:
                        continue
                continue
                
        num_rules = len(strict_dns_rules)
        backup_to_temp_dir(output_filename)
        tz_utc8 = timezone(timedelta(hours=8))
        timestamp = datetime.now(tz_utc8).strftime("%Y-%m-%d %H:%M:%S")
        
        header = f"""! Title: Adblock-Rule-Collection (Strict DNS Rules)
! Description: 仅包含由 || 和 @@|| 开头且经过严格校验的有效 DNS 拦截规则。已自动剔除所有美容规则、正则及网络层路径规则。
! Homepage: https://github.com/qirui-bot/Adblock-Rule-Collection
! LICENSE1: https://github.com/qirui-bot/Adblock-Rule-Collection/blob/main/LICENSE-GPL%203.0
! LICENSE2: https://github.com/qirui-bot/Adblock-Rule-Collection/blob/main/LICENSE-CC-BY-NC-SA%204.0
! Generated: {timestamp} (UTC+8)
! Total rules: {num_rules}
"""
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(header)
            for rule in sorted(strict_dns_rules):
                f.write(rule + "\n")
                
        file_size_bytes = os.path.getsize(output_filename)
        size_str = f"{file_size_bytes / (1024 * 1024):.2f} MB" if file_size_bytes > 1024 * 1024 else f"{file_size_bytes / 1024:.2f} KB"
        file_hash = calculate_sha256(output_filename)
        elapsed_time = time.time() - start_time
        update_readme(timestamp, num_rules, UPSTREAM_URLS)
        
        print(f"\n{Colors.BOLD}📊 数据漏斗与体检报告:{Colors.RESET}")
        print(f" ├─ 原始提取域名: {len(raw_domains)}")
        print(f" ├─ {Colors.GREEN}最终有效规则: {Colors.BOLD}{num_rules}{Colors.RESET}")
        print(f" ├─ 📦 文件大小: {Colors.CYAN}{size_str}{Colors.RESET}")
        print(f" └─ ⏱️  总耗时: {Colors.YELLOW}{elapsed_time:.2f} 秒{Colors.RESET}\n")
        log_success(f"成功生成文件: {Colors.CYAN}{output_filename}{Colors.RESET}")
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️ 用户中断，安全退出。{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        log_error(f"发生未知错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
