import { bundle } from "@remotion/bundler"; import { selectComposition, renderStill } from "@remotion/renderer"; import path from "path";
const BE = "/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell";
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.tsx") });
const [id, ...ts] = process.argv.slice(2);
const comp = await selectComposition({ serveUrl, id, browserExecutable: BE });
for (const t of ts.length ? ts : ["0"]) {
  const frame = Math.round(parseFloat(t) * 30);
  await renderStill({ composition: comp, serveUrl, frame, output: `out/${id}_${t}.png`, browserExecutable: BE, chromiumOptions: { gl: "swangle" } });
  console.log("ok", t);
}
