<!-- 居中的大标题 -->
<h1 align="center" style="font-size: 100px; margin-bottom: 40px;">Adblock-Rule-Collection</h1>
<!-- 居中的副标题 -->
<h2 align="center" style="font-size: 30px; margin-bottom: 40px;">一个收集hosts规则，进行转化、合并、去重并剔除无效链接的广告过滤器，兼容常见的广告过滤应用程序（如Adblock Plus、AdGuard 等），每3小时更新一次，确保即时同步上游减少误杀 </h2>

<!-- 🔽 脚本会自动替换此标记之间的内容 🔽 -->
<!-- AUTO_STATUS_START -->
<h3 align="center">📊 仓库状态</h3>

| 项目 | 状态 |
| --- | --- |
| 🕐 最后更新时间 | 2026-07-24 22:23:54 (UTC+8) |
| 📏 规则总数 | 861,673 条 |
| 🔄 更新频率 | 每 3 小时自动更新 |
| 📦 文件格式 | ABP 兼容格式 (双栈 Hosts 转化 + 后缀树深度去重) |
<!-- AUTO_STATUS_END -->
<!-- 🔼 脚本会自动替换此标记之间的内容 🔼 -->

一、关于Adblock-Rule-Collection，本仓库是一个收集hosts规则，进行转化、合并、去重并剔除无效链接的广告过滤器，兼容常见的广告过滤应用程序（如Adblock Plus、AdGuard 等），每3小时更新一次，确保即时同步上游减少误杀 。你可以在Adblock_Rule_Generator.py中修改urls列表来添加自定义的双栈 Hosts 上游源
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
从 上游源 下载过滤器文件进行本地导入。每 3 小时自动发布一次。

三、适用范围
适用于 AdGuard、Adblock Plus 等各类符合 Adblock Plus 语法的广告拦截程序以及 DNS 服务器
<br>

四、规则来源
本仓库从以下双栈 Hosts 源提取域名并转化为 ABP 格式：

<!-- 🔽 脚本会自动替换此标记之间的内容 🔽 -->
<!-- AUTO_UPSTREAM_START -->
<details>
<summary>📋 点击展开完整上游源列表（共 20 个）</summary>

| 序号 | 上游源 | 链接 |
| --- | --- | --- |
| 1 | `Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist/hosts/hosts0` | [链接](https://raw.githubusercontent.com/Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist/master/hosts/hosts0) |
| 2 | `Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist/hosts/hosts1` | [链接](https://raw.githubusercontent.com/Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist/master/hosts/hosts1) |
| 3 | `Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist/hosts/hosts2` | [链接](https://raw.githubusercontent.com/Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist/master/hosts/hosts2) |
| 4 | `Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist/hosts/hosts3` | [链接](https://raw.githubusercontent.com/Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist/master/hosts/hosts3) |
| 5 | `Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist/hosts/hosts4` | [链接](https://raw.githubusercontent.com/Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist/master/hosts/hosts4) |
| 6 | `Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist/hosts/hosts5` | [链接](https://raw.githubusercontent.com/Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist/master/hosts/hosts5) |
| 7 | `wansheng8/adblock/rules/outputs/hosts.txt` | [链接](https://raw.githubusercontent.com/wansheng8/adblock/main/rules/outputs/hosts.txt) |
| 8 | `fynks/blocklists/blocklists/personal.txt` | [链接](https://raw.githubusercontent.com/fynks/blocklists/main/blocklists/personal.txt) |
| 9 | `elliottophellia/adlist/hosts` | [链接](https://raw.githubusercontent.com/elliottophellia/adlist/main/hosts) |
| 10 | `bongochong/CombinedPrivacyBlockLists/newhosts-final.hosts` | [链接](https://raw.githubusercontent.com/bongochong/CombinedPrivacyBlockLists/master/newhosts-final.hosts) |
| 11 | `hagezi/dns-blocklists/hosts/pro.txt` | [链接](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/hosts/pro.txt) |
| 12 | `hagezi/dns-blocklists/hosts/doh.txt` | [链接](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/hosts/doh.txt) |
| 13 | `badmojr/1Hosts/Lite/hosts.txt` | [链接](https://raw.githubusercontent.com/badmojr/1Hosts/master/Lite/hosts.txt) |
| 14 | `rentianyu/Ad-set-hosts/hosts` | [链接](https://raw.githubusercontent.com/rentianyu/Ad-set-hosts/master/hosts) |
| 15 | `110789/anti-ad-hosts/anti-ad-hosts.txt` | [链接](https://raw.githubusercontent.com/110789/anti-ad-hosts/main/anti-ad-hosts.txt) |
| 16 | `qdqqd/add-hosts/addhosts.txt` | [链接](https://raw.githubusercontent.com/qdqqd/add-hosts/main/addhosts.txt) |
| 17 | `vip592850-blip/ros-routing-rules/reject_adlist.txt` | [链接](https://raw.githubusercontent.com/vip592850-blip/ros-routing-rules/main/reject_adlist.txt) |
| 18 | `217heidai/adblockfilters/rules/adblockhosts.txt` | [链接](https://raw.githubusercontent.com/217heidai/adblockfilters/main/rules/adblockhosts.txt) |
| 19 | `neodevpro/neodevhost/host` | [链接](https://raw.githubusercontent.com/neodevpro/neodevhost/master/host) |
| 20 | `Sereinfy/Adrules/rules/adblockhosts.txt` | [链接](https://raw.githubusercontent.com/Sereinfy/Adrules/main/rules/adblockhosts.txt) |
</details>
<!-- AUTO_UPSTREAM_END -->
<!-- 🔼 脚本会自动替换此标记之间的内容 🔼 -->

<br>
<br>
LICENSE

CC-BY-NC-SA 4.0 License

GPL-3.0 License
