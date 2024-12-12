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

# 设置 Chrome WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# 访问网页
driver.get('https://web.agespa-01.com:8443/#/catalog')

years = ['2024', '2023', '2022', '2021', '2020', '2019', '2018', '2017', '2016', '2015', '2014', 
         '2013', '2012', '2011', '2010', '2009', '2008', '2007', '2006', '2005', '2004', 
         '2003', '2002', '2001'] # 根据需要添加更多年份

data = {}  # 创建一个空的字典，用于存储每年的标题列表

for y in years:
    try:
        year_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f'//span[@class="van-tab__text" and contains(text(), "{y}")]'))
        )
        ActionChains(driver).move_to_element(year_element).click().perform()
    except Exception as e:
        print(f"Year {y} not found or clickable:", e)
        continue  # 跳过当前年份，继续下一个年份

    try:
        titles_in_year = []  # 每年的标题列表

        for i in range(1, 999):
            try:
                if i > 1:
                    # 等待直到分页按钮可见
                    li = WebDriverWait(driver, 10).until(
                        EC.visibility_of_element_located((By.XPATH, f'//li[@class="van-pagination__item van-pagination__page van-hairline" and contains(text(), "{i}")]'))
                    )
                    
                    # 使用 JavaScript 将元素滚动到视口内，并执行点击操作
                    driver.execute_script("arguments[0].scrollIntoView(true);", li)
                    driver.execute_script("document.querySelector('.van-hairline--top.van-tabbar.van-tabbar--fixed').style.display='none';")
                    actions = ActionChains(driver)
                    actions.move_to_element(li).click().perform()
                    
                    # 等待一段时间，确保页面元素变化完全
                    time.sleep(2)
                
                # 显示等待直到<h3 class="title">元素出现
                titles = WebDriverWait(driver, 10).until(
                    EC.visibility_of_all_elements_located((By.XPATH, '//h3[@class="title"]'))
                )
                
                # 收集标题文本
                for title in titles:
                    titles_in_year.append(title.text)
                print(f"page {i} in {y}")
            
            except TimeoutException as e:
                print(f"超时异常在分页 {i} in Year {y}:", e)
                break  # 跳出分页循环，进入下一个年份循环
        
        # 将该年的标题列表添加到数据字典中
        data[y] = titles_in_year
    
    except TimeoutException as e:
        print("超时异常:", e)

    except Exception as e:
        print("操作出错:", e)

# 将数据写入 JSON 文件
output_file = 'titles_by_year.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print(f"标题已成功写入到 {output_file}")
