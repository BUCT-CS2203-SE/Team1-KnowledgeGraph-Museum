import time
import requests
from bs4 import BeautifulSoup  # 修改导入的库
import certifi
import csv
import os

arts_info = []
num = 1

headers = {
    "accept": "text/html, */*; q=0.01",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "priority": "u=1, i",
    "referer": "https://searchcollection.asianart.org/search/china/objects/list?page=2",
    "sec-ch-ua": "\"Microsoft Edge\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0",
    "x-requested-with": "XMLHttpRequest"
}
cookies = {
    "JSESSIONID": "6A686673CAD1486334503E227B47919F",
    "_gcl_au": "1.1.1950434450.1745369201",
    "_gid": "GA1.2.1526187988.1745369202",
    "_hjSession_1929636": "eyJpZCI6ImYwY2QwZmQwLWZkNmUtNDA4NS04NDMwLTQwNGJmYmI4OTFmZSIsImMiOjE3NDUzNjkyMDIwNDMsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjoxLCJzcCI6MH0=",
    "_hjSessionUser_1929636": "eyJpZCI6IjI1MDQ0ODc4LTRkOWMtNWMwMS1iNjE2LTg4ZTJmNmJkZDgxZiIsImNyZWF0ZWQiOjE3NDUzNjkyMDIwNDEsImV4aXN0aW5nIjp0cnVlfQ==",
    "_fbp": "fb.1.1745371131565.632400288850517901",
    "_gat_UA-36218640-1": "1",
    "_ga_ELLF5DBPKS": "GS1.1.1745371130.2.1.1745375475.47.0.0",
    "_ga": "GA1.2.670806764.1745369201",
    "_ga_ET2P2QHM1T": "GS1.2.1745371131.2.1.1745375475.21.0.0",
    "_ga_Z9547MV991": "GS1.2.1745371131.2.1.1745375475.0.0.0"
}

# 网站基础URL配置
root_url = "https://searchcollection.asianart.org"
base_url = 'https://searchcollection.asianart.org/search/china/objects/list'


def download_image(url, save_path):
    """
    下载图片并保存到本地。
    """
    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()

        # 确保目录存在
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # 保存图片
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print(f"✅ 下载成功: {save_path}")
    except Exception as e:
        print(f"❌ 下载失败: {url} | 错误: {e}")


def first_page(page):
    full_url = []
    url = "https://searchcollection.asianart.org/search/china/objects/list"
    params = {"page": str(page)}

    response = requests.get(url, headers=headers, cookies=cookies, params=params, verify=certifi.where())
    soup = BeautifulSoup(response.text, 'html.parser')  # 替换解析方式

    # 使用CSS选择器替代xpath
    links = soup.select('div.text-wrap a[href]')
    for a in links:
        href = a['href']
        full_url.append(f"https://searchcollection.asianart.org{href}")

    # print(full_url)
    return full_url


def scrape_detail(u):
    global arts_info, num
    # print(f'爬取的链接是：{u}')
    one_art = []
    response_u = requests.get(u, headers=headers, cookies=cookies, verify=False)
    soup = BeautifulSoup(response_u.text, 'html.parser')  # 替换解析方式

    # 使用find_all替代xpath
    # detail_blocks = soup.select('div.item-details-inner > div')
    detail_blocks = soup.select('.detailField')

    for i, block in enumerate(detail_blocks):
        # 使用get_text获取所有文本
        info = block.get_text(strip=False, separator='\n').split('\n')
        info = [line.strip() for line in info if line.strip()]
        info_parse = {'': ''}

        if i == 0:
            info_parse = {'Title': ' '.join(info)}
            # print(info_parse)
        else:
            try:
                label_tag = block.select_one('.detailFieldLabel')
                value_tag = block.select_one('.detailFieldValue')

                if label_tag and value_tag:
                    key = label_tag.get_text(strip=True)
                    # 深层获取所有段落或文本
                    value = value_tag.get_text(separator=' ', strip=True)
                    info_parse = {key: value}
                    # print({key: value})

                # key = info[0].rstrip(':')
                # value = ' '.join(info[1:]) if len(info) > 1 else ''
                # # info_parse = f"{key} : {value}"
                # info_parse = {key: value}
                # # print(info_parse)
            except IndexError:
                pass
        one_art.append(info_parse)

    img_tag = soup.select_one("div.emuseum-img-wrap img")  # preview后缀
    img_url = root_url + img_tag['src'] if img_tag and img_tag.get('src') else "No Image"
    one_art.append({'Img_url': img_url})
    one_art.append({'Img_path': f'images_china/asian_{num}.jpg'})

    # print(one_art)
    download_image(img_url, f'images_china/asian_{num}.jpg')
    num += 1
    arts_info.append(one_art)


import csv


def save_object_data_to_csv(all_data, filename='objects_china.csv'):
    """
    把多个物品的数据保存为 CSV 文件。
    """
    # 提取所有字段名
    all_keys = set()
    processed_rows = []

    for item_data in all_data:
        merged = {}
        for entry in item_data:
            merged.update(entry)
        processed_rows.append(merged)
        all_keys.update(merged.keys())

    fieldnames = list(all_keys)

    # 写入 CSV
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in processed_rows:
            writer.writerow(row)


if __name__ == '__main__':
    for page in range(1, 600):
        print('=' * 200)
        print(f'当前页码：{page}')
        url_list = first_page(page)
        for u in url_list:
            scrape_detail(u)
            time.sleep(1)
        print(f'第 {page} 页爬取完毕。')
        print('=' * 200)
        save_object_data_to_csv(arts_info)
