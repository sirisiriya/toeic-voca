"""data/raw.json -> data/ipa.json (미국식 IPA). 사전: pip install cmudict
사용: python3 scripts/make_ipa.py
"""
import json, pathlib, cmudict

root = pathlib.Path(__file__).resolve().parent.parent
D = cmudict.dict()
V = {"AA":"ɑ","AE":"æ","AH":"ʌ","AO":"ɔ","AW":"aʊ","AY":"aɪ","EH":"ɛ","ER":"ɝ","EY":"eɪ","IH":"ɪ","IY":"i","OW":"oʊ","OY":"ɔɪ","UH":"ʊ","UW":"u"}
C = {"B":"b","CH":"tʃ","D":"d","DH":"ð","F":"f","G":"ɡ","HH":"h","JH":"dʒ","K":"k","L":"l","M":"m","N":"n","NG":"ŋ","P":"p","R":"r","S":"s","SH":"ʃ","T":"t","TH":"θ","V":"v","W":"w","Y":"j","Z":"z","ZH":"ʒ"}
STOPS = {"P","B","T","D","K","G"}
def onset_ok(cs):
    if len(cs) <= 1: return cs != ["NG"]
    if len(cs) == 2:
        a, b = cs
        return ((a in STOPS | {"F","TH","SH"} and b == "R") or (a in {"P","B","K","G","F","S"} and b == "L")
                or (a == "S" and b in {"P","T","K","M","N","F","W","L"}) or (a in {"T","D","K","G","TH"} and b == "W")
                or (a in STOPS | {"F","V","M","N","HH","S","Z","L"} and b == "Y"))
    if len(cs) == 3:
        return cs[0] == "S" and cs[1] in {"P","T","K"} and cs[2] in {"R","L","W","Y"}
    return False

def to_ipa(ph):
    syl = []  # (onset consonants, vowel arpa, stress)
    cur = []
    for p in ph:
        base = p.rstrip("012")
        if base in V:
            syl.append([cur, base, p[-1] if p[-1] in "012" else "0", []]); cur = []
        else:
            cur.append(base)
    if syl: syl[-1][3] = cur
    # 모음 사이 자음을 최대 onset 규칙으로 앞 음절 coda / 뒤 음절 onset으로 나눈다
    for i in range(1, len(syl)):
        cs = syl[i][0]; k = 0
        while k < len(cs) and not onset_ok(cs[k:]): k += 1
        syl[i-1][3] = cs[:k]; syl[i][0] = cs[k:]
    out = ""
    for on, v, st, co in syl:
        mark = "ˈ" if st == "1" else "ˌ" if st == "2" else ""
        vo = "ə" if (v == "AH" and st == "0") else "ɚ" if (v == "ER" and st == "0") else V[v]
        out += mark + "".join(C[c] for c in on) + vo + "".join(C[c] for c in co)
    return out

MANUAL = {"altercate":"ˈɔltɚˌkeɪt","deteriorative":"dɪˈtɪriəˌreɪtɪv","re-energize":"ˌriˈɛnɚˌdʒaɪz",
          "preconditioned":"ˌprikənˈdɪʃənd","indistinctly":"ˌɪndɪˈstɪŋktli","gratifyingly":"ˈɡrætɪˌfaɪɪŋli",
          "headhunting":"ˈhɛdˌhʌntɪŋ"}
def word_ipa(w):
    w = w.lower().strip()
    if w in MANUAL: return MANUAL[w]
    if w in D: return to_ipa(D[w][0])
    if "-" in w: return " ".join(word_ipa(x) for x in w.split("-"))
    return ""

raw = json.loads((root / "data/raw.json").read_text(encoding="utf-8"))
res = {str(w["id"]): word_ipa(w["word"]) for w in raw}
(root / "data/ipa.json").write_text(json.dumps(res, ensure_ascii=False, indent=0), encoding="utf-8")
print(len(res), "words, missing:", [w["word"] for w in raw if not res[str(w["id"])]])
for i in (1,2,3,20,35,44,100,300): print(raw[i-1]["word"], "/"+res[str(i)]+"/")
