import pandas as pd

# 读取两个 CSV 文件
df1 = pd.read_csv('datasets/spider_Chicago.csv')

df_filtered = df1
df_filtered['Museum'] = 'The Art Institute of Chicago'


# 将处理后的数据保存到新文件
df_filtered.to_csv('datasets/Combine_Chicago.csv', index=False)

print("处理完成，新的 CSV 文件已保存为 'Combine_Asian.csv'")

# 获取总行数
total_rows = len(df_filtered)

print(f"文件中共有 {total_rows} 行")

