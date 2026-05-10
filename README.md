# DNS

一个用于批量查询域名解析结果的小工具（最初版本很简单，这里做了功能增强）。

## 功能

- 从文本文件读取域名（每行一个）
- 自动忽略空行与 `#` 注释
- 允许输入 `http://example.com/path` 或 `example.com:443`，会自动提取域名
- 返回：
  - 所有去重后的 IP
  - 解析失败的域名
  - 每个域名的详细结果
  - 汇总统计（总数、成功、失败、唯一 IP 数）
- 提供 CLI，支持文本输出或 JSON 输出

## Python API

```python
from dns import dns, dns_detailed

ips, failed = dns("domains.txt")

ips, failed, results, summary = dns_detailed("domains.txt")
```

## CLI 用法

```bash
python dns.py domains.txt
python dns.py domains.txt --json
```

## 输入示例

`domains.txt`:

```text
# 注释行
example.com
https://openai.com/research
github.com:443
8.8.8.8
invalid-domain.local
```
