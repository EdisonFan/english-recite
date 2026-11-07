#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""阶段⑥ 视频产物 · 提交前自检（主流程闸门的同源副本）。

用法（仓库根目录）：
    python tasks/8b/video/自检.py unit01
    python tasks/8b/video/自检.py unit01 /path/to/repo

只读，不联网，不改文件，不写状态。全绿才提交。
"""
import hashlib
import json
import os
import re
import subprocess
import sys

FILES = ("视频.mp4", "音频.mp3", "封面.png")


def run(cmd, timeout=300):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def probe(path):
    r = run(["ffprobe", "-v", "error", "-show_format", "-show_streams",
             "-of", "json", path], 90)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {}


def duration(path):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", path], 90)
    try:
        return float(r.stdout.strip())
    except Exception:
        return 0.0


def env_check(errs):
    for exe in ("ffmpeg", "ffprobe"):
        try:
            subprocess.run([exe, "-version"], capture_output=True, timeout=30)
        except Exception:
            errs.append("缺可执行程序 %s" % exe)
    if errs:
        return
    h = subprocess.run(["ffmpeg", "-hide_banner", "-h", "filter=ass"],
                       capture_output=True, text=True, timeout=30)
    if "Render ASS" not in (h.stdout + h.stderr):
        errs.append("ffmpeg 未编入 libass（字幕渲染不可用），请换带 libass 的 ffmpeg")
    e = run(["ffmpeg", "-hide_banner", "-encoders"])
    for enc in ("libx264", "aac"):
        if enc not in e.stdout:
            errs.append("ffmpeg 缺编码器 %s" % enc)
    try:
        from PIL import Image  # noqa
    except ImportError:
        errs.append("缺 Pillow：pip install -r tasks/8b/video/requirements.txt")


def main():
    if len(sys.argv) < 2 or not re.fullmatch(r"unit0[1-8]", sys.argv[1]):
        sys.exit("用法：python 自检.py unit01 … unit08 [仓库根目录]")
    u = sys.argv[1]
    root = sys.argv[2] if len(sys.argv) > 2 else "."
    out = os.path.join(root, "results", "8b", u, "video")
    aud = os.path.join(root, "results", "8b", u, "audio")
    data_p = os.path.join(root, "tasks", "8b", "video", "data_%s.json" % u)
    errs, warns = [], []

    print("== %s 视频产物自检 ==" % u, flush=True)
    env_check(errs)
    if errs:
        for e in errs:
            print("   ✗ " + e)
        print("\n  ❌ FAIL（环境不满足），先修环境再渲染"); sys.exit(1)
    print("   环境 OK：ffmpeg / ffprobe / libass / libx264 / aac / Pillow", flush=True)

    if not os.path.isfile(data_p):
        print("\n  ❌ FAIL  缺 %s" % data_p); sys.exit(1)
    d = json.load(open(data_p, encoding="utf-8"))
    lessons = d["lessons"]
    want_dirs = [x["key"] for x in lessons]
    if not os.path.isdir(out):
        print("\n  ❌ FAIL  缺输出目录 %s" % out); sys.exit(1)

    got = sorted(x for x in os.listdir(out) if os.path.isdir(os.path.join(out, x)))
    if got != sorted(want_dirs):
        extra = [x for x in got if x not in want_dirs]
        miss = [x for x in want_dirs if x not in got]
        if extra: errs.append("多余课包目录：%s" % extra)
        if miss: errs.append("缺课包目录：%s" % miss)

    for les in lessons:
        k = les["key"]
        p = os.path.join(out, k)
        if not os.path.isdir(p):
            continue
        fs = sorted(f for f in os.listdir(p) if os.path.isfile(os.path.join(p, f)))
        extra = [f for f in fs if f not in FILES]
        miss = [f for f in FILES if f not in fs]
        if extra: errs.append("%s 目录多余文件：%s" % (k, extra[:5]))
        if miss: errs.append("%s 缺文件：%s" % (k, miss))
        if miss:
            continue

        mp4 = os.path.join(p, "视频.mp4")
        mp3 = os.path.join(p, "音频.mp3")
        png = os.path.join(p, "封面.png")
        src_mp3 = os.path.join(aud, k + ".mp3")
        tlf = os.path.join(aud, k + ".timeline.json")

        # 视频流参数
        pf = probe(mp4)
        fmt = pf.get("format", {})
        v = next((s for s in pf.get("streams", []) if s.get("codec_type") == "video"), {})
        a = next((s for s in pf.get("streams", []) if s.get("codec_type") == "audio"), {})
        vd = duration(mp4)
        ad = duration(mp3)
        if v.get("width") != 1080 or v.get("height") != 1920:
            errs.append("%s 分辨率 %sx%s（应 1080x1920）" % (k, v.get("width"), v.get("height")))
        if v.get("codec_name") != "h264":
            errs.append("%s 视频编码 %s（应 h264）" % (k, v.get("codec_name")))
        if not a:
            errs.append("%s 无音频流" % k)
        if v.get("r_frame_rate") not in ("24/1", "24/0"):
            warns.append("%s 帧率 %s（期望 24/1）" % (k, v.get("r_frame_rate")))
        if vd < 20:
            errs.append("%s 视频时长 %.1fs < 20s" % (k, vd))

        # 全帧解码
        dec = run(["ffmpeg", "-v", "error", "-i", mp4, "-f", "null", "-"], 600)
        if dec.returncode:
            errs.append("%s 全帧解码失败：%s" % (k, dec.stderr[-160:]))

        # 音画 / 时间轴对齐
        if abs(vd - ad) > 1.0:
            errs.append("%s 音画时长差 %.2fs > 1s" % (k, abs(vd - ad)))
        if os.path.isfile(tlf):
            total = json.load(open(tlf, encoding="utf-8"))["total"]
            if abs(vd - total) > 1.0:
                errs.append("%s 视频 %.1fs 与 timeline total %.1fs 差 >1s" % (k, vd, total))
        if os.path.isfile(src_mp3):
            if sha256(mp3) != sha256(src_mp3):
                errs.append("%s 音频.mp3 与已验收源音频不一致（必须原样复制，不得重编码）" % k)
        else:
            warns.append("%s 找不到源音频，跳过 sha256 比对" % k)

        # 封面
        try:
            from PIL import Image
            im = Image.open(png)
            if im.size != (1080, 1920) or im.format != "PNG":
                errs.append("%s 封面 %s %s（应 1080x1920 PNG）" % (k, im.size, im.format))
        except Exception as e:
            errs.append("%s 封面不可读：%s" % (k, e))

        # 可选：本地临时 ASS 还在的话，验译文事件数
        ass = os.path.join(root, "_8b_video_tmp", k, "page.ass")
        if os.path.isfile(ass):
            n = sum(1 for l in open(ass, encoding="utf-8") if ",Tr," in l)
            if n != len(les["zh"]):
                errs.append("%s ASS 译文事件 %d / 期望 %d" % (k, n, len(les["zh"])))

        print("   %-16s %6.1fs  %sx%s  %s  %s" % (
            k, vd, v.get("width"), v.get("height"),
            "%dkbps" % (int(fmt.get("bit_rate", 0)) // 1000),
            "OK" if not any(e.startswith(k) for e in errs) else "FAIL"), flush=True)

    for w in warns:
        print("   ⚠ " + w)
    for e in errs:
        print("   ✗ " + e)
    print("\n   课包 %d / 期望 %d" % (len(got), len(lessons)))
    if errs:
        print("\n  ❌ FAIL（%d 项），不要提交" % len(errs)); sys.exit(1)
    print("\n  ✅ PASS — %d 个课包可以提交" % len(lessons))


if __name__ == "__main__":
    main()
