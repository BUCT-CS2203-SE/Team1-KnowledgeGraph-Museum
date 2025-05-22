import pandas as pd
import numpy as np
import re


# 替换逻辑：逐行替换每个匹配项
def replace_names(text):
    for eng, zh in replacements.items():
        text = re.sub(re.escape(eng), zh, text)
    return text


df = pd.read_csv('datasets/Process_datas1_1.csv')

# df['Title'] = df['Title'].str.replace(r'\s*\(.*?\)', '', regex=True)
df['Title'] = df['Title'].apply(
    lambda x: re.search(r'[\u4e00-\u9fff].*$',
    str(x)).group() if re.search(r'[\u4e00-\u9fff].*$', str(x)) else x)

replacements = {
    # "Manchu\nChina": 'Manchu',
    # 'Manchu, China': 'Manchu',
    # 'Chen Wu 陳武': '陳武',
    # 'Zhu Lunhan 朱倫瀚': '朱倫瀚',
    # 'Yao Luan 姚鑾': '姚鑾',

    "Fang Jiekan": "方介堪",
    "Walasse Ting": "丁雄泉",
    "Manchu": '满族',
    'Shanchun Yan': '阎善春',
    'DoDo Jin Ming': '金旻',
    'Tai Xiangzhou': '泰祥洲',
    'Wucius Wong': '王無邪',
    'Little Flower Miao': '小花苗族',
    'Gejia Miao': '革家苗族',
    'Miao': '苗族',
    'Zhou Leyuan': '周樂元',
    'Long-Horned Miao': '长角苗族',
    'Xugu': '虛谷',
    'Ren Yi': '任頤',
    'Hung Liu': '刘虹',
    'Irene Chow': '周绿云',
    'Kong Pak-yu': '江伯宇',
    'Mi Guangjiang (Haji Noor Deen)': '米广江',
    'Chang Dai-chien (Zhang Daqian; Chinese, 1899 - 1983)': '張大千 (China, 1899-1983)',
    'Zhang Daqian (1899-1983)': '張大千 (China, 1899-1983)',
    'Zhang Renjun ': '张人骏',
    'Lin Fengmian': '林风眠',
    'Wu Guanzhong': '吴冠中',
    'Yang Yanping': '杨燕屏',
    'Henry Wo Yue Kee': '胡宇基',
    'Fang Zhaoling': '方召麐',
    'C. C. Wang': '王己千',
    'Pu Ru': '溥心畬',
    'Chang Shangpu': '张尚璞',
    'Chao Shao-an': '赵少昂',
    'Au Ho-nien': '欧豪年',
    'Lu Wu-Chiu': '呂無咎',
    'Weng Fanggang': '翁方纲',
    'Cai Heng': '蔡珩',
    'Chen Chun': '陳淳',
    'Cheng Jiezi': '程芥子',
    'Gong Xian': '龚贤',
    'Guanxiu': '貫休',
    'Hua Yan': '华嵒',
    'Huang Binhong': '黄宾虹',
    'Jade Snow Wong': '黄玉雪',
    'Zou Zhe': '徐釚',
    'Lan Ying': '藍瑛',
    'Liu Guosong': '刘国松',
    'Liu Zheng': '刘铮',
    'Lu Yuan': '陆远',
    'Lu Can': '陆灿',
    'Pan Gongkai': '潘公凯',
    'Qi Baishi (Chinese, 1863 - 1957)': '齊白石 (1864-1957)',
    'Qiu Ying (Chinese, 1494-1552)': '仇英 (Chinese, 1494-1552)',
    'Shitao': '石涛',
    'Song Yulin': '宋玉麟',
    'Wang Yachen': '汪亚尘',
    'Wanxin Zhang': '張萬新',
    'Wen Zhengming (Chinese, 1470 - 1559)': '文徵明 (Chinese, 1470-1559)',
    'Wu Zijian': '吴子建',
    'Xiang Shengmo': '项圣谟',
    'Ye Gongchao': '叶公超',
    'Ye Yanlan': '叶衍兰',
    'Yun Bing': '恽冰',
    'Zhang Peili': '张培力',
    'Zhou Dingfang': '周定芳',
    'Zhou Zhimian': '周之冕',
    'Chen Mingyuan': '陈鸣远',
    'Cheng Shifa': '程十发',
    'Gu Kui': '顾恺',
    'Gu Luo': '顾洛',
    'Hai Bo': '海波',
    'Han Gan': '韩幹',
    'Hongren': '弘仁',
    'Huang Junbi': '黄君璧',
    'Huang Zhou': '黄胄',
    'Jiang Eshi': '蒋谔士',
    'Jiang Zhaoshen': '江兆申',
    'John Way': '魏樂唐',
    'Sun Kehong': '孙克弘',
    'Wang Dongling, born 1945（Chinese）': 'Wang Dongling（Chinese）',
    'Wu Ping': '吳平',
    'Wu Zhang': '吴章',
    '王無邪 (Chinese, born. 1936)': '王無邪（Chinese, born 1936）',
    '歐豪年 (born 1935)': '欧豪年 (Chinese, 1935 - 2024)',
    '杨燕屏（Chinese, born 1934）': '杨燕屏 (Chinese, born. 1934)',
    '陸? (Chinese, active c. 1685-1715)': '陸 (Chinese, active c. 1685-1715)',
    '盛懋 (ca. 1310-1360)': '盛懋（Chinese (1310-1360)）',
    '虛谷 (Chinese, 1824-1896)': '虛谷 (Chinese, 1823-1896)',

}
df['Artist'] = df['Artist'].astype(str).apply(replace_names)

# 更改换行
# df['Artist'] = df['Artist'].str.replace(r'\n(.*)', r'（\1）', regex=True)
df['Artist'] = df['Artist'].apply(
    lambda x: np.nan if str(x).strip().lower() in ['', 'Anonymous friend of the Asian Art Museum'] else x
)
# df['Artist'].replace('nan', np.nan, inplace=True)

# print(df['Artist'].unique())

df.insert(0, 'id', range(1, len(df) + 1))

# 提取 Artist 中空格前或右括号前的名字，放入 OnlyArtist 列
df['OnlyArtist'] = df['Artist'].astype(str).str.extract(r'^(.+?)\s*\(')
df.replace('nan', np.nan, inplace=True)

df.to_csv('datasets/Process_datas2.csv', index=False)
