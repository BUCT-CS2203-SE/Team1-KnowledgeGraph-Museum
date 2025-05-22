import pandas as pd
import numpy as np
import re


# 替换逻辑：逐行替换每个匹配项
def replace_names(text):
    for eng, zh in replacements.items():
        text = re.sub(re.escape(eng), zh, text)
    return text


df = pd.read_csv('datasets/Clean_datas.csv')

df['Title'] = df['Title'].str.replace(r'\s*\(.*?\)', '', regex=True)

replacements = {
    "Manchu\nChina": 'Manchu',
    'Manchu, China': 'Manchu',
    'Chen Wu 陳武': '陳武',
    'Zhu Lunhan 朱倫瀚': '朱倫瀚',
    'Yao Luan 姚鑾': '姚鑾',

    #     "Fang Jiekan": "方介堪",
    #     "Walasse Ting": "丁雄泉",
    #     "Manchu": '满族',
    # 'Shanchun Yan':'阎善春',
    #     'DoDo Jin Ming':'金旻',
    # 'Tai Xiangzhou':'泰祥洲',
    # 'Wucius Wong:'王無邪',
    # 'Little Flower Miao':'小花苗族',
    # 'Gejia Miao':'革家苗族',
    # 'Miao':'苗族',
    # 'Long-Horned Miao':'长角苗族',
    # 'Xugu:'虛谷',
    # 'Ren Yi':'任頤'
    # 'Chang Dai-chien (Zhang Daqian; Chinese, 1899 - 1983)':'張大千 (China, 1899-1983)',
    #
}
df['Artist'] = df['Artist'].astype(str).apply(replace_names)
df['Artist'] = df['Artist'].apply(
    lambda x: np.nan if str(x).strip().lower() in ['han-chinese\nchina', 'artist unknown (chinese, 19th century)',
                                                   'chinese', 'china; probably shaanxi province', 'china',
                                                   'artist unknown\nchinese', 'china or korea', 'china or japan',
                                                   'possibly china', 'china, qishan county, shaanxi province',
                                                   'probably shaanxi province, china\nbronze',
                                                   'china, for the thai market'
                                                   'china, qishan county\nshaanxi province',
                                                   'northern china or eurasian steppes',
                                                   'china, for the european market'
                                                   'northern china or inner mongolia', 'northeastern china',
                                                   'china or mongolia', 'japan or china', 'artist unknown'
                                                                                          'artist unknown (chinese, made for the american market)\nchina',
                                                   'possibly china','china, for the thai market'] else x
)
# 更改换行
df['Artist'] = df['Artist'].str.replace(r'\n(.*)', r'（\1）', regex=True)
df['Artist'].replace('nan', np.nan, inplace=True)

# print(df['Artist'].unique())

df.to_csv('datasets/Process_datas1.csv', index=False)
