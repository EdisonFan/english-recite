import asyncio, json, os, subprocess, wave
import edge_tts, imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
print("FFMPEG=" + FF, flush=True)
SR, GAP, RATE = 16000, 0.75, "-10%"
os.makedirs("output", exist_ok=True)
data = json.load(open("data.json", encoding="utf-8"))


def ff(args):
    subprocess.run([FF, "-y", "-loglevel", "error"] + args, check=True)


async def synth(text, voice, path):
    last = None
    for a in range(4):
        try:
            c = edge_tts.Communicate(text, voice, rate=RATE)
            await c.save(path)
            if os.path.getsize(path) > 1000:
                return
            last = "empty audio"
        except Exception as e:
            last = type(e).__name__ + ": " + str(e)[:180]
        await asyncio.sleep(2 + 2 * a)
    raise RuntimeError("edge-tts failed: " + str(last))


async def main():
    report = {}
    for les in data["lessons"]:
        key = les["key"]
        pcm, timeline, cursor = [], [], 0.0
        print(f"=== {key} {len(les['lines'])} 句 ===", flush=True)
        for i, ln in enumerate(les["lines"], 1):
            mp3 = f"/tmp/{key}_{i:02d}.mp3"
            wav = f"/tmp/{key}_{i:02d}.wav"
            await synth(ln["text"], ln["voice"], mp3)
            ff(["-i", mp3, "-ac", "1", "-ar", str(SR), "-c:a", "pcm_s16le", wav])
            with wave.open(wav, "rb") as f:
                dur = f.getnframes() / f.getframerate()
                pcm.append(f.readframes(f.getnframes()))
            pcm.append(b"\x00\x00" * int(SR * GAP))
            timeline.append({"start": cursor, "end": cursor + dur + GAP,
                             "role": ln["role"], "text": ln["text"]})
            cursor += dur + GAP
            print(f"  {i:02d}/{len(les['lines'])} {ln['role']:<11} {dur:5.2f}s", flush=True)
            os.remove(mp3); os.remove(wav)
        wav_out = f"/tmp/{key}.wav"
        with wave.open(wav_out, "wb") as f:
            f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR)
            f.writeframes(b"".join(pcm))
        mp3_out = f"output/{key}.mp3"
        try:
            ff(["-i", wav_out, "-af", "loudnorm=I=-17:TP=-1.5:LRA=11",
                "-codec:a", "libmp3lame", "-q:a", "2", mp3_out])
        except subprocess.CalledProcessError:
            ff(["-i", wav_out, "-codec:a", "libmp3lame", "-q:a", "2", mp3_out])
        json.dump({"key": key, "no": les["no"], "title": les["title"],
                   "title_zh": les["title_zh"], "kind": les["kind"],
                   "timeline": timeline, "total": cursor},
                  open(f"output/{key}.timeline.json", "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        report[key] = {"sentences": len(timeline), "total": round(cursor, 2),
                       "mp3_bytes": os.path.getsize(mp3_out)}
        print(f"  ✓ {key} 总 {cursor:.1f}s  mp3 {os.path.getsize(mp3_out)//1024}KB", flush=True)
    json.dump(report, open("output/report.json", "w"), indent=2)
    print("REPORT=" + json.dumps(report), flush=True)


asyncio.run(main())
