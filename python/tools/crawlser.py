import re
import ssl
import certifi
from urllib.request import urlopen
from bs4 import BeautifulSoup
import jieba as jb

def cut_content(words):
    word_freq = {}
    for word in words:
        word_freq[word] = word_freq.get(word, 0) + 1
    # 只取词频大于3的词
    filtered_word_freq = {word: freq for word, freq in word_freq.items() if freq > 3}
    
    # 按词频排序
    sorted_word_freq = dict(sorted(filtered_word_freq.items(), key=lambda item: item[1], reverse=True))
    
    return sorted_word_freq

def prc01():
    context = ssl.create_default_context(cafile=certifi.where())

    strhtml = urlopen("http://pythonscraping.com/pages/page1.html", context=context)
    print(strhtml.read())

    html = urlopen("https://www.pythonscraping.com/exercises/exercise1.html", context=context)
    bsObj = BeautifulSoup(html.read(), "html.parser")
    print(bsObj.h1)


    html02 = urlopen("https://www.ecnu.edu.cn/info/1094/59213.htm", context=context)
    bsObj = BeautifulSoup(html02.read(),"html.parser");
    rs = bsObj.find_all(attrs={"name": "description"});
    print ( rs[0]['content'] );
    print ( rs[1]['content'] );


def prc02():
    context = ssl.create_default_context(cafile=certifi.where())

    html = urlopen("http://chenhui.li/courses/infovis2024/05-EcnuNews.html", context=context)
    bsObj = BeautifulSoup(html.read(), "html.parser")
    a_tags = bsObj.find_all('a')
    
    result_list = []  # 用于存储每个 a_tag 的 content_dict
    
    for a_tag in a_tags:
        href = a_tag.get('href')
        html_herf = urlopen(href, context=context)
        bsObj_herf = BeautifulSoup(html_herf.read(), "html.parser")

        title = a_tag.get('title').strip()
        print(f'href: {href}, title: {title}')
        
        vsb_content = bsObj_herf.find(id="vsb_content")
        if vsb_content:
            p_tags = vsb_content.find_all('p')
            content = ""
            for p_tag in p_tags[:-11]:
                content += p_tag.get_text().strip()

            content = re.sub(r'[^\w\s]', '', content)
            content_word = jb.lcut(content)
            content_dict = cut_content(content_word)
            
            result_list.append(content_dict)  # 将 content_dict 添加到结果列表中
        
        else:
            print("没有找到id为vsb_content的标签")

    return result_list  # 返回包含所有 content_dict 的列表



# prc01()
# print(prc02())