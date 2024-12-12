'''
Description: 
Author: 唐健峰
Date: 2024-07-11 12:59:07
LastEditors: ${author}
LastEditTime: 2024-07-14 00:00:23
'''
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
import time

from words_to_points import analyze_sentiment

# 设置 Chrome WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
driver.get('https://web.agespa-01.com:8443/#/detail/20240012')
output_file = 'data/从Lv2开始开挂的原勇者候补悠闲的异世界生活.json'

# 获取所有评论
comments = []
points = []
dates = []


for i in range(1, 999):
    try:
        if i > 1:
            # 等待直到分页按钮可见
            li = WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.XPATH, f'//li[@class="van-pagination__item van-pagination__page van-hairline" and contains(text(), "{i}")]'))
            )                    
            # 使用 JavaScript 将元素滚动到视口内，并执行点击操作
            driver.execute_script("arguments[0].scrollIntoView(true);", li)
            driver.execute_script("document.querySelector('.van-hairline--top.van-tabbar.van-tabbar--fixed').style.display='none';")
            actions = ActionChains(driver)
            actions.move_to_element(li).click().perform()
                    
            # 等待一段时间，确保页面元素变化完全
            time.sleep(2)
    except TimeoutException:
        print("评论加载完毕")
        break
    # 等待评论加载完毕
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'video-comments-list--content')))
    except TimeoutException:
        print("评论加载超时")
    comment_elements = driver.find_elements(By.CLASS_NAME, 'video-comments-list--content')
    date_elements = driver.find_elements(By.CLASS_NAME, 'video-comments-list--date')
    for comment_element, date_element in zip(comment_elements, date_elements):
        comment_text = comment_element.text
        comment_date = date_element.text
        # 过滤掉带有"该条评论正等待审核！"文本的评论
        if "该条评论正等待审核！" not in comment_text and "该条评论存在异议，已被屏蔽！" not in comment_text:
            print(comment_text)
            comments.append(comment_text)
            points.append(analyze_sentiment(comment_text))
            dates.append(comment_date)

# 将评论写入 JSON 文件
data = {
    'comments': comments,
    'point': points,
    'date': dates
}
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print(f"评论已成功写入到 {output_file}")

# 关闭浏览器
driver.quit()
