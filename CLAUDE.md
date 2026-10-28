# 시리 토익 (토익 독종반 단어장)

토익 독종반 단어 PDF(1~1200번)를 웹 단어장으로 만든 프로젝트. 빌드 도구 없이 `index.html`을 브라우저로 바로 연다.

## 구조
- `docs/index.html` — 앱 전체(HTML·CSS·JS 한 파일). 프레임워크 없음. GitHub Pages가 `docs/`를 서빙한다.
- `docs/words.enc.json` — 앱이 읽는 **암호화된** 데이터. 직접 고치지 말 것. `PASSCODE=... node scripts/build_secure.mjs`가 만든다.
- `data/examples_siri.json` — 시리의 일상 예문 `{ "id": ["English", "한국어"] }` (영어에 he/she 대신 'Siri'만 사용)
- `docs/sw.js`, `manifest.webmanifest`, `icon-*.png` — PWA(홈 화면 설치·오프라인)
- `data/ipa.json` — 미국식 발음기호 `{ "id": "ɪɡˈzɛkjətɪv" }`. `python3 scripts/make_ipa.py`(pip install cmudict)가 만든다.
- `data/raw.json` — PDF에서 뽑은 단어 원본 `{id, word, meanings:[{pos, meaning}]}`
- `data/examples.json` — 예문 `{ "id": ["English sentence", "한국어 해석"] }`
- `data/overrides.json` — PDF 추출이 깨진 행을 손으로 바로잡은 값
- `scripts/extract_pdf.py` — PDF → raw.json (`python3 scripts/extract_pdf.py <pdf폴더> data/raw.json data/overrides.json`)
- `scripts/build_secure.mjs` — raw + examples + examples_siri → docs/words.enc.json (AES-GCM)

## 데이터 수정 흐름
1. `data/*.json`을 고친다
2. (단어 목록이 바뀌었으면) `python3 scripts/make_ipa.py`
3. `PASSCODE='비밀번호' node scripts/build_secure.mjs`
4. `docs/`를 커밋·푸시 (`data/`는 .gitignore — 평문 원본은 올리지 않는다)

## 기능
- 블라인드: 끔 / 영어 가리기 / 뜻 가리기. 가린 칸은 빨간 암기 시트 모양, 탭하면 하나씩 열림. 영어 가리기면 예문 속 표제어도 빈칸 처리.
- 예문: 영어 예문 + 해석, 예문 속 표제어 강조, 예문 듣기 버튼.
- 발음: 브라우저 내장 Web Speech API(`speechSynthesis`). 억양(미/영/호), 속도 선택. 인터넷·API 키 불필요.
- 세트는 25단어 단위(48세트). 단어 옆에 /발음기호/가 보이고 영어 블라인드 때 같이 가려진다.
- 목록/카드 모드, 외운 단어 체크(localStorage), 안 외운 것만 보기, 섞기.
- 카드 모드 단축키: ← → 이동, Space 뒤집기, P 발음, K 외움.

## 규칙
- 예문은 토익 Part 5·6·7에 나올 법한 비즈니스 문장, 15단어 안팎, 표제어 그대로 또는 기본 변화형 사용.
- 해석은 자연스러운 한국어, 직역투 피하기.
- 디자인 토큰은 `index.html` 맨 위 `:root`에 있다. 색은 반드시 토큰으로.
