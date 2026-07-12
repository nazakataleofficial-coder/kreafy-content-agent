# Kreafy Content Agent — Zero-Touch Social Automation

Roz khud: Google Trends (automated) + tumhara weekly curated Reddit material se → 5 unique posts likhta hai (Web Dev / App Dev / YouTube Automation / Animation / AI-Automation rotation, **bilkul simple aasan wording mein**) → har post **2 languages** mein banta hai (LinkedIn/X ke liye English, Facebook ke liye Roman Urdu) → ek **fixed recognizable character** (locked design, story ke hisab se pose/expression badalta hai) ki illustration banti hai → har version ki apni **4-slide scroll-stopping carousel** (Hook → Problem → Solution → CTA) banata hai → Buffer mein khud sahi platform pe sahi language post kar deta hai.

**⚠️ 2 zaroori limitations jo test karni hain:**
1. Buffer ka naya API (2026) images ka **public URL** maangta hai, direct upload nahi. Isliye repo **public** hona zaroori hai (images GitHub mein push hoti hain, wahan se raw URL Buffer ko diya jata hai). Pehli run ke baad **khud LinkedIn/FB/X pe jaake check karo** ke carousel sahi bana ya nahi — kabhi platform ki taraf se sirf ek image use ho sakti hai.
2. Gemini ka image-generation model ka naam (`GEMINI_IMAGE_MODEL` in `generator/illustration_generator.py`) Google AI Studio mein badalta rehta hai. Pehli run fail ho to https://aistudio.google.com par jaake current image model ka naam check kar lena.

---

## One-time Setup (30-40 min, phir kabhi nahi chhedna)

### 1. Gemini API key (free)
1. https://aistudio.google.com/apikey par jao
2. "Create API key" click karo, copy karo

### 2. Buffer API setup (free) — 2026 ka NAYA tareeqa
⚠️ Buffer ne 2026 mein apna purana developer-apps system band kar diya hai naye users ke liye.
Ab GraphQL API hai, personal API key ke sath.

1. https://buffer.com par account banao, LinkedIn + Facebook Page + X connect karo (free plan = 3 channels)
2. Buffer app mein **Settings → API** jao
3. **"Create Personal API Key"** dabao → jo key mile, copy kar lo (ye `BUFFER_ACCESS_TOKEN` hai)
4. Apne 3 channels ki ID nikalne ke liye https://developers.buffer.com/explorer.html kholo:
   - Apni API key wahan paste karo (top mein "Enter your API key" field)
   - Ye query chalao:
     ```graphql
     query GetOrgAndChannels {
       account { organizations { id } }
     }
     ```
   - Mile hue `organizations.id` ko copy karo, phir ye query chalao:
     ```graphql
     query GetChannels {
       channels(input: { organizationId: "YAHAN_ORG_ID_DAALO" }) {
         id
         name
         service
       }
     }
     ```
   - Result mein har channel ka `id` + `service` (linkedin/facebook/twitter) dikhega — teeno copy kar lo

**⚠️ Zaroori: Repo PUBLIC hona chahiye.** Buffer ka naya API images ka direct upload nahi leta — sirf
ek **public image URL** accept karta hai. System khud images GitHub repo mein push kar deta hai aur
unka `raw.githubusercontent.com` link Buffer ko deta hai — lekin ye sirf **public repos** ke liye kaam
karta hai. Repo banate waqt "Private" nahi, **"Public"** select karna (koi API key ya secret repo
mein nahi jaati, wo GitHub Secrets mein alag se hoti hain — safe hai public rakhna).

### 3. Weekly Topics Google Doc setup (taake phone se hi weekly data daal sako)
Maine already ye bana diya hai tumhare Drive mein: **"Kreafy Content Agent" folder → "Weekly Topics" doc**
(https://docs.google.com/document/d/162fofOuGsVnnI9SPMkG9rU82-ph5T4mXSjzuZOpx5-4/edit)

GitHub Actions ko is Doc ko padhne ke liye ek "service account" chahiye (Google ka robot-account system):
1. https://console.cloud.google.com par jao → naya project banao (ya koi purana select karo)
2. "APIs & Services" → "Enable APIs" → **Google Drive API** enable karo
3. "Credentials" → "Create Credentials" → **Service Account** banao
4. Us service account ke "Keys" tab mein jaake **JSON key download** karo
5. JSON file khol ke uska `client_email` field copy karo (kuch aisa dikhega: `xyz@project.iam.gserviceaccount.com`)
6. **"Weekly Topics" Google Doc khol ke Share karo** us email ke sath (Viewer access kaafi hai)
7. Poori JSON file ka content copy karke rakh lo, agle step (Secrets) mein use hoga

Agar ye step skip karna ho (thoda technical hai), koi baat nahi - system automatically `manual_topics.txt`
(GitHub repo wali file) fallback ki tarah use kar lega. Doc wala route sirf **phone se easily edit karne ke liye** hai.

### 4. GitHub repo mein Secrets daalo
Repo → Settings → Secrets and variables → Actions → "New repository secret":

| Secret Name | Value |
|---|---|
| `GEMINI_API_KEY` | Step 1 se |
| `ANTHROPIC_API_KEY` | (optional - backup ke liye, Claude Code console se) |
| `BUFFER_ACCESS_TOKEN` | Step 2 se |
| `BUFFER_LINKEDIN_ID` | Step 2 se |
| `BUFFER_FACEBOOK_ID` | Step 2 se |
| `BUFFER_TWITTER_ID` | Step 2 se |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | (optional - Step 3 se, Weekly Topics Doc ke liye) |

### 5. Buffer mein posting times set karo (ek baar ka kaam)
Buffer app → har channel (LinkedIn/FB/X) → Posting Schedule → 5 time-slots add karo (Pakistan Time):
**11:00 AM, 1:00 PM, 4:00 PM, 7:00 PM, 9:30 PM** — ye multi-region (US/UK/ME + Pakistan) audience ke
liye best-overlap times hain. Ek baar set karne ke baad system roz khud isi schedule pe post karega.

### 6. Repo push karo GitHub pe
```bash
cd kreafy-content-agent
git init
git add .
git commit -m "Kreafy Content Agent - initial setup"
git remote add origin https://github.com/nazakataleofficial-coder/kreafy-content-agent.git
git push -u origin main
```

---

## Roz kya automatic hai, hafte mein kya manual hai

| Kaam | Frequency | Kaun karta hai |
|---|---|---|
| Google Trends se topics | Roz | Khud automatic |
| Content likhna (5 posts, 2 languages) | Roz | Khud automatic (Gemini/Claude) |
| Character illustration banana | Roz | Khud automatic (Gemini) |
| Carousel images banana | Roz | Khud automatic (Puppeteer) |
| Buffer mein queue karna | Roz | Khud automatic |
| Buffer se actual post publish hona | Set kiye gaye 5 times pe | Buffer khud (Step 5 wale times) |
| **Reddit se real stories dhoondna** | **Hafte mein ek baar (15-20 min)** | **Ale manually karta hai** |

**Weekly kaam kaise karna hai:** Hafte mein ek baar 4-5 subreddits (webdev, Entrepreneur, SaaS, NewTubers, animation) browse karo, jo bhi genuinely relatable real story/pain-point mile usko ek line mein `manual_topics.txt` file mein paste kar do. Baaki sab khud automatic ho jayega - ye Reddit ki policy ke mutabiq zaroori hai (automated Reddit scraping AI-content ke liye allowed nahi), lekin ye sirf 15-20 min/week ka kaam hai, roz nahi.

Agar `manual_topics.txt` khali ho, system phir bhi chalega - sirf Google Trends ke topics use karega (thoda generic hoga, lekin rukega nahi).

## Character (mascot) ke baare mein
`config/config.py` mein `CHARACTER_DESIGN` permanently locked hai (Disney/Pixar-style, curly hair,
warm smile - jo reference images se decide kiya gaya). Ye kabhi nahi badalta - roz sirf uski
pose/expression story ke hisab se badalti hai (Gemini "illustration_prompt_en" field se). Agar
character ka look kabhi badalna ho, sirf ye ek jagah (`CHARACTER_DESIGN`) edit karni hai.

## Poora daily flow (recap)
1. Google Trends + `manual_topics.txt` se topics collect
2. AI 5 posts likhta hai (EN + UR, dono languages) + har post ki illustration-pose describe karta hai
3. Gemini us pose ka real illustration banata hai (fixed character ke sath)
4. Puppeteer har post ki 4-slide carousel (EN + UR alag) banata hai, illustration hook slide pe lagti hai
5. Buffer ki queue mein daal diya jata hai
6. Buffer apne set-kiye-hue 5 daily times pe khud publish kar deta hai

## Manually test karna ho (setup ke turant baad)
Repo → Actions tab → "Kreafy Daily Content Agent" → "Run workflow" button — turant chala ke dekh sakte ho sab theek chal raha hai ya nahi.

## Agar kal ko sell/scale karna ho
Saari settings `config/config.py` mein environment variables se aati hain — koi hardcoded key nahi. Naye client ke liye bas naye secrets daalo, code same rahega.
