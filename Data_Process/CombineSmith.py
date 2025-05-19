import pandas as pd
import numpy as np

# 读取两个 CSV 文件
df1 = pd.read_csv('datasets/smithsonian.csv')
df2 = pd.read_csv('datasets/smithsonian_objects2.0.csv')
df3 = pd.read_csv('datasets/smithsonian_objects3.0.csv')
df4 = pd.read_csv('datasets/smithsonian_objects4.0.csv')
df5 = pd.read_csv('datasets/smithsonian_objects5.0.csv')
df6 = pd.read_csv('datasets/smithsonian_objects6.0.csv')
df7 = pd.read_csv('datasets/smithsonian_objects7.0.csv')

# 合并两个 DataFrame，忽略重复的行
all_df = pd.concat([df1, df2, df3, df4, df5, df6, df7])

none_df = all_df[all_df['Image URL'] == '无图片']
none_df['Image URL'].replace(['无图片', '无', ''], np.nan, inplace=True)
non_none_df = all_df[all_df['Image URL'] != '无图片'].drop_duplicates(subset=['Image URL'], keep='first')
merged_df = pd.concat([none_df, non_none_df], ignore_index=True)
merged_df['Museum'] = 'Smithsonian Institution'

# 将处理后的数据保存到新文件
merged_df.to_csv('datasets/Combine_Smith.csv', index=False)

print("处理完成，新的 CSV 文件已保存为 'Combine_Smith.csv'")

# 获取总行数
total_rows = len(merged_df)

print(f"文件中共有 {total_rows} 行")

