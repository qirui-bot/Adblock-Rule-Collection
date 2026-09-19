#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Adblock-Rule-Collection 自定义规则剔除与统计更新脚本
功能：剔除指定上游规则、同步更新规则文件头部与 README.md 的数量统计。
使用：配置下方 EXCLUDE_SOURCES 链接后，运行 python3 custom_rules_injector.py
"""
import requests
import os
import re

# ==================== 【配置区域】 ====================
# 需要【去除】的上游源链接 (在此添加你希望剔除的第三方规则列表 URL)
EXCLUDE_SOURCES = [
    "https://raw.githubusercontent.com/REIJI007/Adblock-Rule-Collection/main/ADBLOCK_RULE_COLLECTION_DNS.txt",
    "https://raw.githubusercontent.com/Natsuki-Kaede/Natsuki-List/main/adguardhome.txt",
    "https://filters.adtidy.org/android/filters/15_optimized.txt",
    "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.roku.txt",
    "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.lgwebos.txt",
    "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.samsung.txt",
    "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.apple.txt",
    "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.amazon.txt",
    "https://raw.githubusercontent.com/ABPindo/indonesianadblockrules/master/subscriptions/abpindo.txt",
    "https://raw.githubusercontent.com/yous/YousList/master/hosts.txt",
    "https://raw.githubusercontent.com/DandelionSprout/adfilt/master/NorwegianExperimentalList%20alternate%20versions/NordicFiltersAdGuardHome.txt",
    "https://raw.githubusercontent.com/MajkiIT/polish-ads-filter/master/polish-pihole-filters/hostfile.txt",
    "https://raw.githubusercontent.com/lassekongo83/Frellwits-filter-lists/master/Frellwits-Swedish-Hosts-File.txt",
    "https://easylist-downloads.adblockplus.org/easylistdutch.txt",
    "https://raw.githubusercontent.com/DRSDavidSoft/additional-hosts/master/domains/blacklist/unwanted-iranian.txt",
    "https://raw.githubusercontent.com/cchevy/macedonian-pi-hole-blocklist/master/hosts.txt",
    "https://paulgb.github.io/BarbBlock/blacklists/hosts-file.txt",
    "https://www.github.developerdan.com/hosts/lists/facebook-extended.txt",
    "https://www.github.developerdan.com/hosts/lists/dating-services-extended.txt",
    "https://raw.githubusercontent.com/anudeepND/blacklist/master/facebook.txt",
    "https://abpvn.com/android/abpvn.txt",
    "https://raw.githubusercontent.com/bigdargon/hostsVN/master/hosts",
    "https://raw.githubusercontent.com/FadeMind/hosts.extras/master/GoodbyeAds-YouTube-Adblock-Extension/hosts",
    "https://raw.githubusercontent.com/nextdns/native-tracking-domains/main/domains/alexa",
    "https://raw.githubusercontent.com/nextdns/native-tracking-domains/main/domains/apple",
    "https://raw.githubusercontent.com/nextdns/native-tracking-domains/main/domains/roku",
    "https://raw.githubusercontent.com/nextdns/native-tracking-domains/main/domains/samsung",
    "https://raw.githubusercontent.com/nextdns/native-tracking-domains/main/domains/sonos",
    "https://raw.githubusercontent.com/xxcriticxx/.pl-host-file/master/hosts.txt",
    "https://raw.githubusercontent.com/jerryn70/GoodbyeAds/master/Formats/GoodbyeAds-YouTube-AdBlock-Filter.txt",
    "https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/fakenews-gambling-porn-social-only/hosts",
    "https://raw.githubusercontent.com/hectorm/hmirror/master/data/turkish-ad-hosts/list.txt",
    "https://raw.githubusercontent.com/DandelionSprout/adfilt/master/NorwegianExperimentalList%20alternate%20versions/DandelionSproutsNorskeFiltreDomains.txt",
    "https://easylist-downloads.adblockplus.org/Liste_AR.txt",
    "https://easylist-downloads.adblockplus.org/bulgarian_list.txt",
    "https://easylist-downloads.adblockplus.org/easylistczechslovak.txt",
    "https://easylist-downloads.adblockplus.org/easylistgermany.txt",
    "https://easylist-downloads.adblockplus.org/liste_fr.txt",
    "https://easylist-downloads.adblockplus.org/israellist.txt",
    "https://easylist-downloads.adblockplus.org/abpindo.txt",
    "https://easylist-downloads.adblockplus.org/easylistitaly.txt",
    "https://easylist-downloads.adblockplus.org/koreanlist.txt",
    "https://easylist-downloads.adblockplus.org/latvianlist.txt",
    "https://easylist-downloads.adblockplus.org/easylistlithuania.txt",
    "https://easylist-downloads.adblockplus.org/easylistpolish.txt",
    "https://easylist-downloads.adblockplus.org/easylistportuguese.txt",
    "https://easylist-downloads.adblockplus.org/advblock.txt",
    "https://easylist-downloads.adblockplus.org/easylistspanish.txt",
    "https://raw.githubusercontent.com/FilteringDev/filterslists-KO/refs/heads/master/filterslists/adblocking/filters-share/1st_domains.txt",
    "https://raw.githubusercontent.com/FilteringDev/filterslists-KO/refs/heads/master/filterslists/adblocking/filters-share/3rd_domains.txt",
    "https://raw.githubusercontent.com/AdguardTeam/FiltersRegistry/master/filters/filter_7_Japanese/filter.txt",
    "https://raw.githubusercontent.com/tofukko/filter/master/Adblock_Plus_list.txt",
    "https://easylist-downloads.adblockplus.org/ruadlist.txt",
    "https://raw.githubusercontent.com/AdguardTeam/FiltersRegistry/master/filters/filter_1_Russian/filter.txt",
    "https://raw.githubusercontent.com/AdguardTeam/FiltersRegistry/master/filters/filter_16_French/filter.txt",
    "https://raw.githubusercontent.com/AdguardTeam/FiltersRegistry/master/filters/filter_6_German/filter.txt",
    "https://raw.githubusercontent.com/AdguardTeam/FiltersRegistry/master/filters/filter_9_Spanish/filter.txt",
    "https://raw.githubusercontent.com/AdguardTeam/FiltersRegistry/master/filters/filter_13_Turkish/filter.txt",
    "https://raw.githubusercontent.com/omerdduran/turk-adfilter/main/turk-adfilter.txt",
    "https://raw.githubusercontent.com/remad0/TurkHosts404/refs/heads/main/dns-blocklists/adblock.txt",
    "https://raw.githubusercontent.com/symbuzzer/Turkish-Ad-Hosts/main/hosts",
    "https://raw.githubusercontent.com/AdguardTeam/FiltersRegistry/master/filters/filter_23_Ukrainian/filter.txt",
    "https://raw.githubusercontent.com/ukrainianfilters/lists/main/ads/ads.txt",
    "https://raw.githubusercontent.com/ukrainianfilters/lists/main/combined/combined.txt",
    "https://raw.githubusercontent.com/ukrainianfilters/lists/main/privacy/privacy.txt",
    "https://easylist-downloads.adblockplus.org/indianlist.txt",
    "https://raw.githubusercontent.com/brave/adblock-lists/refs/heads/master/custom/is.txt",
    "https://raw.githubusercontent.com/DandelionSprout/Swedish-List-for-Adblock-Plus/refs/heads/main/Swedish%20List%20for%20All-Nordic.txt",
    "https://raw.githubusercontent.com/DandelionSprout/adfilt/master/NorwegianExperimentalList%20alternate%20versions/NordicFiltersABP-Inclusion.txt",
    "https://raw.githubusercontent.com/Hakame-kun/uBlock-Filters-Indonesia/master/uBlock%20Indo/ubindo.txt",
    "https://raw.githubusercontent.com/easylist-thailand/easylist-thailand/master/subscription/easylist-thailand.txt",
    "https://raw.githubusercontent.com/bigdargon/hostsVN/master/filters/adservers.txt",
    "https://raw.githubusercontent.com/bigdargon/hostsVN/master/option/hosts-VN",
    "https://codeberg.org/KhodeKiaa/PersianBlocker/raw/branch/main/PersianBlocker.txt",
    "https://raw.githubusercontent.com/MasterKia/PersianBlocker/main/PersianBlockerAds-Hosts.txt",
    "https://raw.githubusercontent.com/MasterKia/PersianBlocker/main/PersianBlockerHosts.txt",
    "https://raw.githubusercontent.com/MasterKia/PersianBlocker/main/PersianBlockerTrackers-Hosts.txt",
    "https://raw.githubusercontent.com/AdguardTeam/FiltersRegistry/master/filters/filter_8_Dutch/filter.txt",
    "https://cdn.jsdelivr.net/gh/hufilter/hufilter@gh-pages/hufilter.txt",
    "https://raw.githubusercontent.com/DandelionSprout/adfilt/master/SerboCroatianList.txt",
    "https://raw.githubusercontent.com/DeepSpaceHarbor/Macedonian-adBlock-Filters/refs/heads/master/Filters",
    "https://raw.githubusercontent.com/betterwebleon/slovenian-list/refs/heads/master/filters.txt",
    "https://www.zoso.ro/pages/rolist.txt",
    "https://www.zoso.ro/pages/rolist2.txt",
    "https://www.void.gr/kargig/void-gr-filters.txt",
    "https://raw.githubusercontent.com/andromedarabbit/List-KR/master/filter.txt",
    "https://raw.githubusercontent.com/unchartedsky/adguard-kr/master/adguard-kr.txt",
    "https://raw.githubusercontent.com/Yuki2718/adblock/master/japanese/jp-filters.txt",
    "https://raw.githubusercontent.com/Yuki2718/adblock/master/japanese/jp-paranoid.txt",
    "https://raw.githubusercontent.com/Yuki2718/adblock/master/japanese/jp-annoyances.txt",
    "https://raw.githubusercontent.com/bkrcrc/turk-adlist/master/hosts",
    "https://raw.githubusercontent.com/MajkiIT/polish-ads-filter/master/polish-adblock-filters/adblock.txt",
    "https://raw.githubusercontent.com/olegwukr/polish-privacy-filters/master/adblock.txt",
    "https://raw.githubusercontent.com/tomasko126/easylistczechandslovak/master/filters.txt",
    "https://raw.githubusercontent.com/ConvolutionExpected/CZ-SK-hosts-file-to-block-trackers-and-ads/main/AdsAndTrackers",
    "https://raw.githubusercontent.com/ABPindo/indonesianadblockrules/master/subscriptions/domain.txt",
    "https://raw.githubusercontent.com/jakdev121/AMS2/master/pi_indo_ads.txt",
    "https://raw.githubusercontent.com/farrokhi/adblock-iran/master/filter.txt",
    "https://raw.githubusercontent.com/lassekongo83/Frellwits-filter-lists/master/Frellwits-Swedish-Filter.txt",
    "https://filters.hufilter.hu/hufilter-dns.txt",
    "https://raw.githubusercontent.com/kargig/greek-adblockplus-filter/master/void-gr-filters.txt",
    "https://raw.githubusercontent.com/hosts-file/BulgarianHostsFile/master/bhf.txt",
    "https://raw.githubusercontent.com/KokichaKolevTM/BG-Adblock-list/main/BG-Adblock-list.txt",
    "https://raw.githubusercontent.com/Ultimate-Hosts-Blacklist/Bad_JAV_Sites/master/domains.list",
    "https://lists.blocklist.de/lists/all.txt",
    "https://raw.githubusercontent.com/tongxin0520/AdFilterForAdGuard/refs/heads/main/KR_DNS_Filter.txt",
    "https://adguardteam.github.io/HostlistsRegistry/assets/filter_37.txt",
    "https://raw.githubusercontent.com/PolishFiltersTeam/KADhosts/master/KADhosts.txt",
    "https://dl.red.flag.domains/red.flag.domains.txt",
    "https://phish.co.za/latest/phishing-domains-ACTIVE.txt",
    "https://raw.githubusercontent.com/BlackJack8/iOSAdblockList/master/Regular%20Hosts.txt",
    "https://raw.githubusercontent.com/mitchellkrogza/Badd-Boyz-Hosts/master/hosts",
    "https://raw.githubusercontent.com/FadeMind/hosts.extras/master/UncheckyAds/hosts",
    "https://raw.githubusercontent.com/StevenBlack/hosts/master/data/add.Spam/hosts",
    "https://raw.githubusercontent.com/StevenBlack/hosts/master/data/add.Risk/hosts",
    "https://v.firebog.net/hosts/Prigent-Malware.txt",
    "https://v.firebog.net/hosts/Prigent-Crypto.txt",
    "https://v.firebog.net/hosts/Prigent-Ads.txt",
    "https://easylist.to/easylist/fanboy-social.txt",
    "https://filters.adtidy.org/windows/filters/4.txt",
    "https://raw.githubusercontent.com/mitchellkrogza/Top-Attacking-IP-Addresses-Against-Wordpress-Sites/master/wordpress-attacking-ips.txt",
    "https://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/malware",
    "https://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/Phishing-Angriffe",
    "https://blocklistproject.github.io/Lists/porn.txt",
    "https://blocklistproject.github.io/Lists/abuse.txt",
    "https://raw.githubusercontent.com/Dogino/Discord-Phishing-URLs/main/scam-urls.txt",
]

# 是否更新 README.md 和规则文件头部的数量统计
UPDATE_README = True
UPDATE_TOTAL_COUNT = True
README_FILE = "README.md"

# ==================== 核心逻辑 ====================
# 【适配修改】目标文件指向 Adblock-Rule-Collection 的核心输出文件
TARGET_FILES = ["ADBLOCK_RULE_COLLECTION.txt"]

def fetch_rules(url):
    """下载规则文件，去除注释后返回规则列表"""
    try:
        print(f"  ⏳ 下载: {url}")
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        return [
            line.split('!')[0].split('#')[0].strip()
            for line in resp.text.splitlines()
            if line.split('!')[0].split('#')[0].strip()
        ]
    except Exception as e:
        print(f"  ❌ 下载失败: {e}")
        return []

def extract_domain(rule):
    """从 AdGuard 规则中提取核心域名"""
    rule = rule.strip()
    if rule.startswith('@@||'):
        rule = rule[4:]
    elif rule.startswith('||'):
        rule = rule[2:]
    if '$' in rule:
        rule = rule.split('$')[0]
    if rule.endswith('^'):
        rule = rule[:-1]
    return rule.lower()

def is_rule_line(line):
    """判断是否为有效规则行（用于统计）"""
    s = line.strip()
    if not s or s.startswith('[Adblock') or s.startswith('!'):
        return False
    if s.startswith('#') and not s.startswith('##'):
        return False
    return True

def count_rules(lines):
    """统计有效规则行数"""
    return sum(1 for l in lines if is_rule_line(l))

def count_file(path):
    """统计文件中的有效规则数"""
    if not os.path.exists(path):
        return 0
    with open(path, 'r', encoding='utf-8') as f:
        # 【修复】原脚本此处直接传入文件对象，现修正为传入 readlines() 列表
        return count_rules(f.readlines())

def update_total_header(lines):
    """更新文件头部的 ! Total rules: 或 ! Total count:"""
    if not UPDATE_TOTAL_COUNT:
        return lines
    total = count_rules(lines)
    for i, line in enumerate(lines):
        if line.strip().startswith('! Total rules:') or line.strip().startswith('! Total count:'):
            prefix = "! Total rules:" if "! Total rules:" in line else "! Total count:"
            lines[i] = f'{prefix} {total}\n'
            break
    return lines

def update_readme():
    """更新 README.md 中的规则数量 (兼容 Adblock-Rule-Collection 格式)"""
    if not UPDATE_README or not os.path.exists(README_FILE):
        return
    
    total_count = count_file("ADBLOCK_RULE_COLLECTION.txt")
    
    with open(README_FILE, 'r', encoding='utf-8') as f:
        text = f.read()
    original = text
    
    # 【适配修改】兼容 Adblock-Rule-Collection 的 README 表格格式: | 📏 规则总数 | 893,686 条 |
    text = re.sub(r'(\| 📏 规则总数 \| )([\d,]+)( 条 \|)', rf'\g<1>{total_count:,}\g<3>', text)
    # 兼容 HyperADRules 的文本格式: 拦截规则数量: 12345
    text = re.sub(r'(拦截规则数量[^0-9]*?)\d+', rf'\g<1>{total_count}', text)
    
    if text != original:
        with open(README_FILE, 'w', encoding='utf-8') as f:
            f.write(text)
        print("\n📝 已更新 README.md 规则数量")

def process_file(filename, exclude_domains, exclude_exact):
    """处理单个规则文件：剔除 + 更新统计"""
    if not os.path.exists(filename):
        print(f"⚠️ 跳过 {filename}（不存在）")
        return
    
    print(f"\n⚙️ 处理: {filename}")
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    filtered, removed = [], 0
    in_block = False
    
    for line in lines:
        # 跳过/清理残留的自定义注入块（保证幂等，清理旧版脚本留下的痕迹）
        if '! >>>>> CUSTOM_INJECT_START <<<<<' in line:
            in_block = True
            continue
        if '! >>>>> CUSTOM_INJECT_END <<<<<' in line:
            in_block = False
            continue
        if in_block:
            continue
            
        clean = line.split('!')[0].split('#')[0].strip()
        if not clean:
            filtered.append(line)
            continue
            
        # 匹配剔除：精确匹配 / AdGuard域名 / Hosts格式 / 裸域名
        if clean in exclude_exact:
            removed += 1
            continue
        if clean.startswith(('||', '@@||')):
            if extract_domain(clean) in exclude_domains:
                removed += 1
                continue
        elif clean.startswith(('0.0.0.0', '127.0.0.1')):
            parts = clean.split()
            if len(parts) > 1 and parts[1].lower() in exclude_domains:
                removed += 1
                continue
        elif '/' not in clean and '.' in clean:
            if clean.lower() in exclude_domains:
                removed += 1
                continue
                
        filtered.append(line)
        
    # 更新统计并写入
    filtered = update_total_header(filtered)
    with open(filename, 'w', encoding='utf-8') as f:
        f.writelines(filtered)
    print(f"  ✅ 完成 | 🗑️ 剔除 {removed} 条规则")

def main():
    print("🚀 开始执行规则剔除与统计更新...")
    
    # 解析排除列表
    exclude_domains, exclude_exact = set(), set()
    if EXCLUDE_SOURCES:
        print("\n🔍 解析排除列表...")
        for url in EXCLUDE_SOURCES:
            for rule in fetch_rules(url):
                if rule.startswith(('||', '@@||')):
                    exclude_domains.add(extract_domain(rule))
                elif rule.startswith(('0.0.0.0', '127.0.0.1')):
                    parts = rule.split()
                    if len(parts) > 1:
                        exclude_domains.add(parts[1].lower())
                else:
                    if '/' not in rule and '.' in rule:
                        exclude_domains.add(rule.lower())
                    exclude_exact.add(rule)
        print(f"  📊 提取 {len(exclude_domains)} 个域名, {len(exclude_exact)} 条精确规则")
    else:
        print("⚠️ 未配置需要剔除的上游源 (EXCLUDE_SOURCES)")
        
    # 处理目标文件
    for f in TARGET_FILES:
        process_file(f, exclude_domains, exclude_exact)
        
    # 更新 README
    update_readme()
    
    print("\n🎉 剔除与统计更新完成！")

if __name__ == "__main__":
    main()
