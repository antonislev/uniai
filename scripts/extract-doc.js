// scripts/extract-doc.js
const fs = require("fs");
const path = require("path");
const pdf = require("pdf-parse");

(async () => {
  const pdfPath = path.join(__dirname, "../data/bmw_x1.pdf");
  const buffer = fs.readFileSync(pdfPath);
  const { text } = await pdf(buffer);

  // Split by page breaks (\f), tweak as needed
  const pages = text.split("\f");

  const chapters = pages.map((p, i) => ({
    id: i + 1,
    title: `Page ${i + 1}`,
    text: p.trim(),
    images: []  // no images pulled by this script
  }));

  const outDir = path.join(__dirname, "../frontend/public/docs");
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });
  fs.writeFileSync(
    path.join(outDir, "data.json"),
    JSON.stringify(chapters, null, 2),
    "utf-8"
  );
  console.log("✅ data.json written with", chapters.length, "chapters");
})().catch(console.error);

