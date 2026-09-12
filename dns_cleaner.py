"""
=============================================================================
Adblock 规则死链清洗脚本 (dns_cleaner.py) - 终极防误杀 & 缓存压缩 & README同步版
核心功能：
  1. 弃用 aiodns，改用 dnspython 精确区分 NXDOMAIN(真死) 和 SERVFAIL(假死)，确保 0 误杀。
  2. 引入增量缓存机制，大幅缩短每周运行时间。
  3. 【缓存压缩】使用 gzip 压缩 dns_cache.json，将 57MB 的缓存压缩至 10MB 以内，
     彻底解决 GitHub 50MB 警告，并大幅提升 CI 读写速度。
  4. 【精准同步】使用正则精确匹配 README.md 中的表格格式，自动更新规则总数。
=============================================================================
"""
import re
import os
import time
import json
import gzip  # 【新增】引入 gzip 模块用于压缩缓存
import dns.resolver
import dns.exception
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# ================= 1. 核心配置区 =================
INPUT_FILE = "ADBLOCK_RULE_COLLECTION.txt"
OUTPUT_FILE = "ADBLOCK_RULE_COLLECTION.txt"
# 【核心修改】将缓存文件改为 gzip 压缩格式，解决 57MB 超限问题
CACHE_FILE = "dns_cache.json.gz" 
README_FILE = "README.md"

# 【稳健配置】多线程并发 500，保证速度且不触发 DNS 限速
MAX_WORKERS = 500
DNS_TIMEOUT = 3.0 # 单次查询超时 3 秒

CACHE_ALIVE_DAYS = 30 # 存活域名 30 天内不复查
CACHE_DEAD_DAYS = 7   # 死链域名 7 天后复查（防复活）
# =================================================

# ================= 2. 缓存与 README 管理 =================
def load_cache():
    """加载并解压本地 DNS 缓存文件"""
    if os.path.exists(CACHE_FILE):
        try:
            # 【修改】使用 gzip 解压读取
            with gzip.open(CACHE_FILE, 'rt', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_cache(cache):
    """保存并压缩 DNS 缓存文件"""
    # 【修改】使用 gzip 压缩保存，并使用紧凑格式 (separators) 进一步减小体积
    with gzip.open(CACHE_FILE, 'wt', encoding='utf-8') as f:
        json.dump(cache, f, separators=(',', ':'))

def update_readme(final_count):
    """
    【精准同步】自动更新 README.md 中的规则数量统计。
    精确匹配格式：| 📏 规则总数 | 893,686 条 |
    """
    if not os.path.exists(README_FILE):
        print("⚠️ 未找到 README.md，跳过更新。")
        return

    with open(README_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    
    # 【核心正则】精确匹配 README 表格行
    pattern = r'(\| 📏 规则总数 \| )([\d,]+)( 条 \|)'
    
    def replacer(match):
        # 将新数字格式化为带千分位逗号的形式
        formatted_count = f"{final_count:,}"
        return f"{match.group(1)}{formatted_count}{match.group(3)}"

    content = re.sub(pattern, replacer, content)

    if content != original_content:
        with open(README_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"📝 已成功同步更新 README.md 中的规则数量为: {final_count:,}")
    else:
        print("⚠️ 未在 README.md 中匹配到 '| 📏 规则总数 | xxx 条 |' 格式。")

# ================= 3. 域名提取 =================
def extract_and_clean_rule(rule):
    """提取域名，同时过滤掉逻辑无效的毒瘤规则"""
    rule = rule.strip()
    if not rule or rule.startswith('!') or rule.startswith('[') or rule.startswith('@@'):
        return None, True
    # 过滤毒瘤宽泛规则
    if rule in ['||com^', '||net^', '||org^', '||cn^', '||top^']:
        return None, False 

    match = re.match(r'^\|\|([^/^\s]+)', rule)
    if match:
        domain = match.group(1).split(':')[0]
        domain = re.sub(r'[^a-zA-Z0-9.-]', '', domain)
        if domain and '.' in domain:
            return domain, True
    return None, True

# ================= 4. 稳健的 DNS 检查 =================
def check_domain_dns(domain):
    """
    使用 dnspython 检查域名。
    只有明确的 NXDOMAIN 才会返回 False，其他所有错误一律返回 True（防误杀）。
    """
    try:
        dns.resolver.resolve(domain, 'A', lifetime=DNS_TIMEOUT)
        return domain, True
    except dns.resolver.NXDOMAIN:
        return domain, False # 唯一死刑：域名确实不存在
    except (dns.resolver.NoAnswer, dns.resolver.NoNameservers, dns.exception.Timeout):
        return domain, True # 假死/超时/无响应，保守保留防误杀！
    except Exception:
        return domain, True

def batch_check_domains(domains_to_check):
    """批量多线程检查域名"""
    if not domains_to_check: return set()
    
    print(f"🌐 [稳健模式] 准备检查 {len(domains_to_check)} 个域名 (并发: {MAX_WORKERS})...")
    start_time = time.time()
    dead_domains = set()
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(check_domain_dns, d): d for d in domains_to_check}
        for future in tqdm(as_completed(futures), total=len(futures), desc="DNS检查", mininterval=2.0):
            domain, is_alive = future.result()
            if not is_alive:
                dead_domains.add(domain)
                
    elapsed = time.time() - start_time
    print(f"✅ DNS 检查完成！耗时: {elapsed:.2f} 秒。发现 {len(dead_domains)} 个真死链。")
    return dead_domains

# ================= 5. 主执行流程 =================
def main():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ 错误: 找不到输入文件 '{INPUT_FILE}'。")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        rules = f.readlines()
    
    original_count = len(rules)
    cache = load_cache()
    now = datetime.now()
    
    unique_domains = set()
    rule_domain_mapping = {}
    logically_invalid_count = 0
    
    # 步骤 A: 提取域名与逻辑清洗
    for rule in rules:
        domain, is_valid = extract_and_clean_rule(rule)
        if not is_valid:
            logically_invalid_count += 1
            continue
        if domain:
            unique_domains.add(domain)
            rule_domain_mapping[rule.strip()] = domain

    # 步骤 B: 增量缓存比对
    domains_to_check = set()
    domain_status = {}
    
    for domain in unique_domains:
        if domain in cache:
            last_check = datetime.fromtimestamp(cache[domain]['time'])
            is_alive = cache[domain]['alive']
            days_passed = (now - last_check).days
            
            if (is_alive and days_passed < CACHE_ALIVE_DAYS) or \
               (not is_alive and days_passed < CACHE_DEAD_DAYS):
                domain_status[domain] = is_alive
                continue
        domains_to_check.add(domain)

    print(f"🎯 共 {len(unique_domains)} 个域名。缓存命中 {len(unique_domains)-len(domains_to_check)} 个，需新查询 {len(domains_to_check)} 个。")

    # 步骤 C: 执行 DNS 检查
    if domains_to_check:
        dead_domains = batch_check_domains(domains_to_check)
        for d in domains_to_check:
            is_dead = d in dead_domains
            cache[d] = {'alive': not is_dead, 'time': now.timestamp()}
            domain_status[d] = not is_dead
        save_cache(cache)

    # 步骤 D: 过滤规则
    cleaned_rules = []
    removed_dead_count = 0
    
    for rule in rules:
        rule_stripped = rule.strip()
        if not rule_stripped or rule_stripped.startswith('!') or rule_stripped.startswith('['):
            cleaned_rules.append(rule)
            continue
        if rule_stripped in ['||com^', '||net^', '||org^', '||cn^', '||top^']:
            continue

        mapped_domain = rule_domain_mapping.get(rule_stripped)
        if mapped_domain and not domain_status.get(mapped_domain, True):
            removed_dead_count += 1
        else:
            cleaned_rules.append(rule)

    # 步骤 E: 写回规则文件
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.writelines(cleaned_rules)

    # 步骤 F: 输出统计报告
    print("\n" + "="*50)
    print("🎉 规则清洗任务完成！统计报告：")
    print(f" ├─ 原始规则总数: {original_count}")
    print(f" ├─ 逻辑剔除(毒瘤): {logically_invalid_count}")
    print(f" ├─ 死链剔除(无效): {removed_dead_count}")
    print(f" └─ 最终保留规则: {len(cleaned_rules)}")
    print("="*50 + "\n")

    # 步骤 G: 精准同步更新 README
    update_readme(len(cleaned_rules))

if __name__ == "__main__":
    main()
