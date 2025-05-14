import pandas as pd

# 读取两个 CSV 文件
df1 = pd.read_csv('datasets/asian_chinese.csv')
df2 = pd.read_csv('datasets/asian_china.csv')

# 合并两个 DataFrame，忽略重复的行
merged_df = pd.concat([df1, df2]).drop_duplicates(
    subset=['Img_url'], keep='first')
# merged_df = df1.drop_duplicates(
#     subset=['Img_url'], keep='first')

# 筛选 Department 列为 "Chinese" 的行
df_chinese = merged_df[merged_df['Department'] == 'Chinese Art']
# df_chinese=merged_df

# 选择需要保留的列，这里假设你只保留 'title' 和 'Artist' 列
df_filtered = df_chinese

# 将处理后的数据保存到新文件
df_filtered.to_csv('datasets/Combine_Asian.csv', index=False)

print("处理完成，新的 CSV 文件已保存为 'Combine_Asian.csv'")

# 获取总行数
total_rows = len(df_filtered)

print(f"文件中共有 {total_rows} 行")

