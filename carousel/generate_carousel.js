/**
 * Carousel/Image Generator - Puppeteer
 * daily_posts.json se har post ke 4-slide carousel (Hook/Problem/Solution/CTA)
 * ke dono language versions (EN + UR) banata hai, hook slide par story-relevant
 * fixed-character illustration bhi composite karta hai.
 *
 * Design: bold high-contrast single-accent-per-post theme (rotates daily from
 * THEMES array) + Archivo Black high-impact hook headline + Fraunces bold serif
 * for body slides + keyword highlight boxes. Colors/fonts change karne ho to
 * THEMES aur font-family CSS badlo.
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const OUTPUT_DIR = path.join(__dirname, '..', 'output', 'images');
const POSTS_JSON = path.join(__dirname, '..', 'output', 'daily_posts.json');

// Har post ka apna EK accent theme hota hai (poore carousel mein consistent) -
// roz alag theme rotate hota hai taake variety rahe, lekin ek carousel ke andar
// cohesive/bold single-color-punch look bane (jaisa high-attention agency content)
const THEMES = [
  { name: 'crimson', bgGradient: 'linear-gradient(155deg, #1A0A0A 0%, #0A0A0A 65%)', accent: '#E8453F' },
  { name: 'gold', bgGradient: 'linear-gradient(155deg, #1A1610 0%, #0A0A0A 65%)', accent: '#D4AF37' },
  { name: 'emerald', bgGradient: 'linear-gradient(155deg, #0B1F17 0%, #0A0F0D 65%)', accent: '#C8A96B' },
  { name: 'violet', bgGradient: 'linear-gradient(155deg, #150F1F 0%, #0A0A0A 65%)', accent: '#9D6FFF' },
  { name: 'ice', bgGradient: 'linear-gradient(155deg, #0A1420 0%, #0A0A0A 65%)', accent: '#4FC3F7' },
];

function getTheme(postIndex) {
  return THEMES[postIndex % THEMES.length];
}

// Icons ab function hain (accent color dynamically inject hota hai, theme ke hisaab se)
const SLIDE_ICONS = {
  hook: () => '',
  problem: (accent) => `<svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="${accent}" stroke-width="1.8"><path d="M12 2 L22 20 H2 Z" stroke-linejoin="round"/><line x1="12" y1="9" x2="12" y2="14"/><circle cx="12" cy="17" r="0.6" fill="${accent}"/></svg>`,
  solution: (accent) => `<svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="${accent}" stroke-width="1.8"><circle cx="12" cy="12" r="9.5"/><path d="M7.5 12.5 L10.5 15.5 L16.5 8.5" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
  cta: (accent) => `<svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="${accent}" stroke-width="2"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12,5 19,12 12,19" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
};

const SLIDE_KICKERS = {
  hook: '',
  problem: 'THE PROBLEM',
  solution: 'THE FIX',
  cta: 'NEXT STEP',
};

// Font sizes per slide - hook bilkul bold/huge (Archivo Black), baaki Fraunces bold serif
const FONT_SIZE = { hook: '92px', problem: '42px', solution: '42px', cta: '46px' };

const SLIDE_ORDER = ['hook', 'problem', 'solution', 'cta'];

function buildHTML(text, slideType, slideIndex, totalSlides, brandName, illustrationPath, theme) {
  const isCta = slideType === 'cta';
  // Non-CTA slides: near-black bg + accent color pops. CTA slide: solid accent bg (inverted, loud stop-scroll moment)
  const bg = isCta ? theme.accent : theme.bgGradient;
  const textColor = isCta ? '#0A0A0A' : '#F5F5F5';
  const lineColor = isCta ? '#0A0A0A' : theme.accent;
  const mutedColor = isCta ? 'rgba(10,10,10,0.5)' : 'rgba(245,245,245,0.45)';
  const icon = SLIDE_ICONS[slideType](lineColor);
  const kicker = SLIDE_KICKERS[slideType];
  const fontSize = FONT_SIZE[slideType];
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
      @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,650;9..144,700&family=Manrope:wght@400;500;600;700;800&family=Archivo+Black&display=swap');
      * { margin: 0; padding: 0; box-sizing: border-box; }
      body {
        width: 1080px;
        height: 1350px;
        background: ${bg};
        font-family: 'Manrope', sans-serif;
        position: relative;
        overflow: hidden;
      }
      .diag-accent {
        position: absolute;
        top: 0; right: 0;
        width: 340px; height: 340px;
        border-left: 1px solid ${isCta ? 'rgba(10,10,10,0.15)' : 'rgba(255,255,255,0.12)'};
        border-bottom: 1px solid ${isCta ? 'rgba(10,10,10,0.15)' : 'rgba(255,255,255,0.12)'};
        transform: rotate(45deg) translate(120px, -180px);
      }
      .grid-bg {
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background-image: radial-gradient(${isCta ? 'rgba(10,10,10,0.12)' : 'rgba(255,255,255,0.06)'} 1.5px, transparent 1.5px);
        background-size: 28px 28px;
      }
      .hl {
        background: ${lineColor};
        color: ${isCta ? '#F5F5F5' : '#0A0A0A'};
        padding: 2px 12px;
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
        color: ${lineColor};
        font-size: 22px;
        font-weight: 800;
        letter-spacing: 1px;
        font-family: 'Manrope', sans-serif;
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
      .illustration-wrap {
        position: relative;
        margin-bottom: 20px;
        align-self: center;
      }
      .illustration-glow {
        position: absolute;
        inset: -50px;
        background: radial-gradient(circle, ${lineColor}33 0%, transparent 70%);
        filter: blur(30px);
        z-index: 0;
      }
      .illustration {
        position: relative;
        width: 420px;
        height: auto;
        object-fit: contain;
        z-index: 1;
        -webkit-mask-image: radial-gradient(ellipse 68% 72% at center, black 55%, transparent 100%);
        mask-image: radial-gradient(ellipse 68% 72% at center, black 55%, transparent 100%);
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
        color: ${textColor};
        font-family: ${slideType === 'hook' ? "'Archivo Black', sans-serif" : "'Fraunces', serif"};
        font-size: ${fontSize};
        font-weight: ${slideType === 'hook' ? 400 : 700};
        line-height: ${slideType === 'hook' ? 1.05 : 1.3};
        max-width: 880px;
        letter-spacing: ${slideType === 'hook' ? '-1px' : '-0.3px'};
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
        background: #0A0A0A;
        color: #F5F5F5;
        padding: 18px 32px;
        border-radius: 100px;
        font-size: 24px;
        font-weight: 700;
        font-family: 'Manrope', sans-serif;
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
      .save-tag {
        display: flex;
        align-items: center;
        gap: 6px;
        color: ${lineColor};
        font-size: 15px;
        font-weight: 700;
        letter-spacing: 1px;
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
      ${showIllustration ? `<div class="illustration-wrap"><div class="illustration-glow"></div><img class="illustration" src="${illustrationSrc}" /></div>` : ''}
      ${icon ? `<div class="icon-wrap">${icon}</div>` : ''}
      ${kicker ? `<div class="kicker">${kicker}</div>` : ''}
      <div class="headline">${highlightText(text)}</div>
      ${slideIndex === 0 && !showIllustration ? '<div class="rule"></div>' : ''}
      ${isCta ? `<div class="cta-btn">Let's talk ${icon}</div>` : ''}
    </div>
    <div class="bottombar">
      <div class="brand">KREAFY.ONLINE</div>
      <div class="progress">
        ${SLIDE_ORDER.map((_, i) => `<div class="progress-dot ${i === slideIndex ? 'active' : ''}"></div>`).join('')}
      </div>
      ${slideIndex <= 1 ? '<div class="swipe">SWIPE →</div>' : (isCta ? '<div class="save-tag"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 3h12a1 1 0 0 1 1 1v17l-7-4-7 4V4a1 1 0 0 1 1-1z"/></svg> SAVE THIS</div>' : '<div style="width:80px"></div>')}
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

    const illustrationPath = path.join(__dirname, '..', 'assets', 'character_poses', `${post.illustration_emotion || 'confident'}.png`);
    const theme = getTheme(i); // ek post = ek theme, poore carousel mein consistent

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
        await page.setContent(buildHTML(text, slideType, s, SLIDE_ORDER.length, brandName, illustrationPath, theme), { waitUntil: 'networkidle0' });
        // ZAROORI FIX: fonts network se load hoti hain lekin render hone mein thoda time
        // lagta hai - is wait ke bina kabhi kabhi default plain font screenshot ho jata
        // tha (Fraunces/Manrope ki jagah). Ye ensure karta hai font pura load ho chuka hai.
        await page.evaluateHandle('document.fonts.ready');
        await new Promise((resolve) => setTimeout(resolve, 200)); // chhota safety buffer

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
