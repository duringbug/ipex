'''
Description: 还需要改进，无法获得所有作品信息
Author: 唐健峰
Date: 2024-07-02 13:53:24
LastEditors: ${author}
LastEditTime: 2024-07-13 10:33:02
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

# 设置 Chrome WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)


def get_data(driver):
    result=[]
    try:
        # 等待页面加载完成（根据实际情况调整等待时间）
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//dl')))

        # 等待包含 "声：" 的第一个 dt 元素所在的 dl 元素列表
        dl_elements = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.XPATH, '//dl[dt[contains(., "声：")]]'))
        )
        # 遍历每个 dl 元素，输出角色名和声优名
        for dl in tqdm(dl_elements, desc="Processing elements"):
            dt_elements = WebDriverWait(dl, 10).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, 'dt'))
            )
            for dt_element in dt_elements:
                dt_text = dt_element.text.split('（')[0].strip()  # 获取角色名
                pattern = r'^[^\[]*'
                ac_name = re.search(pattern, dt_text).group(0).strip()
                person_names = []

                actor_list = []

                span_elements = dt_element.find_elements(By.TAG_NAME, 'span')
                for span in span_elements:
                    span_text = span.text.strip()
                    sup_elements = span.find_elements(By.TAG_NAME, 'sup')
                    for sup in sup_elements:
                        sup_text = sup.text
                        span_text = span_text.replace(sup_text, '')
                    if '声：' in span_text and '）' in span_text:
                        match = re.search(r'声：(.*?).$', span_text)
                        if match:
                            person_names = re.split(r'[、；／]', match.group(1))
                            for person_name in person_names:
                                pattern = r'^[^，]*'
                                match = re.search(pattern, person_name)
                                if match:
                                    extracted_name = match.group(0).strip()
                                    pattern = r'^[^\[\（\）\〈]*'
                                    person_name = re.search(pattern, extracted_name).group(0).strip()
                                    actor_list.append(person_name)
                if len(person_names)==0 and '声：' in dt_element.text:
                    pattern = r"声：(.*)"
                    match = re.search(pattern, dt_element.text)
                    if match:
                        # 提取匹配到的部分，并按“、”分割
                        person_names = re.split(r'[、；／]', match.group(1))
                        for person_name in person_names:
                            pattern = r'^[^，]*'
                            match = re.search(pattern, person_name)
                            if match:
                                extracted_name = match.group(0).strip()
                                pattern = r'^[^\[\（\）\〈]*'
                                person_name = re.search(pattern, extracted_name).group(0).strip()
                                actor_list.append(person_name)
                
                if(len(actor_list)>0):
                    result.append({"ac":ac_name,"actor":actor_list})

    except TimeoutException as e:
        print("未找到dl 元素列表")
        return None

    return result


def check_click(driver):
    result = None
    retries = 3  # 定义重试次数

    while retries > 0:
        try:
            # 查找所有的 h2 标签
            h2_elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, '//h2'))
            )

            # 遍历每个 h2 标签
            for index, h2 in enumerate(h2_elements):
                # 检查当前 h2 元素的文本内容
                if '登场人物' in h2.text.strip():
                    try:
                        next_div = h2.find_element(By.XPATH, 'following-sibling::div')
                    except NoSuchElementException:
                        return None

                    if '主条目：' in next_div.text:
                        print("需要跳转")
                        a_tag = next_div.find_element(By.TAG_NAME, 'a')
                        href = a_tag.get_attribute('href')
                        driver.get(href)
                        time.sleep(0.2)
                        result = get_data(driver)
                        return result
                    else:
                        result = get_data(driver)
                        return result
                    break  # 如果找到了目标元素，跳出循环

            break  # 如果成功遍历了所有 h2 元素，跳出循环

        except StaleElementReferenceException:
            retries -= 1
            print(f"StaleElementReferenceException encountered. Retrying... {retries} attempts left.")
            time.sleep(0.5)  # 等待一段时间后重试
        except TimeoutException as e:
            print(f"未找到元素: {e}")
            return None

    return result


def fetch_actor_data():

    with open('titles_by_year.json', 'r', encoding='utf-8') as file:
        titles_data = json.load(file)

    data = []

    for year in titles_data:
        print(f"Year: {year}")
        for title in titles_data[year]:
            target = title
            driver.get('https://www.google.com/')
            output_file = 'data/03.json'
            target = title
            print(target)

            # 为美好的世界献上祝福
            # 我推的孩子
            # 盾之勇者成名录
            # 夏洛特
            # 无职转生

            textarea = WebDriverWait(driver, 100).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/textarea'))
            )

            textarea.send_keys(target + "，动画，维基百科")

            search_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[3]/form/div[1]/div[1]/div[4]/center/input[1]'))
            )

            # 使用 执行点击操作
            ActionChains(driver).click(search_button).perform()
                                
            try:
                # 等待第一个包含文本 "维基百科" 的 span 元素可见
                wiki_link = WebDriverWait(driver, 20).until(
                    EC.visibility_of_element_located((By.XPATH, '//span[contains(text(), "维基百科")]'))
                )
            except TimeoutException:
                continue

            ActionChains(driver).click(wiki_link).perform()

            list = check_click(driver)

            if list is not None:
                data.append({"name": target, "list": list})

    return data


result_array = fetch_actor_data()
output_file = "works_to_actors.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(result_array, f, ensure_ascii=False, indent=4)

print(f"评论已成功写入到 {output_file}")

# 关闭浏览器
driver.quit()
