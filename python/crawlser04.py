'''
Description: 游戏配音爬取
Author: 唐健峰
Date: 2024-07-02 13:53:24
LastEditors: ${author}
LastEditTime: 2024-07-15 16:05:06
'''
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from tqdm import tqdm

import time
import re

tagrt_urls = [
    "https://zh.wikipedia.org/wiki/%E8%94%9A%E8%97%8D%E6%AA%94%E6%A1%88%E8%A7%92%E8%89%B2%E5%88%97%E8%A1%A8",
    "https://zh.wikipedia.org/wiki/%E5%8E%9F%E7%A5%9E%E8%A7%92%E8%89%B2%E5%88%97%E8%A1%A8",
    "https://zh.wikipedia.org/wiki/%E5%B4%A9%E5%9D%8F3",
    "https://zh.wikipedia.org/zh-cn/%E6%98%8E%E6%97%A5%E6%96%B9%E8%88%9F",
    "https://zh.wikipedia.org/wiki/%E5%B4%A9%E5%9D%8F%EF%BC%9A%E6%98%9F%E7%A9%B9%E9%93%81%E9%81%93%E8%A7%92%E8%89%B2%E5%88%97%E8%A1%A8",
]
target_names = [
    "蔚蓝档案",
    "原神",
    "崩坏3",
    "明日方舟",
    "崩坏星穹铁道",
]
result_array = []

# 设置 Chrome WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

def get_data(driver):
    result=[]
    try:
        # 等待页面加载完成（根据实际情况调整等待时间）
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//dl')))
        # 等待包含 "配音：" 的第一个 dt 元素所在的 dl 元素列表
        dl_elements = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.XPATH, '//dl[dd[contains(., "配音：")] | dt[contains(., "配音：") or contains(., "声：")]]'))
        )
        for dl in tqdm(dl_elements, desc="Processing elements"):
            try:
                dt_elements = WebDriverWait(dl, 1).until(
                    EC.presence_of_all_elements_located((By.TAG_NAME, 'dt'))
                )
            except Exception as e:
                continue
            for dt_element in dt_elements:
                actor_list = []
                if '配音：' in dt_element.text:
                    dt_text = dt_element.text.split('（')[0].strip()  # 获取角色名
                    pattern = r'^[^\[]*'
                    ac_name = re.search(pattern, dt_text).group(0).strip()
                    match = re.search(r'配音：(.*?).$', dt_element.text)
                    if match:
                        person_names = re.split(r'[、；／]', match.group(1))
                        for person_name in person_names:
                            pattern = r'^[^\[\（\）\〈]*'
                            person_name02 = re.search(pattern, person_name).group(0).strip()
                            actor_list.append(person_name02)
                    if(len(actor_list)>0):
                        result.append({"ac":ac_name,"actor":actor_list})
                    continue
                if '声：' in dt_element.text:
                    dt_text = dt_element.text.split('（')[0].strip()  # 获取角色名
                    pattern = r'^[^\[]*'
                    ac_name = re.search(pattern, dt_text).group(0).strip()
                    match = re.search(r'声：(.*?).$', dt_element.text)
                    if match:
                        person_names = re.split(r'[、；／→]', match.group(1))
                        for person_name in person_names:
                            pattern = r'^[^\※\[\（\）\〈]*'
                            person_name02 = re.search(pattern, person_name).group(0).strip()
                            actor_list.append(person_name02)
                    if(len(actor_list)>0):
                        result.append({"ac":ac_name,"actor":actor_list})
                    continue

                dt_text = dt_element.text.split('（')[0].strip()  # 获取角色名
                pattern = r'^[^\[]*'
                ac_name = re.search(pattern, dt_text).group(0).strip()
                person_names = []
                try:
                    dd_element = dt_element.find_element(By.XPATH, 'following-sibling::dd[contains(., "配音：")]')
                    # 你可以根据需要进一步处理 dd_element
                    dd_text = dd_element.text
                    pattern = r"配音：(.*?)(?:，|$)"
                    match = re.search(pattern, dd_text)
                    if match:
                        # 提取匹配到的部分，并按“、”分割
                        person_names = re.split(r'[、；／→]', match.group(1))
                        for person_name in person_names:
                            pattern = r'^[^，]*'
                            match = re.search(pattern, person_name)
                            if match:
                                extracted_name = match.group(0).strip()
                                pattern = r'^[^\※\[\（\）\〈]*'
                                person_name = re.search(pattern, extracted_name).group(0).strip()
                                actor_list.append(person_name)
                except NoSuchElementException:
                    pass
                if(len(actor_list)>0):
                    result.append({"ac":ac_name,"actor":actor_list})
    except Exception as e:
        print(e)
        print("未找到dl 元素列表")
        return None

    print(result)
    return result


def fetch_actor_data():
    data = []
    for tagrt_url,target_name in zip(tagrt_urls,target_names):
        driver.get(tagrt_url)
        list = get_data(driver)

        if list is not None:
            data.append({"name": target_name, "list": list})
        else:
            print("error")
    
    return data


result_array = fetch_actor_data()
output_file = "games_to_actors.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(result_array, f, ensure_ascii=False, indent=4)

print(f"评论已成功写入到 {output_file}")

# 关闭浏览器
driver.quit()