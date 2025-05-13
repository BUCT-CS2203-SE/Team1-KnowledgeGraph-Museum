import json
import os
import csv
import requests
from urllib.parse import urljoin
from tqdm import tqdm  # 导入进度条库

# 配置参数
json_folder = "D:/Desktop/artworks"  # JSON文件所在目录（当前目录）
output_csv = "chinese_artworks.csv"
image_dir = "chinese_art_images"  # 图片存储目录
progress_file = "progress.txt"  # 进度记录文件
os.makedirs(image_dir, exist_ok=True)  # 确保图片目录存在

# 所需字段（增加image_path）
fields = [
    "id", "title", "artist_display", "date_display", "place_of_origin",
    "category_titles", "description", "medium_display", "dimensions",
    "provenance_text", "exhibition_history", "publication_history",
    "credit_line", "department_title", "style_title", "artwork_type_title",
    "technique_titles", "subject_titles", "image_url", "image_path"
]

# 初始化变量
china_artworks = []
china_artworks_count = 0
image_counter = 1  # 图片计数器，用于生成唯一文件名


# 读取进度
def read_progress():
    """读取上次处理的进度"""
    if os.path.exists(progress_file):
        with open(progress_file, "r") as f:
            try:
                return int(f.read().strip())
            except:
                return 0
    return 0


# 保存进度
def save_progress(file_index):
    """保存当前处理进度"""
    with open(progress_file, "w") as f:
        f.write(str(file_index))


# 获取已处理的图片数量（用于image_counter）
def get_image_counter():
    """获取当前图片计数器值"""
    if os.path.exists(image_dir):
        existing_images = [f for f in os.listdir(image_dir) if f.endswith('.jpg')]
        if existing_images:
            max_num = max([int(f.split('.')[0]) for f in existing_images])
            return max_num + 1
    return 1


def download_image(image_url, save_path):
    """下载图片并保存到指定路径"""
    try:
        response = requests.get(image_url, stream=True, timeout=10)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return True
    except Exception as e:
        print(f"下载图片失败: {e}")
    return False


# 读取已处理的记录ID，避免重复处理
def get_processed_ids():
    """获取CSV中已处理的记录ID"""
    processed_ids = set()
    if os.path.exists(output_csv):
        with open(output_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                processed_ids.add(row["id"])
    return processed_ids


# 初始化进度
last_processed_index = read_progress()
processed_ids = get_processed_ids()
image_counter = get_image_counter()

# 获取排序后的文件列表
file_list = sorted([f for f in os.listdir(json_folder) if f.endswith(".json")])

# 创建进度条
progress_bar = tqdm(
    enumerate(file_list, start=1),
    total=len(file_list),
    initial=last_processed_index,
    desc="处理进度",
    unit="文件",
    dynamic_ncols=True
)

# 遍历JSON文件
for file_index, filename in progress_bar:
    # 跳过已处理的文件
    if file_index <= last_processed_index:
        continue

    filepath = os.path.join(json_folder, filename)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"\n解析JSON文件失败: {filename} - {e}")
        save_progress(file_index)  # 记录进度
        continue

    # 检查是否已处理过
    artwork_id = str(data.get("id", ""))
    if artwork_id in processed_ids:
        save_progress(file_index)  # 记录进度
        continue

    # 检查是否中国文物
    place_of_origin = str(data.get("place_of_origin", "")).lower()
    if "china" not in place_of_origin and "chinese" not in place_of_origin:
        save_progress(file_index)  # 记录进度
        continue

    # 获取图片URL
    image_id = data.get("image_id")
    image_url = f"https://www.artic.edu/iiif/2/{image_id}/full/843,/0/default.jpg" if image_id else ""

    # 下载图片并生成路径
    image_path = ""
    if image_url:
        image_filename = f"{image_counter}.jpg"
        image_counter += 1
        image_path = os.path.join(image_dir, image_filename)

        if not download_image(image_url, image_path):
            print(f"\n⚠️ 图片下载失败: {image_url}")
            image_path = ""  # 下载失败时清空路径

    # 构建记录
    record = {
        "id": data.get("id"),
        "title": data.get("title"),
        "artist_display": data.get("artist_display"),
        "date_display": data.get("date_display"),
        "place_of_origin": data.get("place_of_origin"),
        "category_titles": "; ".join(data.get("category_titles", [])),
        "description": data.get("description") or (data.get("thumbnail") and data["thumbnail"].get("alt_text", "")),
        "medium_display": data.get("medium_display"),
        "dimensions": data.get("dimensions"),
        "provenance_text": data.get("provenance_text"),
        "exhibition_history": data.get("exhibition_history"),
        "publication_history": data.get("publication_history"),
        "credit_line": data.get("credit_line"),
        "department_title": data.get("department_title"),
        "style_title": data.get("style_title"),
        "artwork_type_title": data.get("artwork_type_title"),
        "technique_titles": "; ".join(data.get("technique_titles", [])),
        "subject_titles": "; ".join(data.get("subject_titles", [])),
        "image_url": image_url,
        "image_path": image_path  # 存储相对路径
    }

    china_artworks.append(record)
    china_artworks_count += 1
    processed_ids.add(artwork_id)  # 添加到已处理集合

    # 更新进度条描述
    progress_bar.set_postfix({
        "已处理": china_artworks_count,
        "当前文件": filename[:15] + "..." if len(filename) > 15 else filename
    })

    # 每10条写入一次CSV
    if len(china_artworks) == 10:
        write_header = not os.path.exists(output_csv)
        with open(output_csv, "a", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            if write_header:
                writer.writeheader()
            writer.writerows(china_artworks)
        progress_bar.write(f"已保存 {len(china_artworks)} 条记录到 {output_csv}")
        china_artworks = []

    # 保存进度
    save_progress(file_index)

# 写入剩余记录
if china_artworks:
    write_header = not os.path.exists(output_csv)
    with open(output_csv, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        if write_header:
            writer.writeheader()
        writer.writerows(china_artworks)
    print(f"\n已保存 {len(china_artworks)} 条记录到 {output_csv}")

print(f"\n处理完成！共找到 {china_artworks_count} 件中国文物。")
print(f"图片保存在 {image_dir} 目录中，共下载 {image_counter - 1} 张图片。")