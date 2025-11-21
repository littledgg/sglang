# PR Analysis Tool for SGLang

这个工具帮助你分析 SGLang 项目的 Pull Request (PR)，了解最新的推理技术发展方向。

## 功能特点 (Features)

- ✅ 获取指定时间范围内的所有 PR（已合入和未合入）
- ✅ 支持分页，解决 API 返回数量限制问题
- ✅ 自动分类 PR 到不同技术方向
- ✅ 支持多种输出格式（文本、JSON）
- ✅ 详细的 PR 信息展示

## 技术分类 (Categories)

工具会自动将 PR 分类到以下技术方向：

1. **Performance Optimization** - 性能优化
2. **Model Support** - 模型支持（Llama, DeepSeek, Qwen 等）
3. **Inference Engine** - 推理引擎（CUDA, Triton, FlashAttention 等）
4. **Distributed & Parallelism** - 分布式并行（TP, PP, EP）
5. **Quantization & Compression** - 量化压缩（INT4, INT8, FP8）
6. **API & Interface** - API 接口（OpenAI, gRPC, HTTP）
7. **Structured Output** - 结构化输出（JSON, Grammar）
8. **Testing & CI** - 测试和持续集成
9. **Documentation** - 文档
10. **Bug Fix** - Bug 修复
11. **Infrastructure** - 基础设施
12. **Observability** - 可观测性（日志、监控）

## 使用方法 (Usage)

### 基本用法

分析最近 7 天的 PR：
```bash
python scripts/analyze_prs.py --days 7
```

分析最近 30 天的 PR：
```bash
python scripts/analyze_prs.py --days 30
```

### 高级选项

只查看开放状态的 PR：
```bash
python scripts/analyze_prs.py --days 7 --state open
```

输出 JSON 格式（便于进一步处理）：
```bash
python scripts/analyze_prs.py --days 7 --output json > prs.json
```

不显示详细的 PR 列表：
```bash
python scripts/analyze_prs.py --days 7 --no-details
```

增加获取的页数（每页 100 个 PR）：
```bash
python scripts/analyze_prs.py --days 30 --max-pages 20
```

分析 fork 的仓库：
```bash
python scripts/analyze_prs.py --days 7 --owner yourusername --repo sglang
```

### 完整参数列表

```
--days DAYS           回溯天数（默认：7）
--state {open,closed,all}  PR 状态（默认：all）
--max-pages N         最大页数（默认：10，每页 100 个 PR）
--output {text,json}  输出格式（默认：text）
--no-details          隐藏详细的 PR 列表
--owner OWNER         仓库所有者（默认：sgl-project）
--repo REPO           仓库名称（默认：sglang）
```

## 避免 API 速率限制 (Rate Limit)

GitHub API 对未认证请求有速率限制（每小时 60 次）。为了获得更高的速率限制（每小时 5000 次），你需要设置 GitHub Token：

1. 在 GitHub 创建 Personal Access Token：
   - 访问：https://github.com/settings/tokens
   - 点击 "Generate new token (classic)"
   - 选择 `public_repo` 权限
   - 生成并复制 token

2. 设置环境变量：

**Linux/Mac:**
```bash
export GITHUB_TOKEN=your_token_here
python scripts/analyze_prs.py --days 7
```

**Windows (CMD):**
```cmd
set GITHUB_TOKEN=your_token_here
python scripts\analyze_prs.py --days 7
```

**Windows (PowerShell):**
```powershell
$env:GITHUB_TOKEN="your_token_here"
python scripts\analyze_prs.py --days 7
```

## 示例输出 (Sample Output)

### 文本格式输出

```
Fetching PRs from sgl-project/sglang...
State: all, Looking back: 7 days
Since: 2025-11-14 08:00:00
--------------------------------------------------------------------------------
Page 1: Found 85 PRs (Total: 85)
Page 2: Found 42 PRs (Total: 127)
Reached PRs older than 7 days, stopping...

================================================================================
PR ANALYSIS REPORT
================================================================================

Total PRs: 127

By State:
  Closed: 95
  Open: 32

By Category:
  Bug Fix: 45
  Performance Optimization: 38
  Model Support: 32
  Inference Engine: 28
  Documentation: 18
  API & Interface: 15
  Testing & CI: 12
  Distributed & Parallelism: 10
  Quantization & Compression: 8
  Infrastructure: 6
  Structured Output: 5
  Observability: 3

================================================================================
DETAILED PR BREAKDOWN BY CATEGORY
================================================================================

Bug Fix (45 PRs):
--------------------------------------------------------------------------------
  #12345 [✓ Merged] Fix memory leak in RadixCache
    URL: https://github.com/sgl-project/sglang/pull/12345
    Author: contributor1, Created: 2025-11-18
  #12344 [○ open] Fix CUDA error in flashinfer kernel
    URL: https://github.com/sgl-project/sglang/pull/12344
    Author: contributor2, Created: 2025-11-17
  ...
```

### JSON 格式输出

```json
{
  "total_prs": 127,
  "by_state": {
    "closed": 95,
    "open": 32
  },
  "by_category": {
    "Bug Fix": 45,
    "Performance Optimization": 38,
    "Model Support": 32,
    ...
  },
  "categorized_prs": {
    "Bug Fix": [
      {
        "number": 12345,
        "title": "Fix memory leak in RadixCache",
        "state": "closed",
        "merged": true,
        "url": "https://github.com/sgl-project/sglang/pull/12345",
        "created_at": "2025-11-18T10:30:00Z",
        "updated_at": "2025-11-19T15:45:00Z",
        "user": "contributor1",
        "categories": ["Bug Fix", "Performance Optimization"]
      },
      ...
    ]
  }
}
```

## 使用建议 (Tips)

1. **关注技术方向**：查看哪些类别的 PR 数量最多，了解当前开发重点
2. **学习最新技术**：阅读 "Performance Optimization" 和 "Inference Engine" 类的 PR
3. **定期跟踪**：每周运行一次，了解项目动态
4. **导出数据**：使用 `--output json` 导出数据，用于进一步分析
5. **组合使用**：结合 `--state open` 查看待合入的新功能

## 故障排除 (Troubleshooting)

**问题：Rate limit exceeded**
- 解决：设置 GITHUB_TOKEN 环境变量（见上文）

**问题：No PRs found**
- 检查时间范围是否合适（--days）
- 检查网络连接
- 尝试增加 --max-pages

**问题：连接超时**
- 检查网络连接
- 可能是 GitHub API 暂时不可用，稍后重试

## 贡献 (Contributing)

如果你想添加新的分类类别或改进分类算法，欢迎修改 `analyze_prs.py` 中的 `CATEGORIES` 字典。

## 许可 (License)

与 SGLang 项目保持一致的许可证。
