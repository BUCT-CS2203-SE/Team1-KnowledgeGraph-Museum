import pandas as pd
import requests
import concurrent.futures
import os
import time

# DeepSeek Chat API 配置
API_URL = "https://api.deepseek.com/chat/completions"
API_KEY = "sk-cc7dfaf168f14940921cdc3866ff51de"

import re

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}


# 判断是否为中文
def is_chinese(text):
    text = str(text).strip()
    if not text:
        return False
    return all('\u4e00' <= ch <= '\u9fff' for ch in text)


# 不需要翻译的列
SKIP_COLS = ['ImgUrl', 'ImgPath', 'main_start', 'main_end', 'id', 'sub_start', 'sub_end']


# 翻译
def translate_deepseek(text):
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system",
             "content": "你是一个中英文翻译助手。请将英文翻译为中文。如果输入本身是中文，则原样返回。只返回翻译后的文本，不要任何解释。"},
            {"role": "user", "content": text}
        ],
        "temperature": 0.2
    }
    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"翻译失败：{e}")
        return text

def process_row(index, row, translated_df):
    new_row = row.copy()
    row_id = str(row['id'])
    for col in row.index:
        if col in SKIP_COLS:
            continue
        val = row[col]
        if pd.isna(val):  # 跳过NaN
            continue

        # 这里改用 row_id 代替 index
        if col in translated_df.columns and row_id in translated_df.index and not pd.isna(translated_df.at[row_id, col]):
            continue
        if is_chinese(val):
            continue

        translated = translate_deepseek(str(val))
        new_row[col] = translated
        time.sleep(1)  # 控制速率
    return index, new_row

# def process_row(index, row, translated_df):
#     new_row = row.copy()
#     row_id = str(row['id'])
#     for col in row.index:
#         if col in SKIP_COLS:
#             continue
#         val = row[col]
#         if pd.isna(val):  # 跳过NaN
#             continue
#         # if pd.isna(val) or val.strip() == "":
#         #     continue
#         # 若已翻译，则跳过
#         if col in translated_df.columns and not pd.isna(translated_df.at[index, col]):
#             continue
#         # 若为中文，也跳过
#         if all('\u4e00' <= ch <= '\u9fff' for ch in str(val).strip()):
#             continue
#         if pd.isna(val) or val == "":
#             continue
#             # 如果该列该id已翻译过，则跳过
#         if col in translated_df.columns and row_id in translated_df.index and pd.notna(translated_df.at[row_id, col]):
#             continue
#             # 如果已经是中文，跳过
#         if is_chinese(val):
#             continue
#
#         translated = translate_deepseek(str(val))
#         new_row[col] = translated
#         time.sleep(1)  # 控制速率
#     return index, new_row


# 主流程
def translate_csv_append(input_csv, output_csv, max_workers=3):
    df = pd.read_csv(input_csv, dtype=str)

    # 确保整数列为字符串读取，后面统一转换
    int_cols = ['id', 'main_start', 'main_end', 'sub_start', 'sub_end']

    translated_df = pd.DataFrame(columns=df.columns).set_index('id')

    # 如果已存在输出文件，读取已翻译数据，设置id为索引
    if os.path.exists(output_csv):
        translated_df = pd.read_csv(output_csv, dtype=str).set_index('id')
        print(f"已翻译 {len(translated_df)} 行，将跳过")

    # 筛选出没翻译过的行
    untranslated = df[~df['id'].isin(translated_df.index)]

    print(f"待翻译行数：{len(untranslated)}")

    # 如果文件不存在，先写表头
    if not os.path.exists(output_csv):
        df.iloc[0:0].to_csv(output_csv, index=False)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for idx, row in untranslated.iterrows():
            futures.append(executor.submit(process_row, idx, row, translated_df))

        for future in concurrent.futures.as_completed(futures):
            index, translated_row = future.result()

            # 转整数列，避免浮点或字符串格式不一致
            for col in int_cols:
                if col in translated_row and pd.notna(translated_row[col]):
                    try:
                        translated_row[col] = str(int(float(translated_row[col])))
                    except Exception:
                        translated_row[col] = ''

            # 追加写入csv
            pd.DataFrame([translated_row]).to_csv(output_csv, mode='a', index=False, header=False)
            print(f"✅ 已追加翻译行 id={translated_row['id']}")

    print(f"🎉 翻译完成，结果保存于：{output_csv}")


if __name__ == "__main__":
    translate_csv_append("datasets/Process_time.csv", "datasets/Process_ds_multi2.csv", max_workers=10)

# def translate_csv(input_csv, output_csv, max_workers=4):
#     df = pd.read_csv(input_csv)
#     if os.path.exists(output_csv):
#         translated_df = pd.read_csv(output_csv)
#         print("📂 已加载已有翻译结果，继续翻译未完成部分...")
#     else:
#         translated_df = df.copy()
#         translated_df[:] = None  # 初始化为空
#
#     total = len(df)
#     print(f"📋 待翻译行数：{total}")
#
#     with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
#         futures = []
#         for i, row in df.iterrows():
#             futures.append(executor.submit(process_row, i, row, translated_df))
#
#         for future in concurrent.futures.as_completed(futures):
#             idx, updated_row = future.result()
#             translated_df.loc[idx] = updated_row
#             translated_df.to_csv(output_csv, index=False)  # 实时保存
#             print(f"✅ 已翻译第 {idx + 1} 行")
#
#     print(f"🎉 所有任务完成，翻译结果保存在：{output_csv}")

# 示例运行
# translate_csv_append("datasets/Process_time.csv", "datasets/Process_ds_multi2.csv", max_workers=10)
