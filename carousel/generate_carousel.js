/**
 * Carousel/Image Generator - Puppeteer
 * daily_posts.json se har post ke 4-slide carousel (Hook/Problem/Solution/CTA)
 * ke dono language versions (EN + UR) banata hai, hook slide par story-relevant
 * fixed-character illustration bhi composite karta hai.
 *
 * Design: dark premium palette (per-slide color variety) + editorial serif
 * typography + highlighted keyword boxes. Rang/style change karna ho to
 * SLIDE_STYLES aur CSS badlo.
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const OUTPUT_DIR = path.join(__dirname, '..', 'output', 'images');
const POSTS_JSON = path.join(__dirname, '..', 'output', 'daily_posts.json');

// Har slide type ka apna visual treatment - icon + kicker label + editorial typography
// Design: dark luxury (deep emerald/gold/ivory), serif display font for punch, sans for labels
const SLIDE_ICONS = {
  hook: '',
  problem: `<svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#C8A96B" stroke-width="1.6"><path d="M12 2 L22 20 H2 Z" stroke-linejoin="round"/><line x1="12" y1="9" x2="12" y2="14"/><circle cx="12" cy="17" r="0.6" fill="#C8A96B"/></svg>`,
  solution: `<svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#C8A96B" stroke-width="1.6"><circle cx="12" cy="12" r="9.5"/><path d="M7.5 12.5 L10.5 15.5 L16.5 8.5" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
  cta: `<svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#26150A" stroke-width="1.8"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12,5 19,12 12,19" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
};

const SLIDE_KICKERS = {
  hook: '',
  problem: 'THE PROBLEM',
  solution: 'THE FIX',
  cta: 'NEXT STEP',
};

const SLIDE_STYLES = {
  hook: { bg: 'linear-gradient(155deg, #1A1512 0%, #0D0B09 65%)', fontSize: '68px', textColor: '#F5F1E8' },
  problem: { bg: 'linear-gradient(155deg, #3A1220 0%, #24090F 65%)', fontSize: '38px', textColor: '#F5F1E8' },
  solution: { bg: 'linear-gradient(155deg, #0E2E28 0%, #081C18 65%)', fontSize: '38px', textColor: '#F5F1E8' },
  cta: { bg: '#C8A96B', fontSize: '38px', textColor: '#26150A' },
};

const SLIDE_ORDER = ['hook', 'problem', 'solution', 'cta'];

function buildHTML(text, slideType, slideIndex, totalSlides, brandName, illustrationPath) {
  const style = SLIDE_STYLES[slideType];
  const icon = SLIDE_ICONS[slideType];
  const kicker = SLIDE_KICKERS[slideType];
  const isCta = slideType === 'cta';
  const lineColor = isCta ? '#26150A' : '#C8A96B';
  const mutedColor = isCta ? 'rgba(38,21,10,0.55)' : 'rgba(245,241,232,0.5)';
  const showIllustration = slideType === 'hook' && illustrationPath && fs.existsSync(illustrationPath);
  // file:// src Puppeteer ke sandboxed setContent() page mein reliably load nahi hota -
  // isliye base64 data URI use karte hain, jo har environment mein guaranteed chalta hai
  const illustrationSrc = showIllustration
    ? `data:image/png;base64,${fs.readFileSync(illustrationPath).toString('base64')}`
    : '';

  return `
  <!DOCTYPE html>
  <html>
  <head>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,650&family=Manrope:wght@400;500;600;700&display=swap');
      * { margin: 0; padding: 0; box-sizing: border-box; }
      body {
        width: 1080px;
        height: 1350px;
        background: ${style.bg};
        font-family: 'Manrope', sans-serif;
        position: relative;
        overflow: hidden;
      }
      .diag-accent {
        position: absolute;
        top: 0; right: 0;
        width: 340px; height: 340px;
        border-left: 1px solid ${isCta ? 'rgba(11,31,23,0.15)' : 'rgba(200,169,107,0.18)'};
        border-bottom: 1px solid ${isCta ? 'rgba(11,31,23,0.15)' : 'rgba(200,169,107,0.18)'};
        transform: rotate(45deg) translate(120px, -180px);
      }
      .grid-bg {
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background-image: radial-gradient(${isCta ? 'rgba(11,31,23,0.12)' : 'rgba(245,241,232,0.08)'} 1.5px, transparent 1.5px);
        background-size: 28px 28px;
      }
      .hl {
        background: ${isCta ? '#26150A' : '#C8A96B'};
        color: ${isCta ? '#F5F1E8' : '#0B1F17'};
        padding: 2px 10px;
        border-radius: 4px;
        display: inline-block;
      }
      .topbar {
        position: absolute;
        top: 72px; left: 72px; right: 72px;
        display: flex;
        justify-content: space-between;
        align-items: center;
      }
      .mark {
        width: 40px; height: 40px;
        border: 1.5px solid ${lineColor};
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        color: ${lineColor};
        font-family: 'Fraunces', serif;
        font-size: 20px;
        font-weight: 600;
      }
      .pagenum {
        color: ${mutedColor};
        font-size: 15px;
        font-weight: 500;
        letter-spacing: 2px;
      }
      .content {
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: flex-start;
        padding: 0 90px;
      }
      .illustration {
        width: 260px;
        height: 260px;
        object-fit: contain;
        margin-bottom: 30px;
        align-self: center;
      }
      .icon-wrap { margin-bottom: 28px; }
      .kicker {
        color: ${lineColor};
        font-size: 20px;
        font-weight: 600;
        letter-spacing: 4px;
        margin-bottom: 22px;
      }
      .headline {
        color: ${style.textColor};
        font-family: 'Fraunces', serif;
        font-size: ${style.fontSize};
        font-weight: 600;
        line-height: 1.25;
        max-width: 860px;
        letter-spacing: -0.3px;
      }
      .rule {
        width: 64px; height: 4px;
        background: ${lineColor};
        border-radius: 2px;
        margin-top: 36px;
      }
      .cta-btn {
        margin-top: 40px;
        display: inline-flex;
        align-items: center;
        gap: 14px;
        background: #26150A;
        color: #F5F1E8;
        padding: 18px 32px;
        border-radius: 100px;
        font-size: 24px;
        font-weight: 600;
      }
      .bottombar {
        position: absolute;
        bottom: 64px; left: 90px; right: 90px;
        display: flex;
        justify-content: space-between;
        align-items: center;
      }
      .brand {
        color: ${lineColor};
        font-size: 22px;
        font-weight: 600;
        letter-spacing: 1px;
      }
      .progress { display: flex; gap: 8px; }
      .progress-dot {
        width: 8px; height: 8px;
        border-radius: 50%;
        background: ${mutedColor};
      }
      .progress-dot.active {
        background: ${lineColor};
        width: 28px;
        border-radius: 5px;
      }
      .swipe {
        color: ${mutedColor};
        font-size: 17px;
        font-weight: 500;
        letter-spacing: 2px;
      }
    </style>
  </head>
  <body>
    <div class="grid-bg"></div>
    <div class="diag-accent"></div>
    <div class="topbar">
      <div class="mark">K</div>
      <div class="pagenum">${String(slideIndex + 1).padStart(2, '0')} / ${String(totalSlides).padStart(2, '0')}</div>
    </div>
    <div class="content" style="${showIllustration ? 'align-items: center; text-align: center;' : ''}">
      ${showIllustration ? `<img class="illustration" src="${illustrationSrc}" />` : ''}
      ${icon ? `<div class="icon-wrap">${icon}</div>` : ''}
      ${kicker ? `<div class="kicker">${kicker}</div>` : ''}
      <div class="headline">${highlightText(text)}</div>
      ${slideIndex === 0 && !showIllustration ? '<div class="rule"></div>' : ''}
      ${isCta ? `<div class="cta-btn">Let's talk ${SLIDE_ICONS.cta}</div>` : ''}
    </div>
    <div class="bottombar">
      <div class="brand">KREAFY.ONLINE</div>
      <div class="progress">
        ${SLIDE_ORDER.map((_, i) => `<div class="progress-dot ${i === slideIndex ? 'active' : ''}"></div>`).join('')}
      </div>
      ${slideIndex === 0 ? '<div class="swipe">SWIPE →</div>' : '<div style="width:80px"></div>'}
    </div>
  </body>
  </html>
  `;
}

// Content ke andar **word** likha ho to usko highlighted box mein render karta hai
// (jaisa reference image mein "SEO" aur "Future" boxed the) - AI ko yehi marker use karne ko kaha jayega
function highlightText(text) {
  return text.replace(/\*\*(.+?)\*\*/g, '<span class="hl">$1</span>');
}

async function generateImages() {
  if (!fs.existsSync(POSTS_JSON)) {
    console.error('daily_posts.json nahi mila. Pehle content_generator.py chalao.');
    process.exit(1);
  }

  const data = JSON.parse(fs.readFileSync(POSTS_JSON, 'utf-8'));
  const posts = data.posts || [];

  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });

  const brandName = process.env.BRAND_NAME || 'Kreafy Digital';
  const manifest = [];

  for (let i = 0; i < posts.length; i++) {
    const post = posts[i];
    const postDir = path.join(OUTPUT_DIR, `post_${i + 1}`);
    if (!fs.existsSync(postDir)) fs.mkdirSync(postDir, { recursive: true });

    const illustrationPath = path.join(__dirname, '..', 'output', 'illustrations', `post_${i + 1}.png`);

    const langVariants = {
      en: post.carousel_slides_en || [post.carousel_title || `Post ${i + 1}`, '', '', 'DM us to get started'],
      ur: post.carousel_slides_ur || [post.carousel_title || `Post ${i + 1}`, '', '', 'DM karo shuru karne ke liye'],
    };

    const slidesByLang = {};

    for (const lang of Object.keys(langVariants)) {
      const slides = langVariants[lang];
      const langDir = path.join(postDir, lang);
      if (!fs.existsSync(langDir)) fs.mkdirSync(langDir, { recursive: true });

      const slidePaths = [];

      for (let s = 0; s < SLIDE_ORDER.length; s++) {
        const slideType = SLIDE_ORDER[s];
        const text = slides[s] || '';

        const page = await browser.newPage();
        await page.setViewport({ width: 1080, height: 1350 }); // 4:5 ratio - IG/LinkedIn carousel standard
        await page.setContent(buildHTML(text, slideType, s, SLIDE_ORDER.length, brandName, illustrationPath), { waitUntil: 'networkidle0' });

        const imgPath = path.join(langDir, `slide_${s + 1}_${slideType}.png`);
        await page.screenshot({ path: imgPath });
        await page.close();

        slidePaths.push(imgPath);
      }

      slidesByLang[lang] = slidePaths;
    }

    manifest.push({
      post_index: i + 1,
      service: post.service || '',
      slides_en: slidesByLang.en,
      slides_ur: slidesByLang.ur,
    });

    console.log(`Post ${i + 1}/${posts.length}: EN + UR carousels generate hui -> ${postDir}`);
  }

  await browser.close();

  fs.writeFileSync(
    path.join(OUTPUT_DIR, 'manifest.json'),
    JSON.stringify({ generated_at: new Date().toISOString(), posts: manifest }, null, 2)
  );

  console.log(`Total ${manifest.length} posts x 2 languages x ${SLIDE_ORDER.length} slides generate ho gaye. Folder: ${OUTPUT_DIR}`);
}

generateImages().catch((err) => {
  console.error('Carousel generation fail ho gaya:', err);
  process.exit(1);
});
