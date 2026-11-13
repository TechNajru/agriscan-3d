// Copies the shared English/Hindi text (repo-level /i18n) into the app so backend and frontend use one source.
const fs = require("fs");
const path = require("path");
const candidates = [path.join(__dirname, "..", "..", "i18n"), path.join(__dirname, "..", "i18n-source")];
const src = candidates.find((p) => fs.existsSync(path.join(p, "en.json")));
const dst = path.join(__dirname, "..", "src", "i18n");
fs.mkdirSync(dst, { recursive: true });
if (!src) { console.log("sync-i18n: using existing src/i18n"); process.exit(0); }
for (const f of ["en.json", "hi.json"]) fs.copyFileSync(path.join(src, f), path.join(dst, f));
console.log("sync-i18n: copied", src);
