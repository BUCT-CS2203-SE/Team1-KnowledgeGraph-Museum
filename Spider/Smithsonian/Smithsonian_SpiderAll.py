import requests
from bs4 import BeautifulSoup
import csv

headers = {
    "User-Agent": "Mozilla/5.0"
}

urls = [
    "https://www.si.edu/object/boxing-headgear-worn-muhammad-ali:nmaahc_2010.19.1",
    "https://www.si.edu/object/orbiter-space-shuttle-ov-103-discovery:nasm_A20120325000",
    "https://www.si.edu/object/dorothys-ruby-slippers:nmah_670130"
    #此处可以继续添加url

]

def extract_data(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    data = {"URL": url}

    # 标题
    title_tag = soup.find("h1")
    data["Title"] = title_tag.text.strip() if title_tag else "无标题"

    # 图片链接
    img_tag = soup.find("img", id="edan-image")
    data["Image URL"] = img_tag["src"].replace("&amp;", "&") if img_tag and img_tag.get("src") else "无图片"

    # 提取字段的通用函数
    def add_fields(class_name):
        block = soup.find("dl", class_=class_name)
        if block:
            dts = block.find_all("dt")
            dds = block.find_all("dd")
            for dt, dd in zip(dts, dds):
                key = dt.get_text(strip=True)
                value = dd.get_text(strip=True)
                data[key] = value

    add_fields("field field-freetextname")
    add_fields("field field-freetextnotes")
    add_fields("field field-freetextcreditline")
    add_fields("field field-freetextobjecttype")
    add_fields("field field-freetextphysicaldescription")
    add_fields("field field-freetextdate")


    return data

# 扫描所有链接
all_data = [extract_data(url) for url in urls]

# 定义想要的列的顺序
preferred_fields = [
    "URL",
    "Title",
    "Image URL",
    "Period",
    "Origin",
    "Created by",
    "Owned by",
    "Description",
    "Object Type",
    "Credit Line",
    "Physical Description"
]
# 从所有数据中补充出现的新字段（非首选字段）
all_keys = set()
for d in all_data:
    all_keys.update(d.keys())

# 把没有出现在 preferred_fields 中的字段加进去
remaining_fields = [key for key in all_keys if key not in preferred_fields]

# 最终的字段顺序
fieldnames = preferred_fields + remaining_fields


# 保存为 CSV 文件
filename = "smithsonian_objects.csv"
with open(filename, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for item in all_data:
        writer.writerow(item)

print(f"✅ 所有对象信息已保存到：{filename}")


