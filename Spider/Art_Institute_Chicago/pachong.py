import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
import argparse
import os

# ======================== 全局配置参数 ========================

# 设置请求头，模拟浏览器访问，避免被网站拒绝
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# 默认保存文件路径
DEFAULT_OUTPUT_PATH = "data/artic_chinese_artifacts.csv"

# 默认最大爬取页数（每页最多100条数据）
DEFAULT_MAX_PAGES = 10


# ======================== 功能函数定义 ========================

def get_artworks_from_api(page=1, limit=100):
    """
    从 AIC 的 API 获取与 "China" 关键词相关的文物列表（不包含详情）。
    :param page: 页码，从1开始
    :param limit: 每页最多获取的文物数（最大100）
    :return: 返回文物字典列表
    """
    url = "https://api.artic.edu/api/v1/artworks/search"
    params = {
        "q": "China",
        "page": page,
        "limit": limit,
        "fields": "id,title,date_display,image_id"  # 只请求需要的字段
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return []
    return response.json().get("data", [])


def construct_detail_url(art_id):
    """
    根据文物ID构造详情页链接
    """
    return f"https://www.artic.edu/artworks/{art_id}"


def construct_image_url(image_id):
    """
    根据 image_id 构造图像 URL，返回高清图链接
    """
    if image_id:
        return f"https://www.artic.edu/iiif/2/{image_id}/full/843,/0/default.jpg"
    return ""


def get_description_from_page(detail_url):
    """
    访问详情页并从 HTML 中提取文物描述（如有）
    """
    try:
        response = requests.get(detail_url, headers=HEADERS)
        soup = BeautifulSoup(response.text, "html.parser")
        desc_tag = soup.select_one(".m-article-text")  # CSS 选择器找简介段落
        if desc_tag:
            return desc_tag.get_text(strip=True)
    except Exception as e:
        print(f"❗️获取详情失败: {detail_url} 错误: {e}")
    return ""


def crawl_all_artworks(max_pages=5):
    """
    主爬虫逻辑：循环分页请求 API，并抓取详情页描述。
    :param max_pages: 最大爬取页数
    :return: 返回全部文物记录的列表（每条为一个字典）
    """
    all_data = []
    for page in range(1, max_pages + 1):
        print(f"📄 正在抓取第 {page} 页")
        artworks = get_artworks_from_api(page)
        if not artworks:
            break  # 如果为空，说明没内容了
        for art in artworks:
            detail_url = construct_detail_url(art["id"])
            description = get_description_from_page(detail_url)
            record = {
                "title": art.get("title", ""),
                "time": art.get("date_display", ""),
                "description": description,
                "detail_url": detail_url,
                "image_url": construct_image_url(art.get("image_id"))
            }
            all_data.append(record)
            print(f"  -> 抓取成功: {record['title'][:30]}...")
            time.sleep(0.5)  # 加一点延时，避免请求太快被封
    return all_data


def save_to_csv(data, filename):
    """
    将数据保存为 UTF-8 编码的 CSV 文件
    :param data: 文物数据列表（列表元素是字典）
    :param filename: 保存路径
    """
    # 自动创建目录（如果不存在）
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding="utf-8-sig")
    print(f"✅ 数据保存至：{filename}")


# ======================== 命令行主入口 ========================

def main():
    """
    命令行入口函数，支持用户传入参数控制保存路径和爬取页数
    """
    parser = argparse.ArgumentParser(description="爬取芝加哥艺术博物馆中与中国相关的文物信息")

    # 输出文件路径参数
    parser.add_argument(
        "--output",
        type=str,
        default=DEFAULT_OUTPUT_PATH,
        help=f"保存的 CSV 路径（默认: {DEFAULT_OUTPUT_PATH}）"
    )

    # 最大页数参数
    parser.add_argument(
        "--pages",
        type=int,
        default=DEFAULT_MAX_PAGES,
        help=f"最大爬取页数（默认: {DEFAULT_MAX_PAGES}）"
    )

    # 解析参数
    args = parser.parse_args()

    # 执行爬虫并保存结果
    data = crawl_all_artworks(max_pages=args.pages)
    save_to_csv(data, filename=args.output)


# 当此脚本被直接运行时，执行 main()
if __name__ == "__main__":
    main()
