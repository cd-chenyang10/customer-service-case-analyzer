---
name: customer-service-case-analyzer
description: 客服CASE归因分析工具，用于自动分析"直呼人工"CASE的异常类型。分析ASR（语音转文本）异常（如同音字错误、断句不完整、无意义片段）和智能识别异常（如AI答非所问、用户明确转人工未响应、识别功能树为null但用户提及业务）。输入为包含用户智能交互明细的Excel文件，输出标注到是否ASR异常、是否智能识别异常、是否无异常三列。
---

# 客服CASE归因分析

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

## 判断规则

### ASR异常判断

| 类型 | 判断条件 |
|------|----------|
| 同音字错误 | 包含常见转写错误关键词（如"极速"→"激素"） |
| 断句不完整 | 文本以数字、"还有"、"然后"、"那个"、"就是"、"所以"、"但是"结尾 |
| 无意义片段 | 只有语气词（嗯、啊、哦等）或无有效字符 |

### 智能识别异常判断

| 类型 | 判断条件 |
|------|----------|
| 答非所问 | 用户说"不是"、"我说的是"、"你没听懂"、"不是这个问题"、"你理解错了" |
| 转人工未响应 | 用户明确说"转人工"、"人工服务"、"找人工"等 |
| 功能树未识别 | 用户提及业务关键词（订单、退款、投诉等）但session_ft_2为null |

## 扩展规则

如需添加新的判断规则，编辑 `scripts/analyze_case.py` 中的以下字典：

- `ASR_PATTERNS['homophone_errors']` - 添加同音字错误模式
- `ASR_PATTERNS['incomplete_patterns']` - 添加断句不完整模式
- `INTENT_PATTERNS['manual_request']` - 添加转人工请求关键词
- `INTENT_PATTERNS['mismatch_signs']` - 添加答非所问迹象

## 注意事项

1. 批处理大小默认为1000行，可根据需要调整
2. 如果输出列已存在，会被覆盖更新
3. 空对话内容不会被标记为任何异常
4. 一个CASE可能同时被标记为ASR异常和智能识别异常
