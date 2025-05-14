import pandas as pd

# 读取CSV文件
df = pd.read_csv('../datasets_museum/asian_try.csv')

df['museum'] = '旧金山亚洲艺术博物馆'

# # 保存到新文件（或覆盖原文件）
# df.to_csv('datasets_museum/china.csv', index=False)

merged_df = pd.concat([df], ignore_index=True, sort=False).fillna('NULL')

# 保存合并后的 CSV 文件
merged_df.to_csv("../datasets_museum/china.csv", index=False)

import csv

# 输入CSV文件路径
input_csv = '../datasets_museum/china.csv'  # 替换为你的输入CSV文件路径
output_csv = '../datasets_museum/china_triple.csv'  # 输出三元组CSV文件

# 三元组列表
triplets = []

# 读取CSV文件
with open(input_csv, 'r', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        title = row['Title']
        time = row['Dynasty']
        artist = row['Artist']
        material = row['Materials']
        dimensions = row['Dimensions']
        category = row['Classifications']
        museum = row['museum']

        # 生成三元组
        if time and time != "NULL":
            triplets.append((title, '处于的年代', time))
        if artist and artist != "NULL":
            triplets.append((title, '创作者为', artist))
        if material and material != "NULL":
            triplets.append((title, '材质为', material))
        if dimensions and dimensions != "NULL":
            triplets.append((title, '尺寸为', dimensions))
        if category and category != "NULL":
            triplets.append((title, '类型为', category))
        if museum and museum != "NULL":
            triplets.append((title, '位于', museum))

# 保存三元组到新的CSV文件
with open(output_csv, 'w', encoding='utf-8', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['subject', 'predicate', 'object'])  # 三元组表头
    writer.writerows(triplets)

print(f"三元组已成功生成并保存为 {output_csv}")