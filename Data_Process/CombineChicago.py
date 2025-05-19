import pandas as pd
import numpy as np

# 读取两个 CSV 文件
df1 = pd.read_csv('datasets/spider_Chicago.csv')

df_filtered = df1
df_filtered['Museum'] = 'The Art Institute of Chicago'
df_filtered['artist_display'] = df_filtered['artist_display'].apply(
    lambda x: np.nan if str(x).strip().lower() in ['artist unknown (chinese)', 'china','artist unknown\nchinese','china or korea'] else x
)


# 将处理后的数据保存到新文件
df_filtered.to_csv('datasets/Combine_Chicago.csv', index=False)

print("处理完成，新的 CSV 文件已保存为 'Combine_Asian.csv'")

# 获取总行数
total_rows = len(df_filtered)

print(f"文件中共有 {total_rows} 行")

