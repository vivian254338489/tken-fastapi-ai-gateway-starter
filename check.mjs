import fs from "node:fs";

const required = ["README.md", "LICENSE", "PROMOTION.md", ".env.example", "package.json", "requirements.txt", "app.py", "check.mjs", ".github/workflows/check.yml"];
const missing = required.filter((file) => !fs.existsSync(file));

if (missing.length) {
  console.error(`Missing files: ${missing.join(", ")}`);
  process.exit(1);
}

const app = fs.readFileSync("app.py", "utf8");
for (const text of ["FastAPI", "https://www.tken.shop/v1", "/v1/chat/completions", "free-model", "premium-gpt"]) {
  if (!app.includes(text)) {
    console.error(`app.py missing expected text: ${text}`);
    process.exit(1);
  }
}

const readme = fs.readFileSync("README.md", "utf8");
for (const text of ["FastAPI", "https://www.tken.shop/v1", "/v1/models"]) {
  if (!readme.includes(text)) {
    console.error(`README missing expected text: ${text}`);
    process.exit(1);
  }
}

console.log(JSON.stringify({ ok: true, checked: required.length }, null, 2));
