#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""课文整理阶段 · 提交前自检（主流程闸门的同源公开副本）。

用法（在仓库根目录）：
    python tasks/8b/自检_课文整理.py unit01
    python tasks/8b/自检_课文整理.py unit01 /path/to/repo

只读 results/8b/unitNN/ 的三份 JSON 与 pages/8b/unitNN.txt；
不联网、不改文件、不写状态。全绿才提交。

⚠️ 这份脚本与主流程闸门同源。不要自己改写、不要另写一套校验逻辑。
"""
import json
import os
import re
import sys
from collections import Counter

# ── 唯一口径：与渲染器 _八上定稿_渲染.py 完全一致 ──
SENT = re.compile(r'(?<=[.!?])\s+(?=[A-Z“"]I?)')
ROLES = {"NARRATOR", "LI MING", "JENNY", "DANNY", "WANG MEI", "LI LIN",
         "SONG HUA", "MS LIU", "BRIAN", "ALL", "TIANTIAN", "LUCAS"}

# 只拦「练习题指令」，不拦正文里的普通动词短语。
# 反例（曾误报）：They loved to listen to the singing of the birds.
BAD_INSTRUCTION = re.compile(
    r"\b(Read the (?:passage|questions|conversation|webpage|interview|advertisement)|"
    r"Listen (?:and (?:tick|answer|repeat|check|choose|number)|"
    r"to the (?:conversation|passage|recording|dialogue|tape))|"
    r"Tick|True\s*\(?T\)?|False\s*\(?F\)?|"
    r"Fill in (?:the )?blanks|Complete the (?:table|timeline|sentences|passage)|"
    r"Choose the correct|Answer the questions|Write true|"
    r"Look at the (?:pictures|picture)|Scan the QR|underline|match the|"
    r"Work in pairs|Discuss with your partner)\b", re.I)
RED_LINE = re.compile(r"Back to school|It's Show Time|Summer Holiday Is Coming|衔接三年级起点|Lessons? 1[–\-]48", re.I)
CJK = re.compile(r"[\u4e00-\u9fff]")
ALLOW_HINT = re.compile(r"教材原字|allow_cjk|汉字|象形", re.I)


def norm(s):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", s.lower())).strip()


def words(s):
    return re.findall(r"[a-z0-9']+", s.lower())


def wrap_lines(text):
    """渲染器同款折行：54 px 字号、SW-70 宽、按词换行。字体缺失时降级估算。"""
    SW = 1080
    maxw = SW - 70
    try:
        from PIL import ImageFont
        candidates = [
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            "WenQuanYi Micro Hei",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
        fo = None
        for p in candidates:
            try:
                fo = ImageFont.truetype(p, 54)
                break
            except Exception:
                continue
        if fo:
            lines, cur = [], ""
            for w in text.split():
                tmp = (cur + " " + w).strip()
                if fo.getlength(tmp) <= maxw:
                    cur = tmp
                else:
                    if cur:
                        lines.append(cur)
                    cur = w
            if cur:
                lines.append(cur)
            return len(lines), False
    except Exception:
        pass
    # 降级：英文 54px 下平均约 16 字符/行（保守）
    return max(1, -(-len(text) // 16)), True


def main():
    if len(sys.argv) < 2 or not re.fullmatch(r"unit0[1-8]", sys.argv[1]):
        sys.exit("用法：python 自检_课文整理.py unit01 … unit08 [仓库根目录]")
    u = sys.argv[1]
    n = int(u[-2:])
    root = sys.argv[2] if len(sys.argv) > 2 else "."
    res = os.path.join(root, "results", "8b", u)
    page_p = os.path.join(root, "pages", "8b", u + ".txt")
    errs, warns = [], []

    def E(msg):
        errs.append(msg)

    def W(msg):
        warns.append(msg)

    paths = {f: os.path.join(res, f) for f in
             ("课文数据.json", "教材基准.json", "课文译文.json")}
    for f, p in paths.items():
        if not os.path.isfile(p):
            E("缺文件 %s" % f)
    if errs:
        print("\n  ❌ FAIL"); [print("   ✗ " + e) for e in errs]; sys.exit(1)
    try:
        d = json.load(open(paths["课文数据.json"], encoding="utf-8"))
        b = json.load(open(paths["教材基准.json"], encoding="utf-8"))
        z = json.load(open(paths["课文译文.json"], encoding="utf-8"))
        page = open(page_p, encoding="utf-8").read() if os.path.isfile(page_p) else ""
    except Exception as e:
        print("\n  ❌ FAIL  解析失败：%s %s" % (type(e).__name__, e)); sys.exit(1)

    print("== %s 课文整理自检 ==" % u)
    nd, nb = len(d.get("lessons", [])), len(b.get("lessons", []))
    if not (nd == 6 and nb == 6):
        E("课文数据 %d 课 / 教材基准 %d 课（应各 6）" % (nd, nb))

    want = ["U%02d_Lesson%d" % (n, i) for i in range(1, 6)] + ["U%02d_CX" % n]
    got = [x.get("key", "") for x in b.get("lessons", [])]
    if got != want:
        E("key 应为 %s，实际 %s" % (want, got))

    all_lines, expect = [], []
    for i, les in enumerate(d.get("lessons", []), 1):
        lines = [x.get("text", "") for x in les.get("lines", [])]
        if not lines:
            E("第 %d 课 lines 为空" % i)
        # canonical 逐字一致
        if i <= len(b.get("lessons", [])):
            c = b["lessons"][i - 1].get("canonical", [])
            if lines != c:
                E("第 %d 课 canonical 与 lines 不一致" % i)
        # 该课 inferred 是否声明了教材原字
        inferred = " ".join(b["lessons"][i - 1].get("inferred", [])) if i <= len(b.get("lessons", [])) else ""
        cjk_ok = bool(ALLOW_HINT.search(inferred))
        for x in les.get("lines", []):
            t, role = x.get("text", ""), x.get("role", "")
            if role not in ROLES:
                E("第 %d 课表外 role：%s" % (i, role))
            if CJK.search(t) and not cjk_ok:
                E("第 %d 课英文混入中文且 inferred 未声明教材原字：%s…" % (i, t[:40]))
            elif CJK.search(t):
                W("第 %d 课教材原字已豁免（inferred 已声明）" % i)
            if BAD_INSTRUCTION.search(t) or re.search(r"_{3,}|\(\s{4,}\)|===== PDF p", t):
                E("第 %d 课疑似练习题残留：%s…" % (i, t[:50]))
            if len(t) > 170:
                segs = [s for s in SENT.split(t) if s.strip()]
                if len(segs) > 1:
                    E("第 %d 课 %d 字符且还能切 %d 段，必须按句号切开" % (i, len(t), len(segs)))
                else:
                    nl, approx = wrap_lines(t)
                    if nl > 12:
                        E("第 %d 课 %d 字符切不动且折行 %d 行 > 12" % (i, len(t), nl))
                    else:
                        W("第 %d 课 %d 字符单句切不动，折行 %d 行 ≤12，放行%s" % (
                            i, len(t), nl, "（字体降级估算）" if approx else ""))
            all_lines.append(t)
            for s in SENT.split(t):
                s = s.strip()
                if s:
                    expect.append(s)
        if i <= len(b.get("lessons", [])) and not b["lessons"][i - 1].get("inferred"):
            W("第 %d 课 inferred 为空" % i)

    # 官方正文页命中
    if page:
        pn = norm(page)
        pw = Counter(words(page))
        hit = sum(1 for t in all_lines if norm(t) in pn)
        rate = hit / max(1, len(all_lines))
        lw = Counter(w for t in all_lines for w in words(t))
        cover = sum(min(v, pw.get(k, 0)) for k, v in lw.items()) / max(1, sum(lw.values()))
        print("   PDF 逐句命中 %.1f%% | 词覆盖 %.3f" % (rate * 100, cover))
        if rate < 0.60:
            E("PDF 逐句命中 %.1f%% < 60%%，疑似版本不符" % (rate * 100))
        if cover < 0.95:
            E("词覆盖 %.3f < 0.95，英文可能不来自正文页" % cover)
        if RED_LINE.search(page) or RED_LINE.search(" ".join(all_lines)):
            E("命中旧版教材红线")
    else:
        W("缺 pages/8b/%s.txt，跳过 PDF 命中检查（主流程会补验）" % u)

    # 译文
    items = z.get("items", [])
    en = [x.get("en", "") for x in items]
    nos = [x.get("no") for x in items]
    empty_zh = sum(1 for x in items if not str(x.get("zh", "")).strip())
    print("   朗读单元 %d | 子句 %d | 译文 %d" % (len(all_lines), len(expect), len(items)))
    if en != expect:
        if norm(" ".join(en)) == norm(" ".join(all_lines)):
            E("译文英文文字完整，但切分口径不符：%d 条 / 应为 %d 条（按 SENT 正则重排）" % (
                len(items), len(expect)))
        else:
            first = next((j for j, (a, c) in enumerate(zip(en, expect)) if a != c),
                         min(len(en), len(expect)))
            E("译文与子句错位/丢句，首个差异在第 %d 条" % (first + 1))
    if nos != list(range(1, len(items) + 1)):
        E("译文 no 不连续")
    if empty_zh:
        E("译文有 %d 条空中文" % empty_zh)
    if "自译" not in str(z.get("note", "")) and "参考" not in str(z.get("note", "")):
        E("译文 note 未声明自译 / 非教材原文")

    print("\n  文件 3 / 期望 3")
    for w in warns:
        print("   ⚠ " + w)
    for e in errs:
        print("   ✗ " + e)
    if errs:
        print("\n  ❌ FAIL（%d 项），不要提交" % len(errs)); sys.exit(1)
    print("\n  ✅ PASS — 3 份 JSON 可以提交")


if __name__ == "__main__":
    main()
