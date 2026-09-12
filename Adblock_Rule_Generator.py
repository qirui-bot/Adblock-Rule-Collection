# -- coding: utf-8 --
"""
双栈 Hosts 转 ABP 规则生成器 (Ultimate Clean & User-Friendly Edition)

功能概述：
    解析多个上游双栈 Hosts / ABP 规则源，提取有效域名，
    转化为统一的 ABP (Adblock Plus) 格式，并进行深度清洗、去重、优化。

核心特性：
    - 自动安装缺失依赖（requests、tqdm）
    - CI 环境（GitHub Actions）自适应：禁用彩色输出与进度条
    - 彩色日志分级输出（info / success / warning / error）
    - 带进度条的抓取与清洗流程
    - 临时目录备份旧文件，防止数据丢失
    - SHA-256 文件校验
    - 数据漏斗统计（含各上游源具体新增规则数量）
    - 兼容高级 ABP 语法（通配符、白名单 @@||、$dnsrewrite 等）
    - 后缀树 (Suffix Trie) 深度去重，消除冗余子域名规则
    - 自动更新 README.md 中的仓库状态与上游源列表
    - 严格 DNS 层过滤：剔除所有美容规则、正则表达式及网络层路径规则
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
import traceback
from datetime import datetime, timezone, timedelta


# =====================================================================
# 0. 环境预检与 CI (GitHub Actions) 自适应
# =====================================================================

# 检查 Python 版本，低于 3.8 则终止运行
if sys.version_info < (3, 8):
    print("❌ 错误: 本脚本需要 Python 3.8 或更高版本。请升级您的 Python 环境。")
    sys.exit(1)

# 判断当前是否运行在 GitHub Actions CI 环境中
IS_CI = os.getenv("GITHUB_ACTIONS") == "true"

# Windows 非 CI 环境下启用 ANSI 转义序列支持（使彩色输出生效）
if os.name == 'nt' and not IS_CI:
    os.system('')


class Colors:
    """
    终端颜色常量类。
    在 CI 环境中所有颜色代码置为空字符串，避免日志中出现乱码转义符。
    """
    RESET   = "" if IS_CI else "\033[0m"
    BOLD    = "" if IS_CI else "\033[1m"
    RED     = "" if IS_CI else "\033[91m"
    GREEN   = "" if IS_CI else "\033[92m"
    YELLOW  = "" if IS_CI else "\033[93m"
    BLUE    = "" if IS_CI else "\033[94m"
    CYAN    = "" if IS_CI else "\033[96m"
    MAGENTA = "" if IS_CI else "\033[95m"


def log_info(msg):
    """输出蓝色信息级别日志"""
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.RESET}")


def log_success(msg):
    """输出绿色成功级别日志"""
    print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")


def log_warning(msg):
    """
    输出黄色警告级别日志。
    CI 环境下使用 GitHub Actions 专用的 ::warning:: 格式，
    以便在 Actions 面板中正确显示警告注释。
    """
    if IS_CI:
        print(f"::warning::{msg}")
    else:
        print(f"{Colors.YELLOW}⚠️  {msg}{Colors.RESET}")


def log_error(msg):
    """
    输出红色错误级别日志。
    CI 环境下使用 GitHub Actions 专用的 ::error:: 格式。
    """
    if IS_CI:
        print(f"::error::{msg}")
    else:
        print(f"{Colors.RED}❌ {msg}{Colors.RESET}")


# =====================================================================
# 1. 依赖自动安装 (带权限容错)
# =====================================================================

def install_package(package):
    """
    自动安装指定的 Python 包。
    先尝试全局安装，若因权限不足失败，则回退到 --user 模式安装。
    若两种方式均失败，输出错误提示并终止程序。

    Args:
        package (str): 需要安装的 pip 包名
    """
    print(f"📦 正在自动安装缺失依赖: {package}...")
    try:
        # 第一次尝试：全局安装
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", package])
    except subprocess.CalledProcessError:
        try:
            # 第二次尝试：用户级安装（无需管理员权限）
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "--user", package])
        except subprocess.CalledProcessError:
            log_error(f"无法安装 {package}，请手动执行: pip install {package}")
            sys.exit(1)


# 尝试导入 requests，若缺失则自动安装后再导入
try:
    import requests
except ImportError:
    install_package("requests")
    import requests

# 尝试导入 tqdm（进度条库），若缺失则自动安装后再导入
try:
    from tqdm import tqdm
except ImportError:
    install_package("tqdm")
    from tqdm import tqdm


# =====================================================================
# 2. 核心配置区 (硬编码，保持仓库绝对整洁)
# =====================================================================

# 上游规则源 URL 列表
# 包含多个知名 Hosts / ABP 规则仓库的原始文件地址
# 脚本会依次抓取并解析这些源
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

# 白名单域名集合
# 这些域名及其所有子域名不会被拦截，而是生成 @@|| 白名单规则
# 包含：AdGuard 官方域名、常见路由器管理地址、被误杀的正常网站
WHITELIST_DOMAINS = {
    "adguard.com", "adguard-dns.io", "adguard.info",
    "fritz.box", "fritz.nas", "fritz.repeater", "router.asus.com", "miwifi.com",
    "change.org", "binance.com", "freshbooks.com", "freepik.com", "garmin.com",
    "leadpages.co", "clickfunnels.com", "wixsite.com", "weebly.com", "ck.page"
}


# =====================================================================
# 3. 正则表达式引擎 (清洗管道)
# =====================================================================

# 匹配 Hosts 文件中的 IP 前缀行，捕获后面的域名部分
# 支持 0.0.0.0、0.0.0、127.0.0.1、localhost 等常见前缀
RE_HOSTS_PREFIX = re.compile(r'^(?:0\.0\.0\.0|0\.0\.0|127\.0\.0\.1|localhost)[.\-]?(.*)$', re.IGNORECASE)

# 匹配免费托管平台上的随机哈希子域名（通常是钓鱼/垃圾站点）
# 例如：a1b2c3d4e5f6.netlify.app、xyz789abc123.vercel.app
RE_FREE_HOSTING_HASH = re.compile(
    r'^[a-z0-9\-]{12,}\.(netlify\.app|vercel\.app|web\.app|firebaseapp\.com|pages\.dev|000webhostapp\.com|github\.io|glitch\.me|repl\.co)$'
)

# 匹配纯数字域名（如 12345.com）或裸 IP 地址，这些通常是无效/低质量条目
RE_PURE_NUMERIC_OR_IP = re.compile(r'^(\d+\.(com|net|org|xyz|top|club|info|biz)|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})$')

# 匹配内网/本地保留后缀，这些域名不应出现在公共拦截列表中
RE_MALFORMED_SUFFIX = re.compile(r'\.(domain\.name|local|lan|corp|internal|home|nas)$')

# 标准域名合法性校验正则
# 规则：总长度 1-253 字符，每级标签 1-63 字符，仅含字母数字和连字符，顶级域 2-63 字符
RE_DOMAIN_VALID = re.compile(r'^(?=.{1,253}$)(?:[A-Za-z0-9\-]{1,63}\.)+[A-Za-z0-9\-]{2,63}$')


# =====================================================================
# 4. 核心解析函数 (精准剥离修饰符，绝对拦截路径特征)
# =====================================================================

# ABP 语法中合法的 # 开头前缀（美容规则等）
# 这些规则在 DNS 层面无法处理，解析时会被识别并丢弃
_VALID_HASH_PREFIXES = ("##", "#@#", "#$#", "#$@#", "#?#", "#@?#", "#%#")


def is_comment_line(line: str) -> bool:
    """
    判断一行是否为注释行。

    注释行的判定规则：
    - 以 '!' 开头（ABP 标准注释）
    - 以 '[' 开头（Adblock 元数据头，如 [Adblock Plus 2.0]）
    - 以 '#' 开头，但不属于合法的 ABP 美容规则前缀

    Args:
        line (str): 待判断的文本行

    Returns:
        bool: True 表示是注释行，应跳过
    """
    if line.startswith('!') or line.startswith('['):
        return True
    if line.startswith('#') and not line.startswith(_VALID_HASH_PREFIXES):
        return True
    return False


def parse_line(line: str):
    """
    智能解析每一行规则，将其分类为纯域名或 ABP 规则。

    解析策略优先级：
    A) @@ 开头 → 白名单规则，直接保留
    B) / 开头 → 正则表达式规则，DNS 层无法处理，丢弃
    C) || 开头 → ABP 拦截规则，剥离 $ 修饰符后提取域名部分
       - 若包含 / ? | 等路径/参数特征，判定为网络层规则，丢弃
       - 若包含 * 通配符，保留为 ABP 规则
       - 若为合法纯域名，归类为 DOMAIN
    D) ## 等美容规则前缀 → DNS 无法处理，丢弃
    E) Hosts 格式 (IP + 域名) → 提取纯域名
    F) 单列纯域名 → 直接归类为 DOMAIN

    Args:
        line (str): 待解析的文本行

    Returns:
        tuple|None: ('DOMAIN', domain) 或 ('ABP_RULE', rule) 或 None（丢弃）
    """
    stripped = line.strip()

    # 跳过空行和注释行
    if not stripped or is_comment_line(stripped):
        return None

    # 🔥 策略 A: 识别并保留白名单规则（@@ 开头）
    if stripped.startswith('@@'):
        return ('ABP_RULE', stripped)

    # 🔥 策略 B: 坚决丢弃正则表达式规则（/ 开头，DNS 层面无法处理）
    if stripped.startswith('/'):
        return None

    # 🔥 策略 C: 专门处理 || 开头的拦截规则（核心修复）
    if stripped.startswith('||'):
        # 步骤 1: 精准剥离 $ 修饰符（如 $important, $third-party 等），只取域名部分
        base_rule = stripped.split('$')[0]

        # 步骤 2: 提取 || 和 ^ 之间的内容（自动补全缺失的 ^）
        if base_rule.endswith('^'):
            domain_part = base_rule[2:-1]
        else:
            domain_part = base_rule[2:]

        # 🔥 步骤 3: 绝对防线 —— 只要包含 / ? |，直接判定为网络层/路径规则，坚决丢弃
        if '/' in domain_part or '?' in domain_part or '|' in domain_part:
            return None

        # 步骤 4: 剩下的才可能是合法的域名或域名通配符
        if '*' in domain_part:
            # 包含通配符，保留为 ABP 规则格式
            return ('ABP_RULE', f"||{domain_part}^")
        elif RE_DOMAIN_VALID.match(domain_part):
            # 合法纯域名，归类为 DOMAIN（后续统一转 ABP 格式）
            return ('DOMAIN', domain_part)
        else:
            # 非标准但可能是有效的 ABP 域名模式，保留为 ABP 规则
            return ('ABP_RULE', f"||{domain_part}^")

    # 🔥 策略 D: 其他高级 ABP 规则（如 ## 美容规则），DNS 无法处理，坚决丢弃
    if any(stripped.startswith(p) for p in _VALID_HASH_PREFIXES):
        return None

    # 策略 E: 解析 Hosts 格式（IP 地址 + 域名）
    parts = stripped.split()
    if len(parts) >= 2:
        ip_part, domain_part = parts[0], parts[1]
        try:
            # 验证第一部分是否为合法 IP 地址
            ipaddress.ip_address(ip_part)
            # 排除系统保留域名（localhost 等）
            reserved_domains = {
                'localhost', 'localhost.localdomain', 'broadcasthost',
                'ip6-localhost', 'ip6-loopback', 'ip6-localnet',
                'ip6-mcastprefix', 'ip6-allnodes', 'ip6-allrouters'
            }
            if domain_part.lower() in reserved_domains:
                return None
            return ('DOMAIN', domain_part)
        except ValueError:
            # 第一部分不是合法 IP，继续尝试其他解析策略
            pass

    # 策略 F: 单列纯域名（无 IP 前缀）
    if len(parts) == 1:
        return ('DOMAIN', parts[0])

    # 无法识别的行格式，丢弃
    return None


# =====================================================================
# 5. 深度清洗与去重管道
# =====================================================================

def clean_and_optimize_domains(raw_domains):
    """
    对原始域名集合执行深度清洗与优化。

    清洗流程（按顺序执行）：
    1. 统一转小写、去除空白
    2. 尝试从残留的 Hosts 前缀中恢复域名
    3. 域名合法性校验（RE_DOMAIN_VALID）
    4. 剔除纯数字域名和裸 IP 地址
    5. 剔除内网/本地保留后缀域名
    6. 白名单域名直接放行（不参与后续过滤）
    7. 剔除免费托管平台上的随机哈希子域名（钓鱼/垃圾站）
    8. 后缀树去重：若父域名已存在，则剔除其所有子域名

    Args:
        raw_domains (set): 原始解析出的域名集合

    Returns:
        tuple: (final_domains: set, stats: dict)
            - final_domains: 清洗后的最终域名集合
            - stats: 各清洗步骤的统计计数
    """
    log_info("🧹 启动深度清洗与优化管道...")

    # 统计字典：记录各清洗步骤剔除/处理的域名数量
    stats = {'restored': 0, 'phishing': 0, 'whitelisted': 0, 'redundant': 0, 'malformed': 0}
    cleaned_domains = set()

    # 使用 tqdm 进度条遍历所有原始域名（CI 环境下禁用进度条）
    iterator = tqdm(raw_domains, desc="清洗域名", ncols=80, colour="cyan", disable=IS_CI)

    for domain in iterator:
        # 统一转小写并去除首尾空白
        domain = domain.strip().lower()
        if not domain:
            continue

        # 步骤 1: 检查是否残留 Hosts 前缀（如 "0.0.0.0example.com"），尝试恢复
        match = RE_HOSTS_PREFIX.match(domain)
        if match:
            restored_domain = match.group(1)
            if restored_domain and RE_DOMAIN_VALID.match(restored_domain):
                domain = restored_domain
                stats['restored'] += 1
            else:
                stats['malformed'] += 1
                continue

        # 步骤 2: 域名合法性校验
        if not RE_DOMAIN_VALID.match(domain):
            stats['malformed'] += 1
            continue

        # 步骤 3: 剔除纯数字域名和裸 IP 地址
        if RE_PURE_NUMERIC_OR_IP.match(domain):
            stats['malformed'] += 1
            continue

        # 步骤 4: 剔除内网/本地保留后缀
        if RE_MALFORMED_SUFFIX.search(domain):
            stats['malformed'] += 1
            continue

        # 步骤 5: 白名单域名直接放行，不参与后续过滤
        # 🔧 修复：白名单域名也需要进行合法性校验，避免无效域名进入白名单
        if any(domain == w or domain.endswith('.' + w) for w in WHITELIST_DOMAINS):
            if RE_DOMAIN_VALID.match(domain):  # 新增：白名单域名合法性校验
                cleaned_domains.add(domain)
                stats['whitelisted'] += 1
            else:
                stats['malformed'] += 1  # 不合法的白名单域名计入畸形统计
            continue

        # 步骤 6: 剔除免费托管平台上的随机哈希子域名（高概率钓鱼/垃圾站）
        if RE_FREE_HOSTING_HASH.match(domain):
            stats['phishing'] += 1
            continue

        # 通过所有检查，加入清洗后集合
        cleaned_domains.add(domain)

    # 步骤 7: 剔除冗余子域名
    # 原理：若父域名（如 example.com）已在集合中，
    # 则其子域名（如 ad.example.com）是冗余的，因为拦截父域名已覆盖所有子域名
    log_info("🔍 正在剔除冗余子域名...")
    # 按域名长度升序排序，确保父域名先被处理
    sorted_domains = sorted(cleaned_domains, key=len)
    final_domains = set()

    for domain in sorted_domains:
        parts = domain.split('.')
        is_redundant = False
        # 逐级检查是否存在已收录的父域名
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
    """
    使用后缀树（反转 Trie 树）对 ABP 规则进行无损深度去重。

    算法原理：
    1. 将规则分为"纯域名规则"和"高级规则"（含通配符等）
    2. 对纯域名规则，将域名按 '.' 分割后反转，插入 Trie 树
       例如 "ad.example.com" → ["com", "example", "ad"]
    3. 插入时若经过已标记 is_end 的节点，说明存在更短的父域名，当前域名为冗余
    4. 遍历 Trie 树提取所有非冗余域名
    5. 对高级规则，检查其域名部分是否已被纯域名规则覆盖

    Args:
        rules (set): 待去重的 ABP 规则集合

    Returns:
        set: 去重后的最终规则集合
    """
    log_info("🌳 启动后缀树 (Suffix Tree) 深度去重管道...")

    # 分类：纯域名规则 vs 高级规则（含通配符 * 或其他特殊语法）
    pure_domains, advanced_rules = set(), set()

    for rule in rules:
        # 纯域名规则特征：以 || 开头、以 ^ 结尾、不含 $ 修饰符和 * 通配符
        if rule.startswith('||') and rule.endswith('^') and '$' not in rule and '*' not in rule:
            pure_domains.add(rule[2:-1])  # 提取 || 和 ^ 之间的域名
        else:
            # 尝试从高级规则中提取域名部分（允许包含 * 通配符）
            match = re.match(r'^\|\|([a-zA-Z0-9*.\-]+)\^', rule)
            if match:
                advanced_rules.add((rule, match.group(1)))
            else:
                # 无法提取域名的规则（如白名单等），保留但不参与去重
                advanced_rules.add((rule, None))

    # 构建反转 Trie 树（后缀树）
    root = {}
    for domain in pure_domains:
        # 将域名按 '.' 分割并反转，使顶级域在根节点附近
        parts = domain.split('.')[::-1]
        node, is_redundant = root, False
        for part in parts:
            # 若路径上已有 is_end 标记，说明存在更短的父域名，当前域名为冗余
            if node.get('is_end'):
                is_redundant = True
                break
            if part not in node:
                node[part] = {}
            node = node[part]
        if not is_redundant:
            node['is_end'] = True

    # 从 Trie 树中提取所有非冗余域名
    final_pure_domains = set()

    def extract_domains(node, current_parts):
        """递归遍历 Trie 树，收集所有标记为 is_end 的完整域名"""
        if node.get('is_end'):
            # 将反转的部件列表还原为正常域名
            final_pure_domains.add('.'.join(current_parts[::-1]))
            return  # is_end 节点的后代都是冗余子域名，无需继续遍历
        for part, child in node.items():
            if part != 'is_end':
                extract_domains(child, current_parts + [part])

    extract_domains(root, [])

    # 过滤高级规则：若其域名部分已被纯域名规则覆盖，则剔除
    final_advanced_rules = set()
    for rule, domain in advanced_rules:
        if domain:
            parts, is_covered = domain.split('.'), False
            # 检查该域名的任意后缀是否已在纯域名集合中
            for i in range(len(parts)):
                if '.'.join(parts[i:]) in final_pure_domains:
                    is_covered = True
                    break
            if not is_covered:
                final_advanced_rules.add(rule)
        else:
            # 无法提取域名的规则直接保留
            final_advanced_rules.add(rule)

    # 合并纯域名规则和高级规则，生成最终集合
    final_rules = set(f"||{d}^" for d in final_pure_domains)
    final_rules.update(final_advanced_rules)

    log_success(f"🌳 后缀树去重完成：剔除 {len(rules) - len(final_rules)} 条冗余规则。")
    return final_rules


# =====================================================================
# 7. 网络请求、备份与临时文件清理
# =====================================================================

def fetch_with_retry(url, retries=3, timeout=15):
    """
    带重试机制的 HTTP GET 请求。
    🔧 优化：使用指数退避策略，提高网络不稳定环境下的成功率。

    Args:
        url (str): 目标 URL
        retries (int): 最大重试次数，默认 3 次
        timeout (int): 单次请求超时秒数，默认 15 秒

    Returns:
        str|None: 成功返回响应文本，全部重试失败返回 None
    """
    for i in range(retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()  # 非 2xx 状态码抛出异常
            return response.text
        except Exception as e:
            if i < retries - 1:
                # 🔧 优化：使用指数退避（2^i 秒），避免频繁重试加重服务器负担
                wait_time = 2 ** i
                time.sleep(wait_time)
            else:
                # 所有重试均失败，记录警告
                log_warning(f"抓取失败 {url} -> {e}")
                return None


def backup_to_temp_dir(file_path):
    """
    将指定文件备份到系统临时目录。
    备份文件名包含时间戳，避免覆盖。

    Args:
        file_path (str): 需要备份的文件路径
    """
    if os.path.exists(file_path):
        temp_dir = tempfile.gettempdir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(temp_dir, f"ADBLOCK_RULE_{timestamp}.bak")
        shutil.copy2(file_path, backup_path)  # copy2 保留文件元数据
        log_success(f"旧文件已备份至: {Colors.CYAN}{backup_path}{Colors.RESET}")


def calculate_sha256(file_path):
    """
    计算文件的 SHA-256 哈希值，用于完整性校验。
    🔧 优化：使用更大的读取块（64KB），提高大文件处理效率。

    Args:
        file_path (str): 目标文件路径

    Returns:
        str: 十六进制格式的 SHA-256 哈希字符串
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # 🔧 优化：块大小从 4096 字节增大到 65536 字节（64KB），减少 I/O 次数
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def load_previous_rules(file_path):
    """
    从上一次生成的规则文件中加载规则集合。
    用于对比计算新增规则数量。

    Args:
        file_path (str): 规则文件路径

    Returns:
        set: 旧规则集合，若文件不存在则返回空集合
    """
    if not os.path.exists(file_path):
        return set()
    
    previous_rules = set()
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # 跳过注释行和空行
                if line and not line.startswith('!'):
                    previous_rules.add(line)
    except Exception as e:
        log_warning(f"读取旧规则文件失败: {e}")
    
    return previous_rules


# =====================================================================
# 8. 自动更新 README.md 状态
# =====================================================================

def update_readme(timestamp, num_rules, upstream_urls):
    """
    自动更新 README.md 中的仓库状态表格和上游源列表。

    通过 HTML 注释标记 <!-- AUTO_STATUS_START/END --> 和
    <!-- AUTO_UPSTREAM_START/END --> 定位需要替换的区域，
    使用正则表达式进行精准替换，不影响 README 的其他内容。

    🔧 修复：Markdown 表格的 | 两侧必须添加空格，否则渲染异常。

    Args:
        timestamp (str): 格式化的时间戳字符串
        num_rules (int): 最终规则总数
        upstream_urls (list): 上游源 URL 列表
    """
    readme_path = "README.md"
    if not os.path.exists(readme_path):
        return

    try:
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        num_rules_str = f"{num_rules:,}"

        # 构建仓库状态表格 HTML 块
        # 🔧 修复：| 两侧添加空格，确保 Markdown 表格正确渲染
        status_block = f"""<!-- AUTO_STATUS_START -->
<h3 align="center">📊 仓库状态</h3>

| 项目 | 状态 |
| --- | --- |
| 🕐 最后更新时间 | {timestamp} (UTC+8) |
| 📏 规则总数 | {num_rules_str} 条 |
| 🔄 更新频率 | 每 5 小时自动更新 |
| 📦 文件格式 | ABP 兼容格式 (支持通配符/静默拦截，已剔除正则) |
<!-- AUTO_STATUS_END -->"""

        # 构建上游源列表的可折叠详情块
        upstream_rows = []
        for i, url in enumerate(upstream_urls, 1):
            # 从 URL 中提取 "用户名/仓库名" 作为源名称
            parts = url.replace("https://raw.githubusercontent.com/", "").split("/")
            source_name = f"{parts[0]}/{parts[1]}" if len(parts) >= 3 else url
            upstream_rows.append(f"| {i} | `{source_name}` | [链接]({url}) |")

        # 🔧 修复：| 两侧添加空格，确保 Markdown 表格正确渲染
        upstream_block = f"""<!-- AUTO_UPSTREAM_START -->
<details>
<summary>📋 点击展开完整上游源列表（共 {len(upstream_urls)} 个）</summary>

| 序号 | 上游源 | 链接 |
| --- | --- | --- |
{chr(10).join(upstream_rows)}
</details>
<!-- AUTO_UPSTREAM_END -->"""

        # 使用正则表达式替换标记区域内的内容（re.DOTALL 使 . 匹配换行符）
        content = re.sub(r'<!-- AUTO_STATUS_START -->.*?<!-- AUTO_STATUS_END -->', status_block, content, flags=re.DOTALL)
        content = re.sub(r'<!-- AUTO_UPSTREAM_START -->.*?<!-- AUTO_UPSTREAM_END -->', upstream_block, content, flags=re.DOTALL)

        # 写回更新后的内容
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(content)

        log_success("✅ README.md 状态已更新")
    except Exception as e:
        log_error(f"更新 README.md 失败: {e}")


# =====================================================================
# 9. 辅助函数：从 URL 提取简短源名称
# =====================================================================

def extract_source_name(url):
    """
    从 GitHub raw URL 中提取 "用户名/仓库名" 格式的简短名称。
    若非 GitHub URL，则返回完整 URL。

    Args:
        url (str): 上游源 URL

    Returns:
        str: 简短的源名称
    """
    parts = url.replace("https://raw.githubusercontent.com/", "").split("/")
    return f"{parts[0]}/{parts[1]}" if len(parts) >= 3 else url


# =====================================================================
# 10. 主流程
# =====================================================================

def main():
    """
    主执行流程：
    1. 加载上一次生成的规则文件
    2. 抓取并解析所有上游源（记录每条规则的首次来源）
    3. 深度清洗域名
    4. 转换为 ABP 格式
    5. 后缀树去重
    6. 严格 DNS 层过滤
    7. 生成输出文件
    8. 输出详细数据漏斗报告（含各上游源具体新增规则数量）
    9. 更新 README.md
    """
    start_time = time.time()
    print(f"\n{Colors.BOLD}{Colors.CYAN}🚀 双栈 Hosts 转 ABP 规则生成器 (Ultimate Edition){Colors.RESET}\n")

    output_filename = "ADBLOCK_RULE_COLLECTION.txt"

    try:
        # ---- 加载旧规则文件，用于计算新增规则 ----
        previous_rules = load_previous_rules(output_filename)
        if previous_rules:
            log_info(f"已加载旧规则文件，共 {len(previous_rules):,} 条规则，将计算新增规则数量")
        else:
            log_info("未找到旧规则文件，本次为首次生成")

        # ---- 初始化数据容器 ----
        # 使用字典记录每条规则的首次来源，key 是规则/域名，value 是源名称
        raw_domains = {}        # 原始域名 → 首次出现的源
        kept_abp_rules = {}     # ABP 规则 → 首次出现的源
        failed_urls = []        # 抓取失败的 URL 列表
        upstream_stats = {}     # 各上游源的详细统计

        log_info(f"开始抓取并解析 {len(UPSTREAM_URLS)} 个上游源...")

        # ---- 阶段 1: 抓取并解析所有上游源 ----
        for url in tqdm(UPSTREAM_URLS, desc="抓取上游源", ncols=80, colour="green", disable=IS_CI):
            content = fetch_with_retry(url)
            source_name = extract_source_name(url)

            # 为当前源初始化独立计数器
            url_domains_count = 0
            url_abp_rules_count = 0

            if content:
                # 逐行解析内容
                for line in content.splitlines():
                    result = parse_line(line)
                    if result:
                        if result[0] == 'DOMAIN':
                            domain = result[1]
                            url_domains_count += 1
                            # 仅记录首次出现的源
                            if domain not in raw_domains:
                                raw_domains[domain] = source_name
                        elif result[0] == 'ABP_RULE':
                            rule = result[1]
                            url_abp_rules_count += 1
                            # 仅记录首次出现的源
                            if rule not in kept_abp_rules:
                                kept_abp_rules[rule] = source_name
            else:
                failed_urls.append(url)

            # 记录当前上游源的统计信息
            upstream_stats[source_name] = {
                'domains': url_domains_count,
                'abp_rules': url_abp_rules_count,
                'total': url_domains_count + url_abp_rules_count,
                'status': '✅' if content else '❌ 抓取失败'
            }

        # ---- 阶段 2: 深度清洗与优化域名 ----
        final_domains, clean_stats = clean_and_optimize_domains(set(raw_domains.keys()))

        # ---- 阶段 3: 将清洗后的域名转换为 ABP 格式规则 ----
        final_abp_rules = {}  # 规则 → 来源
        for domain in final_domains:
            # 判断是否为白名单域名，是则生成 @@|| 白名单规则
            is_whitelist = any(domain == w or domain.endswith('.' + w) for w in WHITELIST_DOMAINS)
            if is_whitelist:
                rule = f"@@||{domain}^$important"
            else:
                rule = f"||{domain}^"
            # 保留来源信息
            final_abp_rules[rule] = raw_domains.get(domain, 'unknown')

        # 合并从上游源直接保留的 ABP 规则
        for rule, source in kept_abp_rules.items():
            if rule not in final_abp_rules:
                final_abp_rules[rule] = source

        # ---- 阶段 4: 后缀树深度去重 ----
        pre_dedup_count = len(final_abp_rules)
        deduped_rules_set = suffix_tree_dedup(set(final_abp_rules.keys()))
        suffix_tree_reduced = pre_dedup_count - len(deduped_rules_set)
        
        # 保留去重后的来源信息
        final_abp_rules = {rule: final_abp_rules[rule] for rule in deduped_rules_set if rule in final_abp_rules}

        # ---- 阶段 5: 严格 DNS 层过滤（终极防线） ----
        # 目标：确保最终输出仅包含 DNS 层面可执行的有效规则
        strict_dns_rules = {}  # 规则 → 来源

        for rule, source in final_abp_rules.items():
            rule = rule.strip()
            if not rule:
                continue

            # 处理白名单规则 (@@||...^)
            if rule.startswith('@@||'):
                match = re.match(r'^@@\|\|([a-zA-Z0-9*.\-]+)\^', rule)
                # 确保白名单域名中不含路径或参数特征
                if match and '/' not in match.group(1) and '?' not in match.group(1):
                    strict_dns_rules[f"@@||{match.group(1)}^$important"] = source
                continue

            # 处理拦截规则 (||...^)
            if rule.startswith('||') and rule.endswith('^'):
                domain_part = rule[2:-1]

                # 🔥 第一道防线：绝对不允许出现路径(/)、参数(?)、管道符(|)
                if '/' in domain_part or '?' in domain_part or '|' in domain_part:
                    continue

                # 🔥 第二道防线：处理通配符 '*'，并防范顶级域名误杀
                if '*' in domain_part:
                    # 跳过形如 *.com、*.net 等顶级域名通配（会造成大面积误杀）
                    if re.match(r'^\*\.[a-zA-Z]{2,6}$', domain_part):
                        continue
                    # 跳过国际化顶级域名通配（如 *.xn--xxx）
                    if re.match(r'^\*\.xn--[a-zA-Z0-9\-]+$', domain_part):
                        continue
                    # 合法通配符规则，添加 $dnsrewrite=NOERROR 后缀
                    strict_dns_rules[f"{rule}$dnsrewrite=NOERROR"] = source

                # 第三道防线：处理纯域名（通过正则校验）
                elif RE_DOMAIN_VALID.match(domain_part):
                    strict_dns_rules[f"{rule}$dnsrewrite=NOERROR"] = source

                # 第四道防线：处理 IP 地址（直接保留，不添加 dnsrewrite）
                else:
                    try:
                        ipaddress.ip_address(domain_part)
                        strict_dns_rules[rule] = source
                    except ValueError:
                        # 既非合法域名也非 IP，丢弃
                        continue
                continue

        # ---- 阶段 6: 生成输出文件 ----
        num_rules = len(strict_dns_rules)

        # 备份旧文件到临时目录
        backup_to_temp_dir(output_filename)

        # 生成 UTC+8 时间戳
        tz_utc8 = timezone(timedelta(hours=8))
        timestamp = datetime.now(tz_utc8).strftime("%Y-%m-%d %H:%M:%S")

        # 构建文件头部注释（ABP 标准格式）
        header = f"""! Title: Adblock-Rule-Collection (Strict DNS Rules)
! Description: 仅包含由 || 和 @@|| 开头且经过严格校验的有效 DNS 拦截规则。已自动剔除所有美容规则、正则及网络层路径规则。
! Homepage: https://github.com/qirui-bot/Adblock-Rule-Collection
! LICENSE1: https://github.com/qirui-bot/Adblock-Rule-Collection/blob/main/LICENSE-GPL%203.0
! LICENSE2: https://github.com/qirui-bot/Adblock-Rule-Collection/blob/main/LICENSE-CC-BY-NC-SA%204.0
! Generated: {timestamp} (UTC+8)
! Total rules: {num_rules}
"""

        # 写入输出文件：头部注释 + 排序后的规则
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(header)
            for rule in sorted(strict_dns_rules.keys()):
                f.write(rule + "\n")

        # ---- 阶段 7: 计算文件元数据 ----
        file_size_bytes = os.path.getsize(output_filename)
        # 根据文件大小选择合适的单位
        if file_size_bytes > 1024 * 1024:
            size_str = f"{file_size_bytes / (1024 * 1024):.2f} MB"
        else:
            size_str = f"{file_size_bytes / 1024:.2f} KB"

        file_hash = calculate_sha256(output_filename)
        elapsed_time = time.time() - start_time

        # ---- 阶段 8: 更新 README.md ----
        update_readme(timestamp, num_rules, UPSTREAM_URLS)

        # ---- 阶段 9: 计算各上游源的新增规则数量 ----
        # 计算新增规则集合
        new_rules = set(strict_dns_rules.keys()) - previous_rules
        
        # 统计每个源贡献的新增规则数量
        source_new_counts = {}
        for rule in new_rules:
            source = strict_dns_rules.get(rule, 'unknown')
            source_new_counts[source] = source_new_counts.get(source, 0) + 1

        # ---- 阶段 10: 输出详细数据漏斗报告 ----
        print(f"\n{Colors.BOLD}📊 数据漏斗与体检报告:{Colors.RESET}")

        # 10.1 各上游源贡献明细（仅显示新增规则数量）
        print(f" │")
        print(f" ├─ {Colors.BOLD}📥 上游源新增规则明细:{Colors.RESET}")
        for source_name, stat in upstream_stats.items():
            status_icon = stat['status']
            new_count = source_new_counts.get(source_name, 0)
            
            if stat['total'] > 0:
                if new_count > 0:
                    print(f" │   ├─ {status_icon} {Colors.CYAN}{source_name}{Colors.RESET}: "
                          f"新增 {Colors.GREEN}{Colors.BOLD}+{new_count}{Colors.RESET} 条 "
                          f"(本次解析 {stat['total']} 条)")
                else:
                    print(f" │   ├─ {status_icon} {Colors.CYAN}{source_name}{Colors.RESET}: "
                          f"无新增 (本次解析 {stat['total']} 条)")
            else:
                print(f" │   ├─ {status_icon} {Colors.CYAN}{source_name}{Colors.RESET}: "
                      f"无有效规则")

        # 失败源汇总
        if failed_urls:
            print(f" │   └─ {Colors.RED}❌ 抓取失败源: {len(failed_urls)} 个{Colors.RESET}")
        else:
            print(f" │   └─ {Colors.GREEN}✅ 所有上游源抓取成功{Colors.RESET}")

        # 10.2 数据漏斗各阶段统计
        print(f" │")
        print(f" ├─ {Colors.BOLD}🔢 数据漏斗:{Colors.RESET}")
        print(f" │   ├─ 原始提取域名总数: {Colors.YELLOW}{len(raw_domains):,}{Colors.RESET}")
        print(f" │   ├─ 直接保留ABP规则: {Colors.YELLOW}{len(kept_abp_rules):,}{Colors.RESET}")
        print(f" │   │")
        print(f" │   ├─ {Colors.MAGENTA}🧹 深度清洗统计:{Colors.RESET}")
        print(f" │   │   ├─ 从Hosts前缀恢复: {clean_stats['restored']:,}")
        print(f" │   │   ├─ 剔除畸形域名: {clean_stats['malformed']:,}")
        print(f" │   │   ├─ 剔除钓鱼/垃圾站: {clean_stats['phishing']:,}")
        print(f" │   │   ├─ 白名单放行: {clean_stats['whitelisted']:,}")
        print(f" │   │   └─ 剔除冗余子域名: {clean_stats['redundant']:,}")
        print(f" │   │")
        print(f" │   ├─ 清洗后有效域名: {Colors.YELLOW}{len(final_domains):,}{Colors.RESET}")
        print(f" │   ├─ 合并后规则总数: {Colors.YELLOW}{pre_dedup_count:,}{Colors.RESET}")
        print(f" │   ├─ 🌳 后缀树去重剔除: {Colors.RED}{suffix_tree_reduced:,}{Colors.RESET} 条冗余")
        print(f" │   ├─ 去重后规则数: {Colors.YELLOW}{len(final_abp_rules):,}{Colors.RESET}")
        print(f" │   ├─ 🛡️ 严格DNS过滤剔除: {Colors.RED}{len(final_abp_rules) - num_rules:,}{Colors.RESET} 条无效规则")
        print(f" │   │")
        print(f" │   ├─ {Colors.GREEN}{Colors.BOLD}✅ 最终有效规则: {num_rules:,}{Colors.RESET}")
        print(f" │   └─ {Colors.GREEN}{Colors.BOLD}🆕 本次新增规则: {len(new_rules):,}{Colors.RESET}")

        # 10.3 文件元数据
        print(f" │")
        print(f" ├─ 📦 文件大小: {Colors.CYAN}{size_str}{Colors.RESET}")
        print(f" ├─ 🔐 SHA-256: {Colors.CYAN}{file_hash}{Colors.RESET}")
        print(f" └─ ⏱️  总耗时: {Colors.YELLOW}{elapsed_time:.2f} 秒{Colors.RESET}\n")

        log_success(f"成功生成文件: {Colors.CYAN}{output_filename}{Colors.RESET}")

    except KeyboardInterrupt:
        # 用户手动中断（Ctrl+C），安全退出
        print(f"\n{Colors.YELLOW}⚠️ 用户中断，安全退出。{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        # 🔧 优化：记录完整的堆栈信息，便于调试定位问题
        log_error(f"发生未知错误: {e}")
        if not IS_CI:  # CI 环境下不输出堆栈，避免日志过长
            print(f"{Colors.RED}{traceback.format_exc()}{Colors.RESET}")
        sys.exit(1)


# =====================================================================
# 程序入口
# =====================================================================
if __name__ == "__main__":
    main()
