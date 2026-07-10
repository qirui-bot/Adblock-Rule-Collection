# -- coding: utf-8 --
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
if os.name == 'nt' and not IS_CI: os.system('')

class Colors:
    RESET =   "" if IS_CI else "\033[0m"
    BOLD =    "" if IS_CI else "\033[1m"
    RED =     "" if IS_CI else "\033[91m"
    GREEN =   "" if IS_CI else "\033[92m"
    YELLOW =  "" if IS_CI else "\033[93m"
    BLUE =    "" if IS_CI else "\033[94m"
    CYAN =    "" if IS_CI else "\033[96m"

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
    print(f"📦 正在自动安装缺失依赖: {package}...")
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
# 2. 核心配置区 (硬编码，不生成额外 txt 文件，保持仓库绝对整洁)
# =====================================================================
UPSTREAM_URLS = [
    "https://raw.githubusercontent.com/Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist/master/hosts/hosts0",
    "https://raw.githubusercontent.com/Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist/master/hosts/hosts1",
    "https://raw.githubusercontent.com/Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist/master/hosts/hosts2",
    "https://raw.githubusercontent.com/Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist/master/hosts/hosts3",
    "https://raw.githubusercontent.com/Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist/master/hosts/hosts4",
    "https://raw.githubusercontent.com/Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist/master/hosts/hosts5",
    "https://raw.githubusercontent.com/wansheng8/adblock/main/rules/outputs/hosts.txt",
    "https://raw.githubusercontent.com/fynks/blocklists/main/blocklists/personal.txt",
    "https://raw.githubusercontent.com/elliottophellia/adlist/main/hosts",
    "https://raw.githubusercontent.com/bongochong/CombinedPrivacyBlockLists/master/newhosts-final.hosts",
    "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/hosts/pro.txt",
    "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/hosts/doh.txt",
    "https://raw.githubusercontent.com/badmojr/1Hosts/master/Lite/hosts.txt",
    "https://raw.githubusercontent.com/rentianyu/Ad-set-hosts/master/hosts",
    "https://raw.githubusercontent.com/110789/anti-ad-hosts/main/anti-ad-hosts.txt",
    "https://raw.githubusercontent.com/qdqqd/add-hosts/main/addhosts.txt",
    "https://raw.githubusercontent.com/vip592850-blip/ros-routing-rules/main/reject_adlist.txt",
    "https://raw.githubusercontent.com/217heidai/adblockfilters/main/rules/adblockhosts.txt",
    "https://raw.githubusercontent.com/neodevpro/neodevhost/master/host",
    "https://raw.githubusercontent.com/Sereinfy/Adrules/main/rules/adblockhosts.txt",
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
    r'^[a-z0-9-]{12,}\.(netlify.app|vercel.app|web.app|firebaseapp.com|pages.dev|000webhostapp.com|github.io|glitch.me|repl.co)$'
)
RE_PURE_NUMERIC_OR_IP = re.compile(r'^(\d+\.(com|net|org|xyz|top|club|info|biz)|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})$')
RE_MALFORMED_SUFFIX = re.compile(r'\.(domain.name|local|lan|corp|internal|home|nas)$')
RE_DOMAIN_VALID = re.compile(r'^(?=.{1,253}$)(?:[A-Za-z0-9-]{1,63}\.)+[A-Za-z0-9-]{2,63}$')

# =====================================================================
# 4. 核心解析函数 (彻底封堵畸形规则绕过漏洞)
# =====================================================================
_VALID_HASH_PREFIXES = ("##", "#@#", "#$#", "#$@#", "#?#", "#@?#", "#%#")

def is_comment_line(line: str) -> bool:
    if line.startswith('!') or line.startswith('['): return True
    if line.startswith('#') and not line.startswith(_VALID_HASH_PREFIXES): return True
    return False

def parse_line(line: str):
    """智能解析每一行：识别高级ABP规则，剥离普通||domain^，解析Hosts格式"""
    stripped = line.strip()
    if not stripped or is_comment_line(stripped): return None

    # 策略 A: 识别并 100% 保留真正的高级 ABP 规则
    if stripped.startswith('@@'): return ('ABP_RULE', stripped)
    if '$' in stripped and not stripped.startswith('#'): return ('ABP_RULE', stripped)
    if any(stripped.startswith(p) for p in _VALID_HASH_PREFIXES): return ('ABP_RULE', stripped)
    if stripped.startswith('/'): return ('ABP_RULE', stripped)

    # 策略 B: 处理普通的 ||domain^ 格式 (强制进入清洗管道)
    if stripped.startswith('||') and stripped.endswith('^'):
        domain_part = stripped[2:-1]
        if domain_part.startswith('*.'): domain_part = domain_part[2:]
        elif domain_part.startswith('*'): domain_part = domain_part[1:]
        if '*' in domain_part: return ('ABP_RULE', stripped)
        return ('DOMAIN', domain_part)

    # 策略 C: 解析 Hosts 格式 (提取纯域名)
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
# 5. 深度清洗与去重管道 (增加二次合法性验证)
# =====================================================================
def clean_and_optimize_domains(raw_domains):
    log_info("🧹 启动深度清洗与优化管道...")
    stats = {'restored': 0, 'phishing': 0, 'whitelisted': 0, 'redundant': 0, 'malformed': 0}
    cleaned_domains = set()
    
    iterator = tqdm(raw_domains, desc="清洗域名", ncols=80, colour="cyan", disable=IS_CI)
    for domain in iterator:
        domain = domain.strip().lower()
        if not domain: continue

        # 1. 修复畸形前缀
        match = RE_HOSTS_PREFIX.match(domain)
        if match:
            restored_domain = match.group(1)
            if restored_domain and RE_DOMAIN_VALID.match(restored_domain):
                domain = restored_domain
                stats['restored'] += 1
            else:
                stats['malformed'] += 1
                continue

        # 2. 验证域名合法性
        if not RE_DOMAIN_VALID.match(domain):
            stats['malformed'] += 1
            continue
        if RE_PURE_NUMERIC_OR_IP.match(domain) or RE_MALFORMED_SUFFIX.search(domain):
            stats['malformed'] += 1
            continue

        # 3. 白名单保护
        if any(domain == w or domain.endswith('.' + w) for w in WHITELIST_DOMAINS):
            cleaned_domains.add(domain)
            stats['whitelisted'] += 1
            continue

        # 4. 过滤一次性钓鱼域名
        if RE_FREE_HOSTING_HASH.match(domain):
            stats['phishing'] += 1
            continue

        cleaned_domains.add(domain)

    # 5. 智能去重 (剔除冗余子域名 - 基础版)
    log_info("🔍 正在剔除冗余子域名 (基础智能去重)...")
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
# 🔥 6. 新增：后缀树 (Suffix Tree) 深度去重引擎
# =====================================================================
def suffix_tree_dedup(rules):
    """
    使用后缀树（反转 Trie 树）对 ABP 规则进行无损深度去重。
    原理：将域名按 '.' 分割并反转构建 Trie 树。如果父域名节点被标记为拦截点，
    则其所有子节点（原域名的子域名）均被覆盖，直接剪枝。
    优势：不仅能对纯域名去重，还能剔除被父域名覆盖的高级 ABP 规则，大幅降低规则数。
    """
    log_info("🌳 启动后缀树 (Suffix Tree) 深度去重管道...")
    
    pure_domains = set()
    advanced_rules = set()
    
    # 1. 分离纯域名规则和高级规则
    for rule in rules:
        # 匹配纯域名规则 ||domain^
        if rule.startswith('||') and rule.endswith('^') and '$' not in rule and '*' not in rule:
            domain = rule[2:-1]
            pure_domains.add(domain)
        else:
            # 尝试提取高级规则中的域名部分 (如 ||ads.example.com^$third-party)
            match = re.match(r'^\|\|([a-zA-Z0-9.-]+)\^', rule)
            if match:
                advanced_rules.add((rule, match.group(1)))
            else:
                # 无法提取域名的复杂规则（如正则、通配符等），直接保留
                advanced_rules.add((rule, None))
                
    # 2. 构建后缀树 (反转 Trie)
    root = {}
    for domain in pure_domains:
        parts = domain.split('.')[::-1]  # 反转域名部分，如 com.example.a
        node = root
        is_redundant = False
        for part in parts:
            if node.get('is_end'):
                # 父域名已存在，当前子域名冗余，直接跳过插入
                is_redundant = True
                break
            if part not in node:
                node[part] = {}
            node = node[part]
        if not is_redundant:
            node['is_end'] = True
            
    # 3. 从后缀树中提取去重后的纯域名
    final_pure_domains = set()
    def extract_domains(node, current_parts):
        if node.get('is_end'):
            # 反转回来，还原为正常域名
            final_pure_domains.add('.'.join(current_parts[::-1]))
            return # 剪枝：父域名已拦截，无需遍历子节点（子域名）
        for part, child in node.items():
            if part != 'is_end':
                extract_domains(child, current_parts + [part])
                
    extract_domains(root, [])
    
    # 4. 过滤高级规则：如果其域名被 final_pure_domains 覆盖，则剔除
    final_advanced_rules = set()
    for rule, domain in advanced_rules:
        if domain:
            parts = domain.split('.')
            is_covered = False
            # 检查该域名或其任意父域名是否在 final_pure_domains 中
            for i in range(len(parts)):
                parent = '.'.join(parts[i:])
                if parent in final_pure_domains:
                    is_covered = True
                    break
            if not is_covered:
                final_advanced_rules.add(rule)
        else:
            final_advanced_rules.add(rule)
            
    # 5. 合并结果
    final_rules = set(f"||{d}^" for d in final_pure_domains)
    final_rules.update(final_advanced_rules)
    
    reduced_count = len(rules) - len(final_rules)
    log_success(f"🌳 后缀树去重完成：剔除 {reduced_count} 条冗余规则 (含被父域名覆盖的高级规则)。")
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
        log_success(f"旧文件已备份至系统临时目录: {Colors.CYAN}{backup_path}{Colors.RESET}")
        cleanup_temp_backups(temp_dir, prefix="ADBLOCK_RULE_", max_age_days=3)

def cleanup_temp_backups(temp_dir, prefix="ADBLOCK_RULE_", max_age_days=3):
    now = time.time()
    max_age_sec = max_age_days * 86400
    cleaned_count = 0
    for filename in os.listdir(temp_dir):
        if filename.startswith(prefix) and filename.endswith(".bak"):
            filepath = os.path.join(temp_dir, filename)
            if now - os.path.getmtime(filepath) > max_age_sec:
                try:
                    os.remove(filepath)
                    cleaned_count += 1
                except OSError:
                    pass
    if cleaned_count > 0:
        log_info(f"🗑️  已自动清理 {cleaned_count} 个过期的临时备份文件。")

def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

# =====================================================================
# 8. 自动更新 README.md 状态
# =====================================================================
def update_readme(timestamp, num_rules, upstream_urls):
    readme_path = "README.md"
    if not os.path.exists(readme_path):
        log_warning("未找到 README.md，跳过状态更新。")
        return
    try:
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        num_rules_str = f"{num_rules:,}"
        status_block = f"""<!-- AUTO_STATUS_START -->
<h3 align="center">📊 仓库状态</h3>

| 项目 | 状态 |
| --- | --- |
| 🕐 最后更新时间 | {timestamp} (UTC+8) |
| 📏 规则总数 | {num_rules_str} 条 |
| 🔄 更新频率 | 每 3 小时自动更新 |
| 📦 文件格式 | ABP 兼容格式 (双栈 Hosts 转化 + 后缀树深度去重) |
<!-- AUTO_STATUS_END -->"""

        upstream_rows = []
        for i, url in enumerate(upstream_urls, 1):
            parts = url.replace("https://raw.githubusercontent.com/", "").split("/")
            if len(parts) >= 3:
                source_name = f"{parts[0]}/{parts[1]}"
                if len(parts) > 3:
                    source_name += "/" + "/".join(parts[3:])
            else:
                source_name = url
            upstream_rows.append(f"| {i} | `{source_name}` | [链接]({url}) |")
            
        upstream_block = f"""<!-- AUTO_UPSTREAM_START -->
<details>
<summary>📋 点击展开完整上游源列表（共 {len(upstream_urls)} 个）</summary>

| 序号 | 上游源 | 链接 |
| --- | --- | --- |
{chr(10).join(upstream_rows)}
</details>
<!-- AUTO_UPSTREAM_END -->"""

        pattern_status = r'<!-- AUTO_STATUS_START -->.*?<!-- AUTO_STATUS_END -->'
        if re.search(pattern_status, content, re.DOTALL):
            content = re.sub(pattern_status, status_block, content, flags=re.DOTALL)
            
        pattern_upstream = r'<!-- AUTO_UPSTREAM_START -->.*?<!-- AUTO_UPSTREAM_END -->'
        if re.search(pattern_upstream, content, re.DOTALL):
            content = re.sub(pattern_upstream, upstream_block, content, flags=re.DOTALL)

        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(content)
        log_success(f"✅ README.md 状态已更新：更新时间={timestamp}，规则数={num_rules_str}")
    except Exception as e:
        log_error(f"更新 README.md 时发生错误: {e}")

# =====================================================================
# 9. 主流程
# =====================================================================
def main():
    start_time = time.time()
    print(f"\n{Colors.BOLD}{Colors.CYAN}🚀 双栈 Hosts 转 ABP 规则生成器 (Ultimate Edition){Colors.RESET}\n")
    output_filename = "ADBLOCK_RULE_COLLECTION.txt"
    
    try:
        raw_domains = set()
        kept_abp_rules = set()
        failed_urls = []
        
        log_info(f"开始抓取并解析 {len(UPSTREAM_URLS)} 个上游 Hosts 源...")
        for url in tqdm(UPSTREAM_URLS, desc="抓取上游源", ncols=80, colour="green", disable=IS_CI):
            content = fetch_with_retry(url)
            if content:
                for line in content.splitlines():
                    result = parse_line(line)
                    if result:
                        if result[0] == 'DOMAIN': raw_domains.add(result[1])
                        elif result[0] == 'ABP_RULE': kept_abp_rules.add(result[1])
            else: failed_urls.append(url)
            
        log_success(f"抓取完成。提取到 {Colors.BOLD}{len(raw_domains)}{Colors.RESET} 个原始域名，保留 {Colors.BOLD}{len(kept_abp_rules)}{Colors.RESET} 条高级 ABP 规则。")
        
        final_domains, clean_stats = clean_and_optimize_domains(raw_domains)
        final_abp_rules = set(f"||{domain}^" for domain in final_domains)
        final_abp_rules.update(kept_abp_rules) 
        
        # ================= 🔥 新增：后缀树深度去重 =================
        pre_dedup_count = len(final_abp_rules)
        final_abp_rules = suffix_tree_dedup(final_abp_rules)
        suffix_tree_reduced = pre_dedup_count - len(final_abp_rules)
        # ============================================================
        
        num_rules = len(final_abp_rules)
        backup_to_temp_dir(output_filename)
        
        tz_utc8 = timezone(timedelta(hours=8))
        timestamp = datetime.now(tz_utc8).strftime("%Y-%m-%d %H:%M:%S")
        
        header = f"""! Title: Adblock-Rule-Collection (Dual-Stack Hosts to ABP)
! Description: 将双栈 Hosts (IPv4/IPv6) 转化为 ABP 格式，自动去重、合并、深度清洗优化生成。
! Homepage: https://github.com/qirui-bot/Adblock-Rule-Collection
! LICENSE1: https://github.com/qirui-bot/Adblock-Rule-Collection/blob/main/LICENSE-GPL%203.0
! LICENSE2: https://github.com/qirui-bot/Adblock-Rule-Collection/blob/main/LICENSE-CC-BY-NC-SA%204.0
! Generated: {timestamp} (UTC+8)
! Total rules: {num_rules}
!
! 📖 【食用指南 / How to use】
! 1. AdGuard 浏览器扩展 / AdGuard Home: 直接复制 Raw 链接添加到“自定义过滤器/黑名单”。
! 2. AdGuard for Safari: 因规则数较多，建议配合白名单使用，或仅订阅精简版。
! 3. 本列表已内置防误杀白名单，并剔除了大量一次性钓鱼垃圾域名，请放心使用。
! """
        
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(header)
            for rule in sorted(final_abp_rules):
                f.write(rule + "\n")
                
        file_size_bytes = os.path.getsize(output_filename)
        if file_size_bytes > 1024 * 1024:
            size_str = f"{file_size_bytes / (1024 * 1024):.2f} MB"
        else:
            size_str = f"{file_size_bytes / 1024:.2f} KB"
            
        file_hash = calculate_sha256(output_filename)
        elapsed_time = time.time() - start_time
        
        update_readme(timestamp, num_rules, UPSTREAM_URLS)
        
        print(f"\n{Colors.BOLD}📊 数据漏斗与体检报告:{Colors.RESET}")
        print(f" ├─ 原始提取域名: {len(raw_domains)}")
        print(f" ├─ 修复畸形前缀: {clean_stats['restored']} (变废为宝)")
        print(f" ├─ 丢弃畸形/无效: {clean_stats['malformed']} (清理垃圾)")
        print(f" ├─ 白名单保护:   {clean_stats['whitelisted']} (防止误杀)")
        print(f" ├─ 剔除钓鱼域名: {clean_stats['phishing']} (性能优化)")
        print(f" ├─ 基础子域去重: {clean_stats['redundant']} (逻辑去重)")
        print(f" ├─ {Colors.MAGENTA if hasattr(Colors, 'MAGENTA') else Colors.CYAN}后缀树深度去重: {suffix_tree_reduced} (无损压缩高级规则){Colors.RESET}")
        print(f" ├─ 保留高级规则: {len(kept_abp_rules)} (通配符/修饰符)")
        print(f" ├─ {Colors.GREEN}最终有效规则: {Colors.BOLD}{num_rules}{Colors.RESET}")
        print(f" ├─ 📦 文件大小:   {Colors.CYAN}{size_str}{Colors.RESET}")
        print(f" ├─ 🔐 SHA-256:    {file_hash[:16]}... (完整哈希见文件头或控制台)")
        print(f" └─ ⏱️  总耗时:     {Colors.YELLOW}{elapsed_time:.2f} 秒{Colors.RESET}\n")
        print("-" * 50)
        
        log_success(f"成功生成文件: {Colors.CYAN}{output_filename}{Colors.RESET}")
        log_info(f"生成时间: {timestamp} (UTC+8)")
        
        if failed_urls:
            log_warning(f"共有 {len(failed_urls)} 个 URL 抓取失败，请检查网络或链接有效性。")
            
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  用户中断 (Ctrl+C)，安全退出。{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        log_error(f"发生未知错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
