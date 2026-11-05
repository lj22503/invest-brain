// Copy the Next static export (out/) into the Tauri frontend directory (desktop/ui).
// Shell-agnostic on purpose: the release workflow runs npm scripts under cmd on the Windows runner.
const fs = require("node:fs");
const path = require("node:path");

// `out/` is produced in the directory next build runs in (repo root or app/),
// while the Tauri frontend dir is always <repo>/desktop/ui.
const repoRoot = path.resolve(__dirname, "..");
const from = path.resolve(process.cwd(), "out");
const to = path.join(repoRoot, "desktop", "ui");

if (!fs.existsSync(from)) throw new Error("out/ missing: run `next build` first");
fs.rmSync(to, { recursive: true, force: true });
fs.cpSync(from, to, { recursive: true });
console.log(`ui: copied ${fs.readdirSync(to).length} entries from out/ to desktop/ui`);
