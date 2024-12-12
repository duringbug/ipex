'''
Description: 
Author: 唐健峰
Date: 2024-07-11 11:40:58
LastEditors: ${author}
LastEditTime: 2024-07-11 14:47:27
'''
import re

from textblob import TextBlob
from snownlp import SnowNLP

def extract_chinese(text):
    pattern = re.compile("[\u4e00-\u9fa5]+")  # 匹配中文字符的正则表达式
    chinese_text = "".join(pattern.findall(text))
    return chinese_text

def normalize_polarity(polarity):
    normalized_polarity = (polarity + 1) / 2  # 将 [-1, 1] 映射到 [0, 1]
    return normalized_polarity

def analyze_sentiment(text):
    chinese_text = extract_chinese(text)

    if chinese_text:
        s = SnowNLP(chinese_text)
        sentiment = s.sentiments
        return sentiment
    else:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        normalized_polarity = normalize_polarity(polarity)
        return normalized_polarity