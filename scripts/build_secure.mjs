// data/*.json -> docs/words.enc.json (AES-GCM 암호화). 비밀번호는 환경변수 PASSCODE로 넘긴다.
// 사용: PASSCODE='우리끼리비번' node scripts/build_secure.mjs
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { webcrypto as crypto } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const pass = process.env.PASSCODE;
if (!pass || pass.length < 6) { console.error('PASSCODE 환경변수(6자 이상)가 필요해요.'); process.exit(1); }
const ITER = 310000;
const load = p => existsSync(join(root, p)) ? JSON.parse(readFileSync(join(root, p), 'utf8')) : {};
const raw = load('data/raw.json'), ex = load('data/examples.json'), siri = load('data/examples_siri.json'), ipa = load('data/ipa.json');
const rows = raw.map(w => {
  const e = ex[w.id] || ['', ''], s = siri[w.id] || ['', ''];
  return [w.id, w.word, w.meanings.map(m => [m.pos, m.meaning]), e[0], e[1], s[0], s[1], ipa[w.id] || ''];
});
const b64 = u8 => Buffer.from(u8).toString('base64');
const salt = crypto.getRandomValues(new Uint8Array(16)), iv = crypto.getRandomValues(new Uint8Array(12));
const base = await crypto.subtle.importKey('raw', new TextEncoder().encode(pass), 'PBKDF2', false, ['deriveKey']);
const key = await crypto.subtle.deriveKey({ name: 'PBKDF2', salt, iterations: ITER, hash: 'SHA-256' }, base, { name: 'AES-GCM', length: 256 }, false, ['encrypt']);
const ct = await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, key, new TextEncoder().encode(JSON.stringify(rows)));
writeFileSync(join(root, 'docs/words.enc.json'), JSON.stringify({ v: 1, iter: ITER, salt: b64(salt), iv: b64(iv), ct: b64(new Uint8Array(ct)) }));
console.log(`${rows.length} words (${rows.filter(r => r[3]).length} 토익 예문, ${rows.filter(r => r[5]).length} 시리 예문) -> docs/words.enc.json`);
