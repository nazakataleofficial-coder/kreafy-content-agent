/**
 * Hot-Take Image Generator - Puppeteer
 * hottake_post.json se "photo_mood" ke mutabiq real photo (assets/real_photos/<mood>.png)
 * uthata hai aur uspar "image_caption" (2-4 words, bold caps) overlay karta hai.
 * Do sizes banata hai: 4:5 (LinkedIn/Instagram) aur 16:9 (Twitter, jahan tall crop
 * platform khud bura crop kar deta hai isliye wide version alag banana zaroori hai).
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const OUTPUT_DIR = path.join(__dirname, '..', 'output', 'hottake');
const HOTTAKE_JSON = path.join(__dirname, '..', 'output', 'hottake_post.json');
const PHOTOS_DIR = path.join(__dirname, '..', 'assets', 'real_photos');

function buildHTML(photoSrc, captionText, width, height) {
  return `
  <!DOCTYPE html>
  <html>
  <head>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Archivo+Black&family=Manrope:wght@600;800&display=swap');
      * { margin: 0; padding: 0; box-sizing: border-box; }
      body { width: ${width}px; height: ${height}px; overflow: hidden; position: relative; font-family: 'Manrope', sans-serif; }
      .photo {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        object-fit: cover; object-position: center 20%;
      }
      .fade {
        position: absolute; left: 0; right: 0; bottom: 0; height: 55%;
        background: linear-gradient(to top, rgba(6,6,6,0.95) 0%, rgba(6,6,6,0.55) 55%, transparent 100%);
      }
      .topfade {
        position: absolute; left: 0; right: 0; top: 0; height: 18%;
        background: linear-gradient(to bottom, rgba(0,0,0,0.45) 0%, transparent 100%);
      }
      .caption {
        position: absolute; left: 64px; right: 64px; bottom: 96px;
        font-family: 'Archivo Black', sans-serif;
        color: #FFFFFF;
        font-size: ${width < height ? '84px' : '58px'};
        line-height: 1.05;
        letter-spacing: -1px;
        text-transform: uppercase;
      }
      .accent-bar {
        position: absolute; left: 64px; bottom: 64px;
        width: 64px; height: 6px; background: #D4AF37; border-radius: 3px;
      }
      .topbar {
        position: absolute; top: 40px; left: 64px; right: 64px;
        display: flex; justify-content: space-between; align-items: center;
      }
      .mark {
        width: 40px; height: 40px; border: 1.5px solid #D4AF37; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        color: #D4AF37; font-family: 'Archivo Black', sans-serif; font-size: 18px;
        background: rgba(0,0,0,0.3);
      }
      .brand {
        color: #D4AF37; font-size: 20px; font-weight: 800; letter-spacing: 1px;
      }
    </style>
  </head>
  <body>
    <img class="photo" src="${photoSrc}" />
    <div class="topfade"></div>
    <div class="fade"></div>
    <div class="topbar">
      <div class="mark">K</div>
      <div class="brand">KREAFY.ONLINE</div>
    </div>
    <div class="caption">${captionText}</div>
    <div class="accent-bar"></div>
  </body>
  </html>
  `;
}

async function generateHottakeImage() {
  if (!fs.existsSync(HOTTAKE_JSON)) {
    console.error('hottake_post.json nahi mila. Pehle hottake_generator.py chalao.');
    process.exit(1);
  }

  const data = JSON.parse(fs.readFileSync(HOTTAKE_JSON, 'utf-8'));
  const post = data.post || {};
  const mood = post.photo_mood || 'confident';
  const captionText = (post.image_caption || 'REAL TALK').toUpperCase();

  const photoPath = path.join(PHOTOS_DIR, `${mood}.png`);
  if (!fs.existsSync(photoPath)) {
    console.error(`Photo nahi mili: ${photoPath}. assets/real_photos/ mein 6 mood photos honi chahiye (confident, stern, thoughtful, warm, casual, determined).`);
    process.exit(1);
  }
  const photoSrc = `data:image/png;base64,${fs.readFileSync(photoPath).toString('base64')}`;

  if (!fs.existsSync(OUTPUT_DIR)) fs.mkdirSync(OUTPUT_DIR, { recursive: true });

  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });

  // Main version - 4:5 (LinkedIn feed + Instagram)
  const mainPage = await browser.newPage();
  await mainPage.setViewport({ width: 1080, height: 1350 });
  await mainPage.setContent(buildHTML(photoSrc, captionText, 1080, 1350), { waitUntil: 'networkidle0' });
  await mainPage.evaluateHandle('document.fonts.ready');
  await new Promise((r) => setTimeout(r, 200));
  const mainOut = path.join(OUTPUT_DIR, 'hottake_main.png');
  await mainPage.screenshot({ path: mainOut });
  await mainPage.close();

  // Twitter version - 16:9 wide crop (tall image X pe bura crop hota hai, isliye alag)
  const twPage = await browser.newPage();
  await twPage.setViewport({ width: 1200, height: 675 });
  await twPage.setContent(buildHTML(photoSrc, captionText, 1200, 675), { waitUntil: 'networkidle0' });
  await twPage.evaluateHandle('document.fonts.ready');
  await new Promise((r) => setTimeout(r, 200));
  const twOut = path.join(OUTPUT_DIR, 'hottake_twitter.png');
  await twPage.screenshot({ path: twOut });
  await twPage.close();

  await browser.close();

  const manifest = {
    generated_at: new Date().toISOString(),
    niche_id: post.niche_id || '',
    photo_mood: mood,
    image_caption: captionText,
    main_image: mainOut,
    twitter_image: twOut,
  };
  fs.writeFileSync(path.join(OUTPUT_DIR, 'manifest.json'), JSON.stringify(manifest, null, 2));

  console.log(`Hot-take images ban gayi (mood: ${mood}) -> ${OUTPUT_DIR}`);
}

generateHottakeImage().catch((err) => {
  console.error('Hot-take image generation fail ho gaya:', err);
  process.exit(1);
});
