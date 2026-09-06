<!-- 居中的大标题 -->
<h1 align="center" style="font-size: 100px; margin-bottom: 40px;">Adblock-Rule-Collection</h1>
<!-- 居中的副标题 -->
<h2 align="center" style="font-size: 30px; margin-bottom: 40px;">一个收集hosts规则，进行转化、合并、去重并剔除无效链接的广告过滤器，兼容常见的广告过滤应用程序（如Adblock Plus、AdGuard 等），每6小时更新一次，确保即时同步上游减少误杀 </h2>

<!-- 🔽 脚本会自动替换此标记之间的内容 🔽 -->
<!-- AUTO_STATUS_START -->
<h3 align="center">📊 仓库状态</h3>

| 项目 | 状态 |
| --- | --- |
| 🕐 最后更新时间 | 2026-09-07 12:59:51 (UTC+8) |
| 📏 规则总数 | 1,018,336 条 |
| 🔄 更新频率 | 每 6 小时自动更新 |
| 📦 文件格式 | ABP 兼容格式 (支持通配符/静默拦截，已剔除正则) |

<!-- AUTO_STATUS_END -->
<!-- 🔼 脚本会自动替换此标记之间的内容 🔼 -->

一、关于Adblock-Rule-Collection，本仓库是一个收集hosts规则，进行转化、合并、去重并剔除无效链接的广告过滤器，兼容常见的广告过滤应用程序（如Adblock Plus、AdGuard 等），每6小时更新一次，确保即时同步上游减少误杀 。你可以在Adblock_Rule_Generator.py中修改urls列表来添加自定义的双栈 Hosts 上游源
<hr>
警告:本过滤器订阅有可能破坏某些网站的功能，使用前请斟酌考虑，如有误杀请积极向上游 Hosts 源反馈，本仓库仅提供双栈 Hosts 解析、转化、去重、合并功能
<hr>
<br>

二、本仓库使用方式如下：

1、订阅地址

| 过滤器类型 | 订阅地址 |
| --- | --- |
| 双栈 Hosts 转化 ABP 规则 | [Github](https://raw.githubusercontent.com/qirui-bot/Adblock-Rule-Collection/main/ADBLOCK_RULE_COLLECTION.txt) |

2、下载到本地
从 上游源 下载过滤器文件进行本地导入。每 6 小时自动发布一次。

三、适用范围
适用于 AdGuard、Adblock Plus 等各类符合 Adblock Plus 语法的广告拦截程序以及 DNS 服务器
<br>

四、规则来源
本仓库从以下双栈 Hosts 源提取域名并转化为 ABP 格式：

<!-- 🔽 脚本会自动替换此标记之间的内容 🔽 -->
<!-- AUTO_UPSTREAM_START -->
<details>
<summary>📋 点击展开完整上游源列表（共 43 个）</summary>

| 序号 | 上游源 | 链接 |
| --- | --- | --- |
| 1 | `Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist` | [链接](https://raw.githubusercontent.com/Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist/master/hosts/hosts0) |
| 2 | `Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist` | [链接](https://raw.githubusercontent.com/Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist/master/hosts/hosts1) |
| 3 | `Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist` | [链接](https://raw.githubusercontent.com/Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist/master/hosts/hosts2) |
| 4 | `Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist` | [链接](https://raw.githubusercontent.com/Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist/master/hosts/hosts3) |
| 5 | `Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist` | [链接](https://raw.githubusercontent.com/Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist/master/hosts/hosts4) |
| 6 | `Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist` | [链接](https://raw.githubusercontent.com/Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist/master/hosts/hosts5) |
| 7 | `wansheng8/GZ` | [链接](https://raw.githubusercontent.com/wansheng8/GZ/main/dist/adblock_collection_full.txt) |
| 8 | `fynks/blocklists` | [链接](https://raw.githubusercontent.com/fynks/blocklists/main/blocklists/personal.txt) |
| 9 | `elliottophellia/adlist` | [链接](https://raw.githubusercontent.com/elliottophellia/adlist/main/hosts) |
| 10 | `bongochong/CombinedPrivacyBlockLists` | [链接](https://raw.githubusercontent.com/bongochong/CombinedPrivacyBlockLists/master/cpbl-abp-list.txt) |
| 11 | `badmojr/1Hosts` | [链接](https://raw.githubusercontent.com/badmojr/1Hosts/master/Lite/adblock.txt) |
| 12 | `rentianyu/Ad-set-hosts` | [链接](https://raw.githubusercontent.com/rentianyu/Ad-set-hosts/master/adguard) |
| 13 | `lingeringsound/10007_auto` | [链接](https://raw.githubusercontent.com/lingeringsound/10007_auto/master/adb.txt) |
| 14 | `StevenBlack/hosts` | [链接](https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts) |
| 15 | `vip592850-blip/ros-routing-rules` | [链接](https://raw.githubusercontent.com/vip592850-blip/ros-routing-rules/main/reject_adlist.txt) |
| 16 | `2Gardon/SM-Ad-FuckU-hosts` | [链接](https://raw.githubusercontent.com/2Gardon/SM-Ad-FuckU-hosts/master/SMAdHosts) |
| 17 | `neodevpro/neodevhost` | [链接](https://raw.githubusercontent.com/neodevpro/neodevhost/master/adblocker) |
| 18 | `Sereinfy/Adrules` | [链接](https://raw.githubusercontent.com/Sereinfy/Adrules/main/rules/adblockdns.txt) |
| 19 | `SpiralGlobe6864/BAN-PCDN-ADGUARD` | [链接](https://raw.githubusercontent.com/SpiralGlobe6864/BAN-PCDN-ADGUARD/main/PCDN-BAN-AdGuard.txt) |
| 20 | `hagezi/dns-blocklists` | [链接](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/doh-vpn-proxy-bypass.txt) |
| 21 | `hagezi/dns-blocklists` | [链接](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/pro.txt) |
| 22 | `DickaHandsome/My-Ads-Rule` | [链接](https://raw.githubusercontent.com/DickaHandsome/My-Ads-Rule/main/MyRule.txt) |
| 23 | `qirui-bot/HyperADRules` | [链接](https://raw.githubusercontent.com/qirui-bot/HyperADRules/master/dns.txt) |
| 24 | `Menghuibanxian/AdguardHome` | [链接](https://raw.githubusercontent.com/Menghuibanxian/AdguardHome/main/Black.txt) |
| 25 | `qirui-bot/HyperADRules` | [链接](https://raw.githubusercontent.com/qirui-bot/HyperADRules/master/allow.txt) |
| 26 | `https:/` | [链接](https://hblock.molinero.dev/hosts_adblock.txt) |
| 27 | `https:/` | [链接](https://gitlab.com/quidsup/notrack-blocklists/-/raw/master/trackers.hosts) |
| 28 | `H-i-H/AdGuard-Home-Rules` | [链接](https://raw.githubusercontent.com/H-i-H/AdGuard-Home-Rules/main/Release/combined-rules.txt) |
| 29 | `daboq11/ban-pcdn` | [链接](https://raw.githubusercontent.com/daboq11/ban-pcdn/main/Ban-pcdn.txt) |
| 30 | `lisrain/adguard-home-config` | [链接](https://raw.githubusercontent.com/lisrain/adguard-home-config/master/output/filters.txt) |
| 31 | `hululu1068/AdGuard-Rule` | [链接](https://raw.githubusercontent.com/hululu1068/AdGuard-Rule/main/rule/all.txt) |
| 32 | `cbuijs/adblocks` | [链接](https://raw.githubusercontent.com/cbuijs/adblocks/main/ultimate.adblock.txt) |
| 33 | `smdx/AdGHome_Filter_List` | [链接](https://raw.githubusercontent.com/smdx/AdGHome_Filter_List/main/AdGHome-PCDN.txt) |
| 34 | `ammnt/DeadEnd` | [链接](https://raw.githubusercontent.com/ammnt/DeadEnd/main/filter.txt) |
| 35 | `afwfv/DD-AD` | [链接](https://raw.githubusercontent.com/afwfv/DD-AD/release/easylist.txt) |
| 36 | `hl2guide/curated-adblock-lists` | [链接](https://raw.githubusercontent.com/hl2guide/curated-adblock-lists/main/lists/trackers.txt) |
| 37 | `qq5460168/666` | [链接](https://raw.githubusercontent.com/qq5460168/666/master/dns.txt) |
| 38 | `hagezi/dns-blocklists` | [链接](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/tif.mini.txt) |
| 39 | `hagezi/dns-blocklists` | [链接](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/popupads.txt) |
| 40 | `hagezi/dns-blocklists` | [链接](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/dyndns.txt) |
| 41 | `https:/` | [链接](https://ascopes.github.io/dns-blocklist/blocklist.txt) |
| 42 | `ppfeufer/adguard-filter-list` | [链接](https://raw.githubusercontent.com/ppfeufer/adguard-filter-list/master/blocklist) |
| 43 | `siankatabg/FuFu-AdGuard-blacklist` | [链接](https://raw.githubusercontent.com/siankatabg/FuFu-AdGuard-blacklist/master/fufu-adguard-blacklist.txt) |

</details>
<!-- AUTO_UPSTREAM_END -->
<!-- 🔼 脚本会自动替换此标记之间的内容 🔼 -->

<br>
<br>

LICENSE
CC-BY-NC-SA 4.0 License
GPL-3.0 License
