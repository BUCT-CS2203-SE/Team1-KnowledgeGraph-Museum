import hashlib
import random
import pandas as pd
import requests
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''

# appid = "20250522002363187"
# secretKey = "uVQ0COTEyYIp1wRHcEHA"

appid = '20250509002353080'
secretKey = 'sxYw_exsiT4we7mCXoEx'


translated_path = "datasets/baidu_wiki.csv"


def translate(text, from_lang="auto", to_lang="zh", max_retries=3):
    for attempt in range(max_retries):
        try:
            if not isinstance(text, str) or not text.strip():
                return ""
            salt = random.randint(32768, 65536)
            sign = hashlib.md5((appid + text + str(salt) + secretKey).encode()).hexdigest()
            params = {
                "q": text,
                "from": from_lang,
                "to": to_lang,
                "appid": appid,
                "salt": salt,
                "sign": sign,
                "domain": "wiki"
            }
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            response = requests.post("https://fanyi-api.baidu.com/api/trans/vip/translate",
                                     data=params, headers=headers, timeout=10)
            result = response.json()
            if "error_code" in result:
                print(f"百度翻译API错误：{result.get('error_msg')} (code {result.get('error_code')})")
                return ""
            if 'trans_result' in result:
                return result['trans_result'][0]['dst']
        except Exception as e:
            print(f"翻译失败（尝试 {attempt + 1}）：{text[:30]}... 错误: {e}")
            time.sleep(1)
    return ""  # 最后失败就保留原文


if os.path.exists(translated_path):
    df_translated = pd.read_csv(translated_path, dtype=str)
    translated_ids = set(df_translated['id'].astype(str))
    print(f"检测到已有 {len(translated_ids)} 行已翻译，自动跳过。")
else:
    df_translated = pd.DataFrame()
    translated_ids = set()

df = pd.read_csv("datasets/Process_time.csv", dtype=str).head(1)
translate_columns = [col for col in df.columns if
                     col not in ['ImgUrl', 'ImgPath', 'main_start', 'main_end', 'sub_start', 'sub_end']]

# 初始化翻译 DataFrame（与原始 df 大小一致）
if df_translated.empty:
    df_translated = pd.DataFrame(index=df.index, columns=translate_columns)

to_translate = df[~df['id'].isin(translated_ids)]


def translate_row(row):
    row_id = row['id']
    translated = {"id": row_id}
    for col in translate_columns:
        val = row[col]
        if pd.isna(val):
            translated[col] = ""
            # print(val)
        else:
            translated[col] = translate(val)
            # print(translated[col])
        time.sleep(1)
    return translated


# 多线程翻译
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = {executor.submit(translate_row, row): row['id'] for _, row in to_translate.iterrows()}

    for i, future in enumerate(as_completed(futures), 1):
        result = future.result()
        df_translated = pd.concat([df_translated, pd.DataFrame([result])], ignore_index=True)
        if result['id'] == '' or pd.isna(result['id']):
            continue
        print(f"✅ 完成第 {i} 行 id={result['id']}")
        # print(result)

        # 将结果转为一行 DataFrame 追加写入文件
        pd.DataFrame([result]).to_csv(translated_path, mode='a', index=False,
                                      header=not os.path.exists(translated_path))

# 最终保存
df_translated.to_csv(translated_path, index=False)
print("🎉 所有翻译已完成并保存至", translated_path)
