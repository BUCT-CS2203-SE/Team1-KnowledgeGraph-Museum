import pandas as pd
import numpy as np
import re

df = pd.read_csv('datasets/Process_datas2.csv')

# 判断 ImgUrl 是否为空或为 NaN
df_with_img = df[df['ImgUrl'].notna() & (df['ImgUrl'].str.strip() != '')]
df_without_img = df[df['ImgUrl'].isna() | (df['ImgUrl'].str.strip() == '')]

# 保存到两个文件
df_with_img.to_csv('datasets/with_imgurl.csv', index=False)
df_without_img.to_csv('datasets/without_imgurl.csv', index=False)

df_with_img.replace('nan', np.nan, inplace=True)
df_without_img.replace('nan', np.nan, inplace=True)

# df.to_csv('datasets/Process_datas3.csv', index=False)
