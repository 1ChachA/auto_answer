import json
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pandas as pd
import random

# 加载Excel文件
file_path = 'answer1.xlsx'  # 替换成你的Excel文件路径
df = pd.read_excel(file_path)

webdriver_path = 'chromedriver.exe'

chrome_options = Options()
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                            'like Gecko) Chrome/88.0.4324.150 Safari/537.36')
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

# 设置服务，并指定端口
service = Service(executable_path=webdriver_path)

# 初始化WebDriver
driver = webdriver.Chrome(service=service, options=chrome_options)
# 打开百度
driver.get("https://www.baidu.com")

# 找到搜索框
search_box = driver.find_element(By.ID, "kw")
# 假设配置文件路径为 config.json
config_file_path = 'config.json'


# 读取配置文件
def read_config(key):
    try:
        with open(config_file_path, 'r', encoding='utf-8') as file:
            config = json.load(file)
            # 从配置中读取指定的键
            return config.get(key)
    except FileNotFoundError:
        print("配置文件未找到")
    except json.JSONDecodeError:
        print("配置文件格式错误")
    except Exception as e:
        print(f"读取配置文件时发生错误: {e}")


# 调用函数读取融资融券手续费信息
query_cont = read_config('query')
login_time = read_config('login_time')
print(f"查询：{query_cont}")
# 输入搜索内容，添加排除特定网站的参数 "-site:licai.cofool.com"
search_query = f"inurl:licai.cofool.com/ask {query_cont}"
search_box.send_keys(search_query)

# 提交搜索
search_box.send_keys(Keys.RETURN)

# 等待页面加载
sleep(login_time)
# 循环遍历搜索结果
while True:
    # 找到所有搜索结果的链接
    links = driver.find_elements(By.CSS_SELECTOR, 'h3.t a')
    for link in links:
        # 打开每个搜索结果
        href = link.get_attribute('href')
        driver.execute_script('window.open(arguments[0])', href)
        driver.switch_to.window(driver.window_handles[1])  # 切换到新打开的窗口
        # 假设driver是你的WebDriver实例
        cookies = driver.get_cookies()
        # 将cookie保存到文件
        with open("cookies.json", "w") as file:
            json.dump(cookies, file)
        # 在这里添加处理数据的代码
        print(driver.title)
        elements = driver.find_elements(By.CSS_SELECTOR, ".answer-entrance")

        # 遍历找到的元素
        for element in elements:
            if "我来回答" in element.text:
                # 如果元素的文本包含"我来回答"，则点击该元素
                element.click()
                break  # 假设只有一个符合条件的元素，找到后即停止循环

        # 定位到contenteditable属性为true的div
        try:
            # 移除遮挡元素
            driver.execute_script("arguments[0].style.display = 'none';", driver.find_element(By.CSS_SELECTOR, "div"
                                                                                                               ".answer-tip-wh.textarea-tip"))
            # 使用CSS选择器定位到具有指定class和contenteditable属性的元素
            editable_div = driver.find_element(By.CSS_SELECTOR, 'div.w-e-text[contenteditable="true"]')
            # 确保元素处于聚焦状态
            editable_div.click()
            random_row = random.choice(range(len(df)))
            random_value = df.iloc[random_row, 0]
            # 发送文本到这个元素
            editable_div.send_keys(random_value)
            # 使用CSS选择器定位按钮
            submit_button = driver.find_element(By.CSS_SELECTOR,
                                                "input.redBtn.borderR5.submit-answer.floatR[value='提交答案']")
            # 点击按钮
            submit_button.click()
            print("等待20s，防止过频繁回答")
            sleep(20)
        except Exception as e:  # 正确的异常处理语法
            print("已经回答了")  # 打印异常信息
        # sleep(10)
        # 处理完毕，关闭当前窗口并返回搜索结果页
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    # 尝试点击下一页，如果失败则结束循环
    try:
        next_page = driver.find_element(By.XPATH, '//a[contains(@class, "n") and contains(text(), "下一页")]')
        print("点击下一页")
        next_page.click()
        sleep(2)  # 等待页面加载
    except:
        break  # 如果没有找到下一页，则结束循环

# 完成所有操作后，关闭浏览器
driver.quit()
