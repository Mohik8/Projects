import puppeteer from "puppeteer";
import { existsSync, mkdirSync } from "fs";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

const __dir = dirname(fileURLToPath(import.meta.url));
if (!existsSync(__dir)) mkdirSync(__dir, { recursive: true });

const PAGES = [
  { url: "http://localhost:3000",                                         file: "01-home.png",     wait: 1000 },
  { url: "http://localhost:3000/query?q=Can+I+run+an+Airbnb+in+Saanich", file: "02-query.png",    wait: 4000 },
  { url: "http://localhost:3000/optimize",                                file: "03-optimize.png", wait: 800  },
  { url: "http://localhost:3000/bylaws",                                  file: "04-bylaws.png",   wait: 2500 },
];

const browser = await puppeteer.launch({ headless: "new", args: ["--no-sandbox"] });
const page = await browser.newPage();
await page.setViewport({ width: 1440, height: 900 });

for (const { url, file, wait } of PAGES) {
  console.log(`→ ${file}`);
  await page.goto(url, { waitUntil: "networkidle2", timeout: 20000 });
  await new Promise(r => setTimeout(r, wait));
  await page.screenshot({ path: join(__dir, file), fullPage: false });
  console.log(`  ✓ saved`);
}

await browser.close();
console.log("\nAll screenshots saved to screenshots/");
