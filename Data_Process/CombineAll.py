# import pandas as pd
#
# # 读取两个 CSV 文件
# df1 = pd.read_csv('datasets/smithsonian.csv')
# df2 = pd.read_csv('datasets/smithsonian_objects2.0.csv')
# df3 = pd.read_csv('datasets/smithsonian_objects3.0.csv')
#
# # 合并两个 DataFrame，忽略重复的行
# dfa = df1[
#     ["Img_path", "Credit Line", "Portfolio", "Materials", "Artist", "Markings", "Publisher", "On View", "Department",
#      "School", "Date", "Inscribed", "Classifications", "Signed", "(not entered)", "Dynasty", "More Information",
#      "Img_url", "Dimensions", "Composer", "Printer", "Object number", "Place of Origin", "Period", "Culture",
#      "Provenance Statement", "Title"
#      ]]
# dfb = df2[["Title", "Artist", "Place of Origin", "Date", "Material", "Dimensions", "Credit Line",
#            "Type", "Style", "On View", "inscribed/Inscripions", "Description", "save_path", "Image URL",
#            "Medium"
#            ]]
# dfc = df3[["title", "artist_display", "date_display", "place_of_origin", "category_titles", "description",
#            "medium_display", "dimensions", "provenance_text", "exhibition_history", "publication_history",
#            "credit_line", "department_title", "style_title", "artwork_type_title", "technique_titles", "subject_titles",
#            "image_url", "image_path"
#            ]]
# all_df = pd.concat([df1, df2, df3])
#
# none_df = all_df[all_df['Image URL'] == '无图片']
# non_none_df = all_df[all_df['Image URL'] != '无图片'].drop_duplicates(subset=['Image URL'], keep='first')
# merged_df = pd.concat([none_df, non_none_df], ignore_index=True)
#
# # 将处理后的数据保存到新文件
# merged_df.to_csv('datasets/Combine_Smith.csv', index=False)
#
# print("处理完成，新的 CSV 文件已保存为 'Combine_Smith.csv'")
#
# # 获取总行数
# total_rows = len(merged_df)
#
# print(f"文件中共有 {total_rows} 行")

import pandas as pd

# 读取标准化后的 CSV 文件
csv1 = pd.read_csv('datasets/Combine_Asian.csv')
csv2 = pd.read_csv('datasets/Combine_Smith.csv')
csv3 = pd.read_csv('datasets/Combine_Chicago.csv')

# 统一列名映射字典
rename_map1 = {
    'Img_path': 'ImgPath',
    'Credit Line': 'CreditLine',
    'Title': 'Title',
    'Artist': 'Artist',
    'Dynasty': 'Dynasty',
    'Dimensions': 'Dimensions',
    'Img_url': 'ImgUrl',
    "Materials": 'Materials',
    'More Information': 'Description',
    'Museum': 'Museum',
    'Place of Origin': 'PlaceOri',
    "Inscribed": 'Inscribed',
    "Classifications": 'Classifications',
}
rename_map2 = {
    'save_path': 'ImgPath',
    'Credit Line': 'CreditLine',
    'Title': 'Title',
    'Artist': 'Artist',
    'Date': 'Dynasty',
    'Dimensions': 'Dimensions',
    'Image URL': 'ImgUrl',
    'Description': 'Description',
    'Museum': 'Museum',
    "Material": 'Materials',
    'Place of Origin': 'PlaceOri',
    "inscribed/Inscripions": "Inscribed",
    "Type": 'Classifications',
    "Medium": 'Medium',
}
rename_map3 = {
    'image_path': 'ImgPath',
    'credit_line': 'CreditLine',
    'title': 'Title',
    'artist_display': 'Artist',
    'date_display': 'Dynasty',
    'dimensions': 'Dimensions',
    'image_url': 'ImgUrl',
    'description': 'Description',
    'Museum': 'Museum',
    'place_of_origin': 'PlaceOri',
    "medium_display": 'Medium',
    "artwork_type_title": 'Classifications',

}

# 重命名列
df1 = csv1.rename(columns=rename_map1)
df2 = csv2.rename(columns=rename_map2)
df3 = csv3.rename(columns=rename_map3)

# 选取要保留的标准列（取三份文件中共有的字段合集）
standard_columns = [
    'Title', 'Artist', 'Dynasty', 'CreditLine', 'Dimensions',
    'ImgPath', 'ImgUrl', 'Materials', 'Description', 'Museum',
    'PlaceOri', 'Inscribed', 'Classifications', 'Medium'
]

# 补齐缺失列（防止 concat 时出现列不对齐）
for df in [df1, df2, df3]:
    for col in standard_columns:
        if col not in df.columns:
            df[col] = None  # 填充为空

# 合并
merged_df = pd.concat([df1[standard_columns], df2[standard_columns], df3[standard_columns]], ignore_index=True)

# 保存合并后的文件
merged_df.to_csv('datasets/All_datas.csv', index=False)
print("✅ 合并成功，已保存为 All_datas.csv")
