<!-- 居中的大标题 -->
<h1 align="center" style="font-size: 100px; margin-bottom: 40px;">Adblock-Rule-Collection</h1>
<!-- 居中的副标题 -->
<h2 align="center" style="font-size: 30px; margin-bottom: 40px;">一个收集hosts规则，进行转化、合并、去重并剔除无效链接的广告过滤器，兼容常见的广告过滤应用程序（如Adblock Plus、AdGuard 等），每2小时更新一次，确保即时同步上游减少误杀。采用cron-job确保每2小时更新 </h2>

<!-- 🔽 脚本会自动替换此标记之间的内容 🔽 -->
<!-- AUTO_STATUS_START -->
<h3 align="center">📊 仓库状态</h3>

| 项目 | 状态 |
| --- | --- |
| 🕐 最后更新时间 | 2026-10-03 22:28:36 (UTC+8) |
| 📏 规则总数 | 416,726 条 |
| 🔄 更新频率 | 每 2 小时自动更新 |
| 📦 文件格式 | ABP 兼容格式 (支持通配符/静默拦截，已剔除正则) |
<!-- AUTO_STATUS_END -->
<!-- 🔼 脚本会自动替换此标记之间的内容 🔼 -->

一、关于Adblock-Rule-Collection，本仓库是一个收集hosts规则，进行转化、合并、去重并剔除无效链接的广告过滤器，兼容常见的广告过滤应用程序（如Adblock Plus、AdGuard 等），每2小时更新一次，确保即时同步上游减少误杀 。你可以在Adblock_Rule_Generator.py中修改urls列表来添加自定义的双栈 Hosts 上游源
<hr>
警告:本过滤器订阅有可能破坏某些网站的功能，使用前请斟酌考虑，如有误杀请积极向上游 Hosts 源反馈，本仓库仅提供双栈 Hosts 解析、转化、去重、合并功能
<hr>
<br>

二、本仓库使用方式如下：

1、订阅地址

| 过滤器类型 | 订阅地址 |
| --- | --- |
| 双栈 Hosts 转化 ABP 规则 | [Github](https://qirui-bot.github.io/Adblock-Rule-Collection/ADBLOCK_RULE_COLLECTION.txt) |

2、下载到本地
从 上游源 下载过滤器文件进行本地导入。每 2 小时自动发布一次。

三、适用范围
适用于 AdGuard、Adblock Plus 等各类符合 Adblock Plus 语法的广告拦截程序以及 DNS 服务器
<br>

四、规则来源
本仓库从以下双栈 Hosts 源提取域名并转化为 ABP 格式：

<!-- 🔽 脚本会自动替换此标记之间的内容 🔽 -->
<!-- AUTO_UPSTREAM_START -->
<details>
<summary>📋 点击展开完整上游源列表（共 58 个）</summary>

| 序号 | 上游源 | 链接 |
| --- | --- | --- |
| 1 | `Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist/master/hosts/hosts0` | [链接](https://raw.githubusercontent.com/Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist/master/hosts/hosts0) |
| 2 | `Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist/master/hosts/hosts1` | [链接](https://raw.githubusercontent.com/Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist/master/hosts/hosts1) |
| 3 | `Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist/master/hosts/hosts2` | [链接](https://raw.githubusercontent.com/Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist/master/hosts/hosts2) |
| 4 | `Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist/master/hosts/hosts3` | [链接](https://raw.githubusercontent.com/Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist/master/hosts/hosts3) |
| 5 | `Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist/master/hosts/hosts4` | [链接](https://raw.githubusercontent.com/Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist/master/hosts/hosts4) |
| 6 | `Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist/master/hosts/hosts5` | [链接](https://raw.githubusercontent.com/Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist/master/hosts/hosts5) |
| 7 | `hululu1068/AdGuard-Rule/main/rule/all.txt` | [链接](https://raw.githubusercontent.com/hululu1068/AdGuard-Rule/main/rule/all.txt) |
| 8 | `fynks/blocklists/main/blocklists/personal.txt` | [链接](https://raw.githubusercontent.com/fynks/blocklists/main/blocklists/personal.txt) |
| 9 | `elliottophellia/adlist/main/hosts` | [链接](https://raw.githubusercontent.com/elliottophellia/adlist/main/hosts) |
| 10 | `bongochong/CombinedPrivacyBlockLists/master/cpbl-abp-list.txt` | [链接](https://raw.githubusercontent.com/bongochong/CombinedPrivacyBlockLists/master/cpbl-abp-list.txt) |
| 11 | `rentianyu/Ad-set-hosts/master/adguard` | [链接](https://raw.githubusercontent.com/rentianyu/Ad-set-hosts/master/adguard) |
| 12 | `10007_auto/adb.txt` | [链接](https://lingeringsound.github.io/10007_auto/adb.txt) |
| 13 | `hosts_adblock.txt` | [链接](https://hblock.molinero.dev/hosts_adblock.txt) |
| 14 | `vip592850-blip/ros-routing-rules/main/reject_adlist.txt` | [链接](https://raw.githubusercontent.com/vip592850-blip/ros-routing-rules/main/reject_adlist.txt) |
| 15 | `2Gardon/SM-Ad-FuckU-hosts/master/SMAdHosts` | [链接](https://raw.githubusercontent.com/2Gardon/SM-Ad-FuckU-hosts/master/SMAdHosts) |
| 16 | `adblocker` | [链接](https://neodev.team/adblocker) |
| 17 | `Sereinfy/Adrules/main/rules/adblockdns.txt` | [链接](https://raw.githubusercontent.com/Sereinfy/Adrules/main/rules/adblockdns.txt) |
| 18 | `SpiralGlobe6864/BAN-PCDN-ADGUARD/main/PCDN-BAN-AdGuard.txt` | [链接](https://raw.githubusercontent.com/SpiralGlobe6864/BAN-PCDN-ADGUARD/main/PCDN-BAN-AdGuard.txt) |
| 19 | `hagezi/dns-blocklists/main/adblock/doh-vpn-proxy-bypass.txt` | [链接](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/doh-vpn-proxy-bypass.txt) |
| 20 | `hagezi/dns-blocklists/main/adblock/pro.txt` | [链接](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/pro.txt) |
| 21 | `hagezi/dns-blocklists/main/adblock/popupads.txt` | [链接](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/popupads.txt) |
| 22 | `hagezi/dns-blocklists/main/adblock/dyndns.txt` | [链接](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/dyndns.txt) |
| 23 | `DickaHandsome/My-Ads-Rule/main/MyRule.txt` | [链接](https://raw.githubusercontent.com/DickaHandsome/My-Ads-Rule/main/MyRule.txt) |
| 24 | `HyperADRules/dns.txt` | [链接](https://qirui-bot.github.io/HyperADRules/dns.txt) |
| 25 | `Menghuibanxian/AdguardHome/main/pure%20black.txt` | [链接](https://raw.githubusercontent.com/Menghuibanxian/AdguardHome/main/pure%20black.txt) |
| 26 | `HyperADRules/allow.txt` | [链接](https://qirui-bot.github.io/HyperADRules/allow.txt) |
| 27 | `daboq11/ban-pcdn/main/Ban-pcdn.txt` | [链接](https://raw.githubusercontent.com/daboq11/ban-pcdn/main/Ban-pcdn.txt) |
| 28 | `lisrain/adguard-home-config/master/output/filters.txt` | [链接](https://raw.githubusercontent.com/lisrain/adguard-home-config/master/output/filters.txt) |
| 29 | `cbuijs/adblocks/main/ultimate.adblock.txt` | [链接](https://raw.githubusercontent.com/cbuijs/adblocks/main/ultimate.adblock.txt) |
| 30 | `smdx/AdGHome_Filter_List/main/AdGHome-PCDN.txt` | [链接](https://raw.githubusercontent.com/smdx/AdGHome_Filter_List/main/AdGHome-PCDN.txt) |
| 31 | `ammnt/DeadEnd/main/filter.txt` | [链接](https://raw.githubusercontent.com/ammnt/DeadEnd/main/filter.txt) |
| 32 | `1Hosts/Lite/adblock.txt` | [链接](https://badmojr.github.io/1Hosts/Lite/adblock.txt) |
| 33 | `afwfv/DD-AD/release/easylist.txt` | [链接](https://raw.githubusercontent.com/afwfv/DD-AD/release/easylist.txt) |
| 34 | `hl2guide/curated-adblock-lists/main/lists/trackers.txt` | [链接](https://raw.githubusercontent.com/hl2guide/curated-adblock-lists/main/lists/trackers.txt) |
| 35 | `qq5460168/666/master/dns.txt` | [链接](https://raw.githubusercontent.com/qq5460168/666/master/dns.txt) |
| 36 | `hagezi/dns-blocklists/main/adblock/tif.mini.txt` | [链接](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/tif.mini.txt) |
| 37 | `hagezi/dns-blocklists/main/adblock/native.huawei.txt` | [链接](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.huawei.txt) |
| 38 | `hagezi/dns-blocklists/main/adblock/native.xiaomi.txt` | [链接](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.xiaomi.txt) |
| 39 | `hagezi/dns-blocklists/main/adblock/native.oppo-realme.txt` | [链接](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.oppo-realme.txt) |
| 40 | `hagezi/dns-blocklists/main/adblock/native.vivo.txt` | [链接](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.vivo.txt) |
| 41 | `hagezi/dns-blocklists/main/adblock/native.tiktok.extended.txt` | [链接](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.tiktok.extended.txt) |
| 42 | `hagezi/dns-blocklists/main/adblock/native.winoffice.txt` | [链接](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.winoffice.txt) |
| 43 | `sutchan/DNS_Shield/main/public/adguard.txt` | [链接](https://raw.githubusercontent.com/sutchan/DNS_Shield/main/public/adguard.txt) |
| 44 | `ph00lt0/blocklist/master/blocklist.txt` | [链接](https://raw.githubusercontent.com/ph00lt0/blocklist/master/blocklist.txt) |
| 45 | `dns.txt` | [链接](https://adrules.top/dns.txt) |
| 46 | `guandasheng/adguardhome/main/rule/all.txt` | [链接](https://raw.githubusercontent.com/guandasheng/adguardhome/main/rule/all.txt) |
| 47 | `tomcat10005/adguard-/main/rule/all.txt` | [链接](https://raw.githubusercontent.com/tomcat10005/adguard-/main/rule/all.txt) |
| 48 | `bad-hosts/bad-hosts-abp` | [链接](https://dl.cenk.app/bad-hosts/bad-hosts-abp) |
| 49 | `LJGZ/all.txt` | [链接](https://wansheng8.github.io/LJGZ/all.txt) |
| 50 | `H-i-H/AdGuard-Home-Rules/main/Release/combined-rules.txt` | [链接](https://raw.githubusercontent.com/H-i-H/AdGuard-Home-Rules/main/Release/combined-rules.txt) |
| 51 | `hosts/hosts` | [链接](http://sbc.io/hosts/hosts) |
| 52 | `quidsup/notrack-blocklists/-/raw/master/trackers.hosts` | [链接](https://gitlab.com/quidsup/notrack-blocklists/-/raw/master/trackers.hosts) |
| 53 | `KnightmareVIIVIIXC/AIO-Firebog-Blocklists/main/lists/aiofireboggreen.txt` | [链接](https://raw.githubusercontent.com/KnightmareVIIVIIXC/AIO-Firebog-Blocklists/main/lists/aiofireboggreen.txt) |
| 54 | `yokoffing/filterlists/main/privacy_essentials.txt` | [链接](https://raw.githubusercontent.com/yokoffing/filterlists/main/privacy_essentials.txt) |
| 55 | `REIJI007/Adblock-Rule-Collection/main/ADBLOCK_RULE_COLLECTION_DNS.txt` | [链接](https://raw.githubusercontent.com/REIJI007/Adblock-Rule-Collection/main/ADBLOCK_RULE_COLLECTION_DNS.txt) |
| 56 | `nsfw.oisd.nl` | [链接](https://nsfw.oisd.nl/) |
| 57 | `insoxin/domestic-ad-hosts/main/hosts` | [链接](https://raw.githubusercontent.com/insoxin/domestic-ad-hosts/main/hosts) |
| 58 | `VoidInTheShell/pcdn-block-list/master/pcdn_block_adh.txt` | [链接](https://raw.githubusercontent.com/VoidInTheShell/pcdn-block-list/master/pcdn_block_adh.txt) |
</details>
<!-- AUTO_UPSTREAM_END -->
<!-- 🔼 脚本会自动替换此标记之间的内容 🔼 -->

<br>
<br>

LICENSE
CC-BY-NC-SA 4.0 License
GPL-3.0 License
