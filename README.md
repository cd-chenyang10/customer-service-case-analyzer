# Customer Service Case Analyzer

客服CASE归因分析工具，用于自动分析"直呼人工"CASE的异常类型。

## 功能

自动分析客服系统中"直呼人工"CASE的归因，判断属于以下哪种异常类型：

1. **ASR异常** - 语音转文本过程中的问题
   - 同音字错误（如"激素"转写为"极速"）
   - 断句不完整（文本以数字、"还有"、"然后"等结尾）
   - 无意义片段（只有语气词或无效字符）

2. **智能识别异常** - AI意图理解问题
   - 答非所问（用户说"不是"、"我说的是"等修正AI的回答）
   - 用户明确说"转人工"但AI没有响应
   - 用户说了业务意图但`session_ft_2`（功能树）为null

3. **无异常** - 对话流程正常

## 安装

```bash
npx skills add cd-chenyang10/agent-skills@customer-service-case-analyzer
```

## 使用方法

### 方式1：直接运行脚本

```bash
python scripts/analyze_case.py <输入文件.xlsx> [输出文件.xlsx] [批处理大小]
```

示例：
```bash
python scripts/analyze_case.py cases.xlsx cases_analyzed.xlsx 1000
```

### 方式2：在Python中调用

```python
from scripts.analyze_case import process_excel

# 处理Excel文件
output_path = process_excel(
    input_path='input.xlsx',
    output_path='output.xlsx',
    batch_size=1000
)
```

## 输入要求

Excel 文件必须包含以下列：
- `用户智能交互明细` - 用户与AI的对话文本
- `session_ft_2` - AI识别的功能树（可为空）
- `是否直呼` - 标记是否直呼人工

## 输出列

分析结果写入以下列：
- `是否ASR异常` - 是 / 空
- `是否智能识别异常` - 是 / 空
- `是否无异常` - 是 / 空

## 许可证

MIT
