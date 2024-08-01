import requests
from lxml import html

# 目标网页URL
url = 'http://example.com'



def proxies_fun():
    # 代理列表（示例）
    proxies = {
        'http': 'http://your_proxy_ip:proxy_port',
        'https': 'https://your_proxy_ip:proxy_port'
    }

    # 尝试使用代理发送请求
    try:
        response = requests.get(url, proxies=proxies, timeout=5)
        # 检查请求是否成功
        if response.status_code == 200:
            # 解析HTML内容
            tree = html.fromstring(response.content)

            # 提取数据...
            # 例如，提取所有的链接
            links = tree.xpath('//a/@href')
            for link in links:
                print(link)
        else:
            print('Failed to retrieve the webpage')
    except requests.exceptions.ProxyError:
        print('Proxy error, check your proxy settings')
    except requests.exceptions.RequestException as e:
        print(f'An error occurred: {e}')

    # 异常处理
    try:
        # 可能引发异常的代码
        response = requests.get(url, proxies=proxies)
    except requests.exceptions.RequestException as e:
        print(f'An error occurred: {e}')

def fun():
    # 发送HTTP请求
    response = requests.get(url)
    # 检查请求是否成功
    if response.status_code == 200:
        # 解析HTML内容
        tree = html.fromstring(response.content)

        # 使用XPath或CSS选择器提取数据
        # 例如，提取所有的链接
        links = tree.xpath('//a/@href')

        # 打印每个链接的href属性
        for link in links:
            print(link)
    else:
        print('Failed to retrieve the webpage')

    # 异常处理
    try:
        # 可能引发异常的代码
        response = requests.get(url)
    except requests.exceptions.RequestException as e:
        print(f'An error occurred: {e}')