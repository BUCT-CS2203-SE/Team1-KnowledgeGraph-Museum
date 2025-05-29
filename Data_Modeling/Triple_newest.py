import pandas as pd
import re
import csv

# 加载 CSV
df = pd.read_csv("../Process_ALL/datasets/Process_end2.csv")

# 三元组列表
triples = []

def normalize(value: str, prefix: str):
    """给实体加前缀，空值返回 None"""
    if pd.isna(value) or not str(value).strip():
        return None
    return f"{value.strip()}"

def split_multi_values(value):
    if pd.isna(value):
        return []
    return [v.strip() for v in re.split(r'[；;，,、/]', str(value)) if v.strip()]

# 遍历每一行数据
for _, row in df.iterrows():
    art_id = str(row["id"])
    subj = f"{art_id}"

    # 基本属性（作为 node 属性可选，或三元组也行）
    attr_map = {
        "Title": "标题是",
        "Artist": "艺术家名是",
        "Dynasty": "朝代名是",
        "CreditLine": "收藏来源",
        "Dimensions": "尺寸描述",
        "Materials": "材质描述",
        "Description": "描述信息",
        "Inscribed": "铭文信息",
        "Museum": "博物馆名是",
        "PlaceOri": "来源地名是",
        "Classifications": "类型描述",
        "Medium": "媒介描述"
    }
    # for col, pred in attr_map.items():
    #     val = row.get(col)
    #     if pd.notna(val) and str(val).strip():
    #         triples.append((subj, pred, str(val).strip()))

    # 艺术家节点关联
    artist = row.get("OnlyArtist")
    if pd.notna(artist):
        artist_obj = normalize(artist, "Artist")
        if artist_obj:
            triples.append((subj, "创作者是", artist_obj))

    # 朝代节点关联
    dynasty = row.get("periods")
    if pd.notna(dynasty):
        for d in split_multi_values(dynasty):
            d_obj = normalize(d, "Dynasty")
            if d_obj:
                triples.append((subj, "创造年代是", d_obj))

    # 尺寸节点
    dim = row.get("Dimensions")
    if pd.notna(dim):
        d_obj = normalize(dim, "Dimension")
        triples.append((subj, "尺寸是", d_obj))

    # 材质节点
    materials = row.get("Materials")
    if pd.notna(materials):
        for mat in split_multi_values(materials):
            m_obj = normalize(mat, "Material")
            if m_obj:
                triples.append((subj, "材质是", m_obj))

    # 博物馆节点
    museum = row.get("Museum")
    if pd.notna(museum):
        m_obj = normalize(museum, "Museum")
        triples.append((subj, "现藏博物馆是", m_obj))

    # 来源地节点
    place = row.get("PlaceOri")
    if pd.notna(place):
        p_obj = normalize(place, "PlaceOri")
        triples.append((subj, "来源地是", p_obj))

    # 类型节点
    cls = row.get("Classifications")
    if pd.notna(cls):
        c_obj = normalize(cls, "Classification")
        triples.append((subj, "类型是", c_obj))

    # 媒介节点
    mediums = row.get("Medium")
    if pd.notna(mediums):
        for med in split_multi_values(mediums):
            m_obj = normalize(med, "Medium")
            if m_obj:
                triples.append((subj, "媒介是", m_obj))

# 输出为 CSV 文件
with open("artifact_triples.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["subject", "predicate", "object"])
    writer.writerows(triples)

print(f"导出完成，共 {len(triples)} 条三元组。")
