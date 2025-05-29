import pandas as pd
import re

# 模糊词映射到区间偏移（用于 century 模糊处理）
MODIFIERS = {
    'early': (0.0, 0.3),
    'mid': (0.3, 0.7),
    'late': (0.7, 1.0),
    'first half': (0.0, 0.5),
    'second half': (0.5, 1.0),
    'first': (0.0, 0.3),
    'second': (0.3, 0.6),
    'third': (0.6, 1.0),
    'middle': (0.4, 0.6),
    'probably': (0.0, 1.0),  # 宽泛
}


def extract_info(text):
    text = text.strip()
    # === 带括号的数字区间，如 (1600–1650), (206 B.C.–A.D. 9)
    m = re.search(
        r'\((?P<approx>c\.|ca\.|approx\.)?\s*(?P<start>\d{1,4})\s*[-–/]\s*(?P<end>\d{1,4})\s*(?P<era>B\.?C\.?|BCE|A\.?D\.?|CE)?\)',
        text, flags=re.I)
    if m:
        y1 = int(m.group('start'))
        y2 = int(m.group('end'))
        if m.group('era') and re.search(r'B\.?C\.?|BCE', m.group('era'), flags=re.I):
            y1, y2 = -y1, -y2
        return min(y1, y2), max(y1, y2), text

    # === 百年模糊表达，例如：late 13th century
    m = re.search(
        r'(?P<modifier>early|mid|late|first half|second half|first|second|third)?\s*[-]?\s*(?P<century>\d{1,2})(st|nd|rd|th)? century\s*(?P<era>BCE|CE|AD|BC)?',
        text, flags=re.I)
    if m:
        century = int(m.group('century'))
        modifier = m.group('modifier').lower() if m.group('modifier') else None
        era = m.group('era')
        base_start = (century - 1) * 100
        base_end = base_start + 100

        if modifier and modifier in MODIFIERS:
            offset_start, offset_end = MODIFIERS[modifier]
            y1 = int(base_start + offset_start * 100)
            y2 = int(base_start + offset_end * 100)
        else:
            y1, y2 = base_start, base_end

        if era and re.search(r'BCE|B\.?C\.?', era, flags=re.I):
            y1, y2 = -y1, -y2
        return min(y1, y2), max(y1, y2), text

    # === 年份区间，如 1850–1911 或 13th century–14th century
    m = re.search(r'(?P<start>\d{3,4})\s*[-/–]\s*(?P<end>\d{3,4})', text)
    if m:
        return int(m.group('start')), int(m.group('end')), text

    # === 单一年份
    m = re.search(r'(?P<approx>c\.|ca\.|approx\.)?\s*(?P<year>\d{3,4})\s*(?P<era>BCE|B\.?C\.?|CE|A\.?D\.)?', text,
                  flags=re.I)
    if m:
        y = int(m.group('year'))
        if m.group('era') and re.search(r'BCE|B\.?C\.?', m.group('era'), flags=re.I):
            y = -y
        return y, y, text

    return None, None, text  # 没有识别成功


def parse_time_row(text):
    parts = [p.strip() for p in re.split(r';|,|\bor\b|\band\b', str(text)) if p.strip()]
    results = []
    for part in parts:
        y1, y2, note = extract_info(part)
        if y1 is not None and y2 is not None:
            results.append((y1, y2, note))

    if not results:
        return None, None, None, None

    # 第一个为主区间，其他为次区间
    main_start, main_end, main_note = results[0]
    if len(results) > 1:
        sub_start = min(r[0] for r in results[1:])
        sub_end = max(r[1] for r in results[1:])
        sub_note = "; ".join(r[2] for r in results[1:])
    else:
        sub_start = sub_end = sub_note = None

    return main_start, main_end, sub_start, sub_end


# 所有常见朝代/时期关键词（可扩展）
PERIOD_KEYWORDS = [
    r'Qin dynasty', r'Han dynasty', r'Western Han dynasty', r'Eastern Han dynasty',
    r'Three Kingdoms', r'Jin dynasty', r'Sixteen Kingdoms', r'Northern Wei dynasty',
    r'Eastern Wei dynasty', r'Western Wei dynasty', r'Southern dynasty', r'Northern dynasty',
    r'Sui dynasty', r'Tang dynasty', r'Song dynasty', r'Northern Song dynasty', r'Southern Song dynasty',
    r'Liao dynasty', r'Xia dynasty', r'Yuan dynasty', r'Ming dynasty', r'Qing dynasty',
    r'Republic period', r'Warring States period', r'Spring and Autumn period',
    r'Erligang period', r'Transitional', r'Shang dynasty', r'Zhou dynasty',
    r'Eastern Zhou dynasty', r'Western Zhou dynasty', r'Neolithic', r'Red Turban Rebellion',
    r'Yongle reign', r'Kangxi period', r'Yuan or early Ming dynasty', r'Jurchen dynasty',
]

# 编译成正则列表
PERIOD_PATTERNS = [re.compile(p, re.I) for p in PERIOD_KEYWORDS]


def extract_periods(text):
    found = set()
    for pat in PERIOD_PATTERNS:
        matches = pat.findall(str(text))
        for m in matches:
            found.add(m.strip())
    return "; ".join(sorted(found)) if found else None


# 示例读取 CSV
if __name__ == '__main__':
    df = pd.read_csv("datasets/Process_datas2.csv")  # 替换为你的 CSV 路径
    df[['main_start', 'main_end', 'sub_start', 'sub_end']] = df['Dynasty'].apply(
        lambda x: pd.Series(parse_time_row(x))
    )
    df['periods'] = df['Dynasty'].apply(extract_periods)
    df.to_csv("datasets/Process_time.csv", index=False)
