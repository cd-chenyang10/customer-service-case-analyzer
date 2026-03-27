#!/usr/bin/env python3
"""
客服CASE归因分析脚本
分析直呼人工CASE，判断是ASR异常、智能识别异常还是无异常
"""

import pandas as pd
import re
import sys
from typing import Tuple

# ASR 异常模式
ASR_PATTERNS = {
    # 同音字错误模式（常见转写错误）
    'homophone_errors': [
        (r'极速', '激素'),
        (r'配箱', '配件'),
        (r'三七五', '三七五'),  # 数字类可能是正常的
    ],
    # 断句不完整的标志
    'incomplete_patterns': [
        r'.*是[一二三四五六七八九十百千万亿\d]+$',  # 以数字结尾
        r'.*还有$',  # 未说完
        r'.*然后$',  # 未说完
        r'.*那个$',  # 未说完
        r'.*就是$',  # 未说完
        r'.*所以$',  # 未说完
        r'.*但是$',  # 未说完
    ],
    # 无意义片段
    'meaningless_patterns': [
        r'^[嗯啊哦哎哟喂哼]+$',  # 只有语气词
        r'^[^\u4e00-\u9fa5a-zA-Z0-9]+$',  # 无有效字符
    ]
}

# 智能识别异常模式
INTENT_PATTERNS = {
    # 用户明确要转人工
    'manual_request': [
        r'转人工',
        r'人工服务',
        r'找人工',
        r'我要人工',
        r'人工客服',
        r'接人工',
        r'人工',
    ],
    # 答非所问的迹象
    'mismatch_signs': [
        r'不是[，,]?',
        r'我说的是',
        r'你没听懂',
        r'不是这个问题',
        r'你理解错了',
    ]
}


def analyze_asr_issue(dialog_text: str) -> Tuple[bool, str]:
    """
    分析是否存在ASR异常
    
    Returns:
        (是否异常, 原因描述)
    """
    if pd.isna(dialog_text) or not dialog_text or str(dialog_text).strip() == '':
        return False, "无对话内容"
    
    text = str(dialog_text)
    
    # 检查同音字错误
    for pattern, correct in ASR_PATTERNS['homophone_errors']:
        if re.search(pattern, text):
            return True, f"疑似同音字错误: '{pattern}' 可能应为 '{correct}'"
    
    # 检查断句不完整
    for pattern in ASR_PATTERNS['incomplete_patterns']:
        if re.search(pattern, text):
            return True, "文本疑似不完整"
    
    # 检查无意义片段
    for pattern in ASR_PATTERNS['meaningless_patterns']:
        if re.search(pattern, text):
            return True, "无有效语义内容"
    
    return False, ""


def analyze_intent_issue(dialog_text: str, session_ft_2: str) -> Tuple[bool, str]:
    """
    分析是否存在智能识别异常
    
    Returns:
        (是否异常, 原因描述)
    """
    if pd.isna(dialog_text) or not dialog_text or str(dialog_text).strip() == '':
        return False, "无对话内容"
    
    text = str(dialog_text)
    
    # 情况1: 用户明确说转人工，检查AI是否响应
    for pattern in INTENT_PATTERNS['manual_request']:
        if re.search(pattern, text):
            # 如果用户明确说了转人工，但AI没有转，就是异常
            # 这里需要根据实际对话判断，简单判断是如果包含"转人工"但后续没有转人工的响应
            return True, "用户明确请求转人工"
    
    # 情况2: 答非所问的迹象
    for pattern in INTENT_PATTERNS['mismatch_signs']:
        if re.search(pattern, text):
            return True, "可能存在答非所问"
    
    # 情况3: 用户说了要咨询什么，但session_ft_2为null或空
    # 简单判断：如果对话中有业务关键词但session_ft_2为空
    business_keywords = ['订单', '退款', '退货', '投诉', '举报', '账号', '密码', '直播', '商品']
    has_business_intent = any(kw in text for kw in business_keywords)
    
    if has_business_intent and (pd.isna(session_ft_2) or str(session_ft_2).strip() == '' or str(session_ft_2) == 'NaN'):
        return True, "用户提及业务但未识别功能树"
    
    return False, ""


def analyze_case(dialog_text: str, session_ft_2: str) -> Tuple[str, str, str]:
    """
    分析单个CASE，返回三个异常标记
    
    Returns:
        (是否ASR异常, 是否智能识别异常, 是否无异常)
        值为 "是" 或 ""
    """
    # 首先检查ASR异常
    is_asr_issue, asr_reason = analyze_asr_issue(dialog_text)
    
    # 然后检查智能识别异常
    is_intent_issue, intent_reason = analyze_intent_issue(dialog_text, session_ft_2)
    
    # 如果都不是异常，就是无异常
    if not is_asr_issue and not is_intent_issue:
        return "", "", "是"
    
    return (
        "是" if is_asr_issue else "",
        "是" if is_intent_issue else "",
        ""
    )


def process_excel(input_path: str, output_path: str = None, batch_size: int = 1000) -> str:
    """
    处理Excel文件
    
    Args:
        input_path: 输入Excel文件路径
        output_path: 输出Excel文件路径（默认为原文件名_analyzed.xlsx）
        batch_size: 批处理大小
    
    Returns:
        输出文件路径
    """
    if output_path is None:
        output_path = input_path.replace('.xlsx', '_analyzed.xlsx')
    
    # 读取Excel
    df = pd.read_excel(input_path)
    
    # 确保输出列存在（使用object类型存储字符串）
    if '是否ASR异常' not in df.columns:
        df['是否ASR异常'] = pd.Series(dtype='object')
    else:
        df['是否ASR异常'] = df['是否ASR异常'].astype('object')
    if '是否智能识别异常' not in df.columns:
        df['是否智能识别异常'] = pd.Series(dtype='object')
    else:
        df['是否智能识别异常'] = df['是否智能识别异常'].astype('object')
    if '是否无异常' not in df.columns:
        df['是否无异常'] = pd.Series(dtype='object')
    else:
        df['是否无异常'] = df['是否无异常'].astype('object')
    
    # 处理每一行
    for idx in range(min(batch_size, len(df))):
        dialog = df.at[idx, '用户智能交互明细'] if '用户智能交互明细' in df.columns else ''
        ft2 = df.at[idx, 'session_ft_2'] if 'session_ft_2' in df.columns else ''
        
        asr_result, intent_result, normal_result = analyze_case(dialog, ft2)
        
        df.loc[idx, '是否ASR异常'] = asr_result
        df.loc[idx, '是否智能识别异常'] = intent_result
        df.loc[idx, '是否无异常'] = normal_result
    
    # 保存结果
    df.to_excel(output_path, index=False)
    
    # 输出统计
    asr_count = (df['是否ASR异常'] == '是').sum()
    intent_count = (df['是否智能识别异常'] == '是').sum()
    normal_count = (df['是否无异常'] == '是').sum()
    
    print(f"分析完成!")
    print(f"总处理行数: {min(batch_size, len(df))}")
    print(f"ASR异常: {asr_count}")
    print(f"智能识别异常: {intent_count}")
    print(f"无异常: {normal_count}")
    print(f"输出文件: {output_path}")
    
    return output_path


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python analyze_case.py <input.xlsx> [output.xlsx] [batch_size]")
        print("示例: python analyze_case.py cases.xlsx cases_analyzed.xlsx 1000")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    batch = int(sys.argv[3]) if len(sys.argv) > 3 else 1000
    
    process_excel(input_file, output_file, batch)
