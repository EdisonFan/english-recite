#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""阶段⑥ 视频渲染 · 八下 unit01 分包专用（主流程同一实现的副本）。

单命令跑完 6 课，产出 6 个课包目录，每目录 3 个文件：
    results/8b/unit01/video/U01_Lesson1/{视频.mp4, 音频.mp3, 封面.png}
    ...
    results/8b/unit01/video/U01_CX/{视频.mp4, 音频.mp3, 封面.png}

输入全部自动从仓库固定路径读取，无需任何参数、无需改代码：
    tasks/8b/video/data_unit01.json             预生成课次元信息 + 逐课译文
    tasks/8b/video/fonts/                      自带字体（不依赖系统字体）
    results/8b/unit01/audio/*.mp3               已验收的音频
    results/8b/unit01/audio/*.timeline.json     已验收的时间轴

⚠️ 只运行，不要修改本脚本。版式参数与主流程完全一致，改一处就对不上。
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DATA = os.path.join(HERE, "data_unit01.json")
FONTS = os.path.join(HERE, "fonts")
AUDIO_DIR = os.path.join(ROOT, "results", "8b", "unit01", "audio")
OUT_DIR = os.path.join(ROOT, "results", "8b", "unit01", "video")
TMP = os.path.join(ROOT, "_8b_video_tmp")

W, H = 1080, 1920
BG_C = (231, 242, 228)
INK = (37, 64, 50)
GREY = (118, 143, 126)
BLUE = (32, 80, 144)
SAFE_L = SAFE_R = 110
SW = W - SAFE_L - SAFE_R

WIN_TOP, WIN_BOT = 558, 1520
CENTER = (WIN_TOP + WIN_BOT) // 2
FS, LH, GAP = 54, 82, 26
INK_H = 45
PAGE_LIMIT = 620
FADE = 250
FPS = 24
LIGHT, DARK = "&H00BACABB&", "&H00324025&"
SENT = re.compile(r'(?<=[.!?])\s+(?=[A-Z“"]I?)')

FONT_C = os.path.join(FONTS, "wqy-microhei.ttc")
FONT_B = os.path.join(FONTS, "DejaVuSans-Bold.ttf")
FONT_R = os.path.join(FONTS, "DejaVuSans.ttf")
PB, PR, PC = FONT_B, FONT_R, FONT_C

FILES = ("视频.mp4", "音频.mp3", "封面.png")


def font(p, s):
    return ImageFont.truetype(p, s)


def wrap(text, fo, maxw=SW - 70):
    words, lines, cur = text.split(), [], ""
    for w in words:
        tmp = (cur + " " + w).strip()
        if fo.getlength(tmp) <= maxw:
            cur = tmp
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def esc(s):
    return s.replace("\\", "").replace("{", "(").replace("}", ")")


def hms(sec):
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h}:{m:02d}:{s:02d}.{ms // 10:02d}"


def zh_wrap(s, per=22):
    s = s.strip()
    if len(s) <= per:
        return s
    return s[:per] + r"\N" + s[per:per * 2]


def pauses(seg, dur):
    r = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", seg,
         "-af", "silencedetect=noise=-40dB:d=0.12", "-f", "null", "-"],
        capture_output=True, text=True, timeout=90)
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    return [round(b, 3) for a, b in zip(st, en)
            if a > 0.30 and b < dur - 0.30 and (b - a) >= 0.40]


def build_flow(rows, mp3, tmpdir):
    """朗读单元 → 子句流；子句起点优先取音频真实句间停顿。"""
    os.makedirs(tmpdir, exist_ok=True)
    flow, real, fallback = [], 0, 0
    for i, r in enumerate(rows):
        sents = [x.strip() for x in SENT.split(r["text"]) if x.strip()]
        speak = max(0.3, (r["end"] - r["start"]) - 0.75)
        seg = os.path.join(tmpdir, f"_seg{i:02d}.wav")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error",
                        "-ss", f"{r['start']:.3f}", "-i", mp3,
                        "-t", f"{speak:.3f}", "-ac", "1", "-ar", "16000", seg],
                       check=True, timeout=60)
        ps = pauses(seg, speak)
        os.remove(seg)
        if len(sents) > 1 and len(ps) == len(sents) - 1:
            times = [0.0] + ps
            real += 1
        else:
            lens = [len(x) for x in sents]
            tot = sum(lens) or 1
            times, acc = [0.0], 0
            for n in lens[:-1]:
                acc += n
                times.append(round(speak * acc / tot, 3))
            if len(sents) > 1:
                fallback += 1
        for si, sent in enumerate(sents):
            a = r["start"] + times[si]
            b = (r["start"] + times[si + 1]) if si + 1 < len(times) else r["end"]
            flow.append({"text": sent, "start": a, "end": b, "role": r["role"]})
    print(f"  子句流 {len(flow)} 句 | 真实停顿 {real} 单元 / 比例估算 {fallback} 单元",
          flush=True)
    return flow


def make_bg(path, les, unit_no, book_title):
    """视频静态背景（定稿版式）。"""
    im = Image.new("RGB", (W, H), BG_C)
    d = ImageDraw.Draw(im)
    x = SAFE_L
    d.text((x, 205), book_title, font=font(PC, 40), fill=INK)
    d.text((x, 262), "河北教育出版社 · 2026春起用 · 2022年版课标", font=font(PC, 27), fill=GREY)
    d.text((x, 318), f"第 {unit_no} 单元 · {les['no']}  {les['title']}",
           font=font(PC, 33), fill=INK)
    d.text((x, 370), f"课文：{les['title_zh']}", font=font(PC, 30), fill=GREY)
    d.text((x, 416), f"类型：{les['kind']}", font=font(PC, 29), fill=GREY)
    d.line([(SAFE_L, 486), (W - SAFE_R, 486)], fill=GREY, width=2)
    d.line([(SAFE_L, WIN_BOT + 130), (W - SAFE_R, WIN_BOT + 130)], fill=GREY, width=2)
    d.text((SAFE_L, WIN_BOT + 156), "听一句 · 停一停 · 跟读一遍", font=font(PC, 33), fill=INK)
    d.text((SAFE_L, WIN_BOT + 216), "MORNING ENGLISH PRACTICE", font=font(PR, 26), fill=GREY)
    sx = W - SAFE_R - 14
    d.rounded_rectangle([sx, WIN_TOP + 30, sx + 5, WIN_BOT - 30], radius=3,
                        fill=(206, 222, 202))
    im.save(path)


def make_cover(path, les, unit_no, book_title):
    """竖版封面（与八上 48 课同款）。"""
    BG, BLOCK, INK2, LINE = (231, 242, 228), (214, 231, 210), (86, 118, 94), (168, 196, 172)
    L, R = 110, 970
    SAFE_W = R - L
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)

    def put(xy, text, fp, size, fill, bold=0, maxw=None, minsize=18):
        while size > minsize and maxw:
            f = ImageFont.truetype(fp, size)
            if d.textbbox((0, 0), text, font=f, stroke_width=bold)[2] <= maxw:
                break
            size -= 2
        f = ImageFont.truetype(fp, size)
        d.text(xy, text, font=f, fill=fill, stroke_width=bold, stroke_fill=fill)

    m = re.search(r"Lesson\s*(\d+)", les["no"])
    if m:
        num = int(m.group(1))
        tag, zh_no = f"{num:02d}", f"第 {num} 课"
        idx_line = f"Unit {unit_no} · Lesson {num}"
    else:
        tag, zh_no = "EX", "单元拓展"
        idx_line = f"Unit {unit_no} · Unit cultures"

    en = "MORNING ENGLISH PRACTICE  ·  "
    f_en = font(FONT_R, 27)
    d.text((L, 150), en, font=f_en, fill=INK2)
    d.text((L + d.textlength(en, font=f_en), 150), "初中英语早读", font=font(PC, 27), fill=INK2)
    d.line((L, 205, R, 205), fill=LINE, width=2)

    head = "初中英语课文朗读"
    half = 4 if len(head) >= 8 else (len(head) + 1) // 2
    put((L, 285), head[:half], PC, 150, INK, bold=3, maxw=SAFE_W)
    put((L + 40, 460), head[half:], PC, 150, INK, bold=3, maxw=SAFE_W - 40)

    d.rectangle((L, 665, R, 1010), fill=BLOCK)
    put((L + 55, 705), tag, PB, 250, INK)
    put((L + 470, 780), "LESSON " + tag if tag != "EX" else "CULTURE", PB, 34, INK2)
    put((L + 470, 840), zh_no, PC, 36, INK, bold=1)

    put((L, 1080), les["title"], PB, 50, INK, maxw=SAFE_W, minsize=26)
    put((L, 1160), idx_line, PR, 32, INK2, maxw=SAFE_W)
    y = 1275
    for f in ["逐句字幕", "跟读留白", "自然人声"]:
        d.line((L, y + 22, L + 34, y + 22), fill=INK2, width=3)
        put((L + 52, y), f, PC, 32, INK, maxw=SAFE_W - 60)
        y += 72
    d.line((L, 1480, R, 1480), fill=LINE, width=2)
    put((L, 1520), book_title, PC, 30, INK, maxw=SAFE_W, minsize=20)
    put((L, 1590), "听一句 · 停一停 · 跟读一遍", PC, 30, INK2, maxw=SAFE_W, minsize=20)
    im.save(path, optimize=True)


def paginate(blocks):
    pages, cur, h = [], [], 0
    for i, b in enumerate(blocks):
        add = b["h"] + (GAP if cur else 0)
        if cur and h + add > PAGE_LIMIT:
            pages.append(cur)
            cur, h = [i], b["h"]
        else:
            cur.append(i)
            h += add
    if cur:
        pages.append(cur)
    return pages


def build_ass(path, flow, voices, total, zh):
    fo = font(PB, FS)
    blocks = [{"lines": wrap(f["text"], fo), "h": len(wrap(f["text"], fo)) * LH}
              for f in flow]
    N = len(flow)
    assert len(zh) == N, f"译文 {len(zh)} 条 / 子句 {N} 条，对不上"
    pages = paginate(blocks)
    print(f"  分页 {len(pages)}（每页 {[len(p) for p in pages]} 句）", flush=True)

    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: None

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cur,DejaVu Sans,{FS},&H00324025,&H00BACABA,&H00FFFFFF,&H00000000,-1,0,0,0,100,100,0,0,1,2,0,7,0,0,0,1
Style: Role,WenQuanYi Micro Hei,34,&H00905020,&H000000FF,&H00FFFFFF,&H00000000,-1,0,0,0,100,100,0,0,1,1,0,7,0,0,0,1
Style: Cjk,WenQuanYi Micro Hei,26,&H007E8F76,&H000000FF,&H00FFFFFF,&H00000000,0,0,0,0,100,100,0,0,1,1,0,7,0,0,0,1
Style: Num,DejaVu Sans,30,&H007E8F76,&H000000FF,&H00FFFFFF,&H00000000,0,0,0,0,100,100,0,0,1,1,0,7,0,0,0,1
Style: Tr,WenQuanYi Micro Hei,36,&H0056694E,&H000000FF,&H00FFFFFF,&H00000000,0,0,0,0,100,100,0,0,1,1,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []

    def add(layer, st, en, style, txt, extra=""):
        ev.append(f"Dialogue: {layer},{hms(st)},{hms(en)},{style},,0,0,0,,{extra}{txt}")

    clip = rf"{{\clip({SAFE_L},{WIN_TOP},{W - SAFE_R},{WIN_BOT})\an7}}"
    X = SAFE_L + 34
    band, step = 140, 14
    rect = lambda h: (r"{\p1}m 0 0 l " + str(W) + r" 0 l " + str(W) +
                      r" " + str(h) + r" l 0 " + str(h) + r"{\p0}")
    for yy in range(WIN_TOP, WIN_TOP + band, step):
        a = 255 - int(255 * (1 - (yy - WIN_TOP) / band))
        add(1, 0, total, "Cur", rect(step),
            f"{{\\pos(0,{yy})\\alpha&H{a:02X}&\\1c&HE4F2E7&\\bord0\\shad0}}")
    for yy in range(WIN_BOT - band, WIN_BOT, step):
        a = 255 - int(255 * ((yy - (WIN_BOT - band)) / band))
        add(1, 0, total, "Cur", rect(step),
            f"{{\\pos(0,{yy})\\alpha&H{a:02X}&\\1c&HE4F2E7&\\bord0\\shad0}}")

    for pi, page in enumerate(pages):
        p_start = flow[page[0]]["start"]
        p_end = flow[page[-1]]["end"]
        total_h = sum(blocks[i]["h"] for i in page) + GAP * (len(page) - 1)
        y0 = CENTER - total_h / 2
        fad = (f"\\fad({FADE if pi > 0 else 0},"
               f"{FADE if pi < len(pages) - 1 else 0})")
        sx = W - SAFE_R - 17
        span = WIN_BOT - WIN_TOP - 150
        y_from = WIN_TOP + 30 + (page[0] / max(1, N - 1)) * span
        y_to = WIN_TOP + 30 + (page[-1] / max(1, N - 1)) * span
        add(0, p_start, p_end, "Cur",
            r"{\p1}m 0 0 l 11 0 l 11 90 l 0 90{\p0}",
            (f"{{\\move({sx},{y_from:.0f},{sx},{y_to:.0f},"
             f"0,{int((p_end - p_start) * 1000)})\\alpha&H30&"
             f"\\1c&H905020&\\bord0\\shad0}}"))

        yy = y0
        for i in page:
            f = flow[i]
            t1 = int((f["start"] - p_start) * 1000)
            color = ("{\\1c" + LIGHT + "\\t(" + str(t1) + "," +
                     str(t1 + 160) + ",\\1c" + DARK + ")}")
            for k, ln in enumerate(blocks[i]["lines"]):
                y = yy + k * LH
                if y + LH < WIN_TOP - 40 or y > WIN_BOT + 40:
                    continue
                add(0, p_start, p_end, "Cur", color + esc(ln),
                    "{" + fad + f"\\pos({X},{y:.0f})}}" + clip)
            bh = max(30, blocks[i]["h"] - (LH - INK_H))
            bar = (r"{\p1}m 0 0 l 8 0 l 8 " + str(int(bh)) +
                   r" l 0 " + str(int(bh)) + r"{\p0}")
            add(0, f["start"], f["end"], "Cur", bar,
                (f"{{\\pos({SAFE_L + 4},{yy + 8:.0f})"
                 f"\\alpha&H10&\\1c&H905020&\\bord0\\shad0}}"))
            yy += blocks[i]["h"] + GAP

        for i in page:
            f = flow[i]
            sex = voices.get(f["role"], {}).get("sex", "F")
            mark = "♂♀" if f["role"] == "ALL" else {"M": "♂", "F": "♀"}.get(sex, "♂")
            add(0, f["start"], f["end"], "Role", f"{mark}  {f['role']}",
                "{\\pos(130,510)}")
            add(0, f["start"], f["end"], "Cjk",
                f"第 {i+1} 句 / 共 {N} 句", "{\\pos(730,518)}")
            add(0, f["start"], f["end"], "Num", f"{i+1:02d} / {N:02d}",
                f"{{\\pos(870,{WIN_BOT + 160})}}")
            add(0, f["start"], f["end"], "Tr", zh_wrap(zh[i]),
                f"{{\\fad(180,180)\\pos({W // 2},{WIN_BOT + 62})}}")

    open(path, "w", encoding="utf-8").write(head + "\n".join(ev) + "\n")
    print(f"  ASS 事件 {len(ev)} 条 | 换页 {len(pages)} 次", flush=True)
    return N, len(pages)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def render_one(les, unit_no, book_title, voices):
    key = les["key"]
    mp3 = os.path.join(AUDIO_DIR, key + ".mp3")
    tlf = os.path.join(AUDIO_DIR, key + ".timeline.json")
    if not (os.path.isfile(mp3) and os.path.isfile(tlf)):
        print(f"  ✗ {key} 缺音频/时间轴，跳过", flush=True)
        return False

    meta = json.load(open(tlf, encoding="utf-8"))
    rows, total = meta["timeline"], meta["total"]
    en, zh = les["en"], les["zh"]

    tmp = os.path.join(TMP, key)
    os.makedirs(tmp, exist_ok=True)
    # 字体随包复制到临时目录，ffmpeg 用相对路径 fonts/，避免中文路径转义
    fdst = os.path.join(tmp, "fonts")
    os.makedirs(fdst, exist_ok=True)
    for f in ("wqy-microhei.ttc", "DejaVuSans.ttf", "DejaVuSans-Bold.ttf"):
        shutil.copyfile(os.path.join(FONTS, f), os.path.join(fdst, f))

    flow = build_flow(rows, mp3, tmp)
    if len(flow) != len(en):
        print(f"  ✗ {key} 子句 {len(flow)} / 期望 {len(en)}", flush=True)
        return False
    for i, (f, e) in enumerate(zip(flow, en), 1):
        if f["text"] != e:
            print(f"  ✗ {key} 第 {i} 条英文不一致：{f['text'][:40]} / {e[:40]}", flush=True)
            return False

    bg = os.path.join(tmp, "bg.png")
    ass = os.path.join(tmp, "page.ass")
    out_mp4 = os.path.join(tmp, "视频.mp4")
    make_bg(bg, les, unit_no, book_title)
    build_ass(ass, flow, voices, total, zh)

    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-loop", "1", "-framerate", str(FPS), "-i", "bg.png",
           "-i", mp3,
           "-filter_complex", "[0:v]ass=page.ass:fontsdir=fonts,format=yuv420p[v]",
           "-map", "[v]", "-map", "1:a", "-threads", "2",
           "-c:v", "libx264", "-preset", "ultrafast", "-crf", "24",
           "-tune", "stillimage", "-r", str(FPS),
           "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
           "-t", f"{total:.3f}", "-movflags", "+faststart", out_mp4]
    r = subprocess.run(cmd, cwd=tmp, capture_output=True, text=True, timeout=600)
    if r.returncode:
        print(f"  ✗ {key} 渲染失败\n{r.stderr[-600:]}", flush=True)
        return False

    # 成品核验：全帧解码 + 音画时长
    dec = subprocess.run(["ffmpeg", "-v", "error", "-i", out_mp4, "-f", "null", "-"],
                         capture_output=True)
    vd = duration(out_mp4)
    ad = duration(mp3)
    n_tr = sum(1 for l in open(ass, encoding="utf-8") if ",Tr," in l)
    if dec.returncode or abs(vd - ad) > 1.0 or n_tr != len(zh) or vd < 20:
        print(f"  ✗ {key} 核验失败 {vd:.1f}s/{ad:.1f}s 译文事件{n_tr}/{len(zh)} 解码{dec.returncode}",
              flush=True)
        return False

    pack = os.path.join(OUT_DIR, key)
    os.makedirs(pack, exist_ok=True)
    shutil.copyfile(out_mp4, os.path.join(pack, "视频.mp4"))
    shutil.copyfile(mp3, os.path.join(pack, "音频.mp3"))
    make_cover(os.path.join(pack, "封面.png"), les, unit_no, book_title)

    # 上传前再验「课包里那一份」，防止残件
    pdur = duration(os.path.join(pack, "视频.mp4"))
    pdec = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(pack, "视频.mp4"),
                           "-f", "null", "-"], capture_output=True)
    if abs(pdur - vd) > 1.0 or pdur < 20 or pdec.returncode:
        print(f"  ✗ {key} 课包视频异常 {pdur:.1f}s，拒绝交付", flush=True)
        return False

    print(f"  ✓ {key}  {vd:.1f}s  {len(flow)} 子句 / {len(zh)} 译文  "
          f"{os.path.getsize(os.path.join(pack, '视频.mp4')) // 1024} KB", flush=True)
    return True


def duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration", "-of", "default=nw=1:nk=1", path],
                       capture_output=True, text=True, timeout=90)
    try:
        return float(r.stdout.strip())
    except Exception:
        return 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="只渲染某一课，如 U01_Lesson1（本地试跑用）")
    args = ap.parse_args()

    for f in (FONT_C, FONT_B, FONT_R, DATA):
        if not os.path.isfile(f):
            sys.exit("缺文件：" + f)
    try:
        import PIL  # noqa
    except ImportError:
        sys.exit("缺 Pillow：pip install -r tasks/8b/video/requirements.txt")

    d = json.load(open(DATA, encoding="utf-8"))
    lessons = d["lessons"]
    if args.only:
        lessons = [x for x in lessons if x["key"] == args.only]
        if not lessons:
            sys.exit("找不到课次 " + args.only)

    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"== 八下 unit01 视频渲染（{len(lessons)} 课）==", flush=True)
    print(f"   输入 {AUDIO_DIR}\n   输出 {OUT_DIR}", flush=True)
    ok = []
    for les in lessons:
        print(f"\n── {les['key']} {les['title']} ──", flush=True)
        if render_one(les, d["unit"], d["book"]["title_zh"], d["voices"]):
            ok.append(les["key"])
    print(f"\n== 完成 {len(ok)}/{len(lessons)} 课 ==", flush=True)
    if len(ok) != len(lessons):
        sys.exit("有课失败，不要提交；按报错检查后重跑本脚本")
    print("   下一步：python tasks/8b/video/自检.py unit01", flush=True)


if __name__ == "__main__":
    main()
