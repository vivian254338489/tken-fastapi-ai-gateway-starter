const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
const ignoredDirs = new Set([".git", ".venv", "venv", "node_modules", "__pycache__"]);
const ignoredFiles = new Set(["scan-secrets.js"]);

const patterns = [
  { name: "OpenAI API key", regex: /sk-[A-Za-z0-9_-]{20,}/g },
  { name: "Generic bearer token", regex: /Bearer\s+[A-Za-z0-9._~+/=-]{32,}/g },
  { name: "AWS access key", regex: /AKIA[0-9A-Z]{16}/g },
  { name: "Private key block", regex: /-----BEGIN (RSA |EC |OPENSSH |)PRIVATE KEY-----/g },
];

const findings = [];

function walk(dir) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const fullPath = path.join(dir, entry.name);
    const rel = path.relative(root, fullPath);
    if (entry.isDirectory()) {
      if (!ignoredDirs.has(entry.name)) walk(fullPath);
      continue;
    }
    if (ignoredFiles.has(entry.name)) continue;
    const text = fs.readFileSync(fullPath, "utf8");
    for (const pattern of patterns) {
      const matches = text.match(pattern.regex);
      if (matches) {
        findings.push(`${rel}: ${pattern.name}`);
      }
    }
  }
}

walk(root);

if (findings.length) {
  console.error("Potential secrets found:");
  for (const finding of findings) console.error(`- ${finding}`);
  process.exit(1);
}

console.log("No obvious secrets found.");
