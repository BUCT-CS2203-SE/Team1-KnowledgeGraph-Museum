import pandas as pd
import numpy as np
import re

df = pd.read_csv('datasets/Process_end2.csv')

# def replace_names(text):
#     for eng, zh in replacements.items():
#         text = re.sub(re.escape(eng), zh, text)
#     return text
#
#
# replacements = {
#     "10th-11th century": "10至11世纪",
#     "10th-12th century": '10至12世纪',
#
# }
# df['Artist'] = df['Artist'].astype(str).apply(replace_names)
# df.replace('nan', np.nan, inplace=True)

df = df.sort_values(by='id', ascending=True)

int_cols = ['id', 'main_start', 'main_end', 'sub_start', 'sub_end']

for col in int_cols:
    if col in df.columns:
        for idx, row in df.iterrows():
            value = row[col]
            if pd.notna(value):
                try:
                    df.at[idx, col] = str(int(float(value)))
                except Exception:
                    pass

# 判断 ImgPath 是否为空或为 NaN
df_with_img = df[df['ImgPath'].notna() & (df['ImgPath'].str.strip() != '')]
df_without_img = df[df['ImgPath'].isna() | (df['ImgPath'].str.strip() == '')]

df_with_img['ImgPath'] = '/home/ImageSets/' + df_with_img['ImgPath'].astype(str)

df_with_img.replace('nan', np.nan, inplace=True)
df_without_img.replace('nan', np.nan, inplace=True)

# 保存到两个文件
df_with_img.to_csv('datasets/Data_with_img.csv', index=False)
df_without_img.to_csv('datasets/Data_without_img.csv', index=False)

# df.to_csv('datasets/Process_datas3.csv', index=False)
