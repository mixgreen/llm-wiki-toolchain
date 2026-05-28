# iCloud Dataless 文件死锁 — 诊断与修复

## 现象

对 iCloud 目录中（`~/Library/Mobile Documents/iCloud~md~obsidian/Documents/`）的 `.md` 文件调用 `open()` 或 `pathlib.read_text()` 时抛出：

```
OSError: [Errno 11] Resource deadlock avoided
```

- `stat` 和 `os.path.getsize()` 报告正常文件大小
- 文件在 `find` / `ls` 中可见
- 但实际数据块未本地化（dataless / purgeable 状态）

## 原因

iCloud Drive 的"按需下载"机制：文件元数据本地存在，但数据块在 iCloud 服务器上。macOS 在读取时应自动触发下载，但在某些情况下（daemon 忙、网络差、文件数量多）会陷入死锁。

## 诊断

用 Python 逐文件测试可读性，识别 stuck 文件：

```bash
python3 -c "
import os, time, errno
base = '<vault-path>'
for root, dirs, files in os.walk(base):
    for f in sorted(files):
        if f.endswith('.md'):
            path = os.path.join(root, f)
            ok = False
            for i in range(3):
                try:
                    with open(path, 'r', encoding='utf-8') as fh:
                        fh.read()
                    ok = True
                    break
                except OSError as e:
                    if e.errno == 11:
                        time.sleep(0.5)
                        continue
                    raise
            print(f'{\"OK\" if ok else \"FAIL\"}: {os.path.relpath(path, base)}')
"
```

## 修复

### 批量修复（推荐）

```bash
find "<vault-path>" -name "*.md" -type f | while IFS= read -r f; do
    brctl download "$f" 2>/dev/null
done
```

### 单文件修复

```bash
brctl download "<file-path>"

# 验证（需等待 1-5 秒）
python3 -c "open('<file-path>').read()" && echo "OK"
```

## 注意事项

- `brctl download` 是异步的——返回 0 不代表文件立即可读。通常 1-5 秒后可用
- **不要用 Python 重试循环代替 `brctl download`**：Python 的 `open()` 重试无法触发 iCloud 的 materialization，只会反复得到 `errno 11`
- 同一个 vault 中可能部分文件 stuck、部分正常——这是正常现象

## 真实案例（2026-05-19）

离子阱LLM-Wiki vault：17 个 .md 文件中 7 个 stuck（SCHEMA.md, index.md, log.md, Nikodem Grzesiak.md, Neal Pisenti.md, Yunseong Nam.md, Reinhold Blümel.md）。经`brctl download` 逐文件修复后 lint 通过。
