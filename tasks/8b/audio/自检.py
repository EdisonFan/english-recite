#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 用法（在仓库根目录）：python tasks/8b/audio/自检.py unit01
# 只依赖：Python 标准库 + imageio-ffmpeg（worker 已装）
import json, os, re, subprocess, sys

def ffmpeg():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"

def probe(path):
    r = subprocess.run([ffmpeg(), "-hide_banner", "-i", path, "-f", "null", "-"],
                       capture_output=True, text=True)
    s = r.stderr
    m = re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)", s)
    dur = (int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))) if m else 0.0
    ok = (r.returncode == 0 and dur > 0 and "Audio:" in s)
    return ok, dur, s[-300:] if not ok else ""

def main():
    if len(sys.argv) < 2 or not re.fullmatch(r"unit0[1-8]", sys.argv[1]):
        sys.exit("用法：python 自检.py unit01 … unit08")
    u = sys.argv[1]
    root = sys.argv[2] if len(sys.argv) > 2 else "."
    n = int(u[-2:])
    data_p = os.path.join(root, "tasks/8b/audio", "data_%s.json" % u)
    out = os.path.join(root, "results/8b", u, "audio")
    data = json.load(open(data_p, encoding="utf-8"))
    lessons = data["lessons"]
    errs, warns = [], []
    print("== %s 音频自检（%d 课）==" % (u, len(lessons)))
    if len(lessons) != 6:
        errs.append("输入不是 6 课")
    all_files = []
    for les in lessons:
        key = les["key"]
        mp3 = os.path.join(out, key + ".mp3")
        tl = os.path.join(out, key + ".timeline.json")
        all_files += [key + ".mp3", key + ".timeline.json"]
        for p in (mp3, tl):
            if not os.path.isfile(p):
                errs.append("%s 缺文件 %s" % (key, os.path.basename(p)))
        if not (os.path.isfile(mp3) and os.path.isfile(tl)):
            continue
        ok, dur, tail = probe(mp3)
        if not ok:
            errs.append("%s MP3 不可解码/无音频流 %s" % (key, tail))
            continue
        if dur < 20:
            errs.append("%s MP3 时长 %.1fs < 20s" % (key, dur))
        # 真实语音约 6–9 KB/s；纯静音或空音频会掉到 1 KB/s 左右。
        min_bytes = max(60 * 1024, int(dur * 2500))
        if os.path.getsize(mp3) < min_bytes:
            errs.append("%s MP3 仅 %.1f KB（%.1fs 至少需 %.1f KB），疑似静音/空音频" % (
                key, os.path.getsize(mp3) / 1024, dur, min_bytes / 1024))
        try:
            t = json.load(open(tl, encoding="utf-8"))
        except Exception as e:
            errs.append("%s timeline 解析失败 %s" % (key, e)); continue
        for f in ("key", "no", "title", "title_zh", "kind", "timeline", "total"):
            if f not in t: errs.append("%s timeline 缺字段 %s" % (key, f))
        if t.get("key") != key:
            errs.append("%s timeline.key=%s 不符" % (key, t.get("key")))
        rows = t.get("timeline", [])
        src = les["lines"]
        if len(rows) != len(src):
            errs.append("%s timeline %d 条 / 输入 %d 行" % (key, len(rows), len(src)))
            continue
        cur = 0.0
        for i, (r, s) in enumerate(zip(rows, src), 1):
            for f in ("start", "end", "role", "text"):
                if f not in r: errs.append("%s 第 %d 条缺 %s" % (key, i, f))
            if r.get("text") != s["text"]:
                errs.append("%s 第 %d 条 text 与输入不一致" % (key, i))
            if r.get("role") != s["role"]:
                errs.append("%s 第 %d 条 role 不一致" % (key, i))
            if abs(r.get("start", -1) - cur) > 0.01:
                errs.append("%s 第 %d 条 start=%.3f 应为 %.3f" % (key, i, r.get("start", -1), cur))
            if r.get("end", 0) <= r.get("start", 0):
                errs.append("%s 第 %d 条 end<=start" % (key, i))
            cur = r.get("end", cur)
        total = t.get("total", 0)
        if abs(total - cur) > 0.01:
            errs.append("%s total=%.3f 应为末条 end %.3f" % (key, total, cur))
        if abs(total - dur) > 1.0:
            errs.append("%s total %.2fs 与 MP3 %.2fs 差 >1s（检查 0.75s 句间静音是否拼进去）" % (key, total, dur))
        print("   %-16s %2d 条  %6.2fs  MP3 %6.2fs  %s" % (
            key, len(rows), total, dur,
            "OK" if not any(e.startswith(key + " ") for e in errs) else "FAIL"))
    extra = [f for f in os.listdir(out) if os.path.isfile(os.path.join(out, f)) and f not in all_files] if os.path.isdir(out) else []
    if extra:
        warns.append("目录里有多余文件：%s" % extra[:8])
    print("\n  文件 %d / 期望 %d" % (len(all_files), 12))
    for w in warns: print("   ⚠ " + w)
    for e in errs: print("   ✗ " + e)
    if errs:
        print("\n  ❌ FAIL（%d 项），不要提交" % len(errs)); sys.exit(1)
    print("\n  ✅ PASS — 可以提交 12 个文件")

if __name__ == "__main__":
    main()
