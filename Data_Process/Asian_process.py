import pandas as pd

# 读取两个 CSV 文件
df1 = pd.read_csv('origin/objects_chinese.csv')
df2 = pd.read_csv('origin/objects_china.csv')

# 合并两个 DataFrame，忽略重复的行
merged_df = pd.concat([df1, df2]).drop_duplicates(
    subset=['Object number'], keep='first')

# 将去重后的数据保存到新的 CSV 文件
merged_df.to_csv('merged_no_duplicates.csv', index=False)

print("去重完成并保存为 'merged_no_duplicates.csv'")

# 筛选 Department 列为 "Chinese" 的行
df_chinese = merged_df[merged_df['Department'] == 'Chinese Art']

# 选择需要保留的列，这里假设你只保留 'title' 和 'Artist' 列
df_filtered = df_chinese
# df_filtered = df_chinese[
#     ['Title', 'Date', 'Artist', 'Img_path', 'Img_url', 'Period', 'Credit Line', 'Materials', 'On View',
#      'Classifications']]

# 更改列名
# df_filtered.rename(columns={'Title': '标题', 'Artist': '艺术家'}, inplace=True)

# 将处理后的数据保存到新文件
df_filtered.to_csv('asian_museum.csv', index=False)

print("处理完成，新的 CSV 文件已保存为 'asian_museum.csv'")

# 获取总行数
total_rows = len(df_filtered)

print(f"文件中共有 {total_rows} 行")

