# 🦉 NeVedis
### Don't fall for it. Check before you pay.

Paste a weird text, email or call transcript, or drop a screenshot or voicemail, and NeVedis tells you in plain words whether it's a scam, how the trick works, and exactly what to do.

Built for families and grandparents: one box, one button, no jargon.

## What makes it different from "just ask a chatbot"

| Feature | What it does |
|---|---|
| 🔬 **Link X-ray** | Checked by code, not guessed: *"Looks like USPS → really goes to com-redelivery.info"*. Catches look-alike spellings (`paypa1`, `ezpas`), hidden punycode letters, and link shorteners. |
| 🧠 **Their game plan** | Names the scam family and shows the scammer's script step by step: *"📍 You are here · ⚠️ Next, if you reply"*, plus their predicted next move. |
| 🆘 **"Uh-oh, I already…"** | Tap *clicked the link · shared info · gave card details · sent money (gift card / wire / Zelle / crypto…) · read a code · installed an app* for exact emergency steps. |
| 📣 **Report it** | The right place for each scam: forward to 7726, spam@uspis.gov, ReportFraud.ftc.gov, the FBI's IC3, TIGTA, USCIS, the Elder Fraud Hotline… |
| 💬 **Warn your family** | A ready-to-send warning for the family group chat. |
| 🎮 **Spot the Scam** | A game with 40 real-world messages (28 scams and 12 real ones), streaks and confetti. Trains your scam radar. |
| 📚 **Field guide** | 28 scam families across 9 areas of life, searchable. |

**Scam families covered:** package delivery, unpaid tolls, fake bank fraud alerts, "read me the code", locked-account phishing, fake checks, IRS, Social Security, immigration/USCIS, jury duty and warrants, Medicare, student loan forgiveness, family emergency / "Mom, new number", romance, sextortion, job/task scams, crypto investment (pig butchering), wrong-number texts, Marketplace tricks, fake stores, fake rentals, fake virus pop-ups, fake invoices, utility shut-offs, QR codes, insurance-quote spam, prizes and lotteries, fake charities.

## How it works

```
message / screenshot / audio
   │
   ├─ rules.py      instant checks (English keywords): links, look-alikes, punycode, gift card/crypto/wire/Zelle,
   │                urgency, code/password requests, remote-access apps, email headers (From vs Reply-To, SPF/DKIM/DMARC)
   │                → rule_score 0-100 + hard/soft signals
   │
   ├─ analyzer.py   Gemini (JSON + schema): 3P test (pretext · pressure · payoff ask), category, scam family,
   │                quoted red flags, next move, family warning. Retries once, 60 s cap, rules-only fallback.
   │
   └─ final score   0.6 × AI + 0.4 × rules (AI alone for screenshot/audio-only, or when the rules find nothing)
                    any hard red flag → at least 80 · 70-100 high · 40-69 medium · 0-39 low
```

- `scams.py`: the scam library, report places, emergency steps, and the game cards (one source of truth).
- `server.py`: a small FastAPI server. `static/` holds the web page.
- Safety: user text is never treated as instructions. `<item>` fences are neutralized, uploaded files are checked by their content, not their name, and the app never calls anything "safe".

## Run it

Requires Python 3.11+ and a free Gemini API key from https://aistudio.google.com/apikey.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env          # then paste your key after GEMINI_API_KEY=
.venv/bin/python test.py      # checks that the key works
.venv/bin/python server.py    # open http://127.0.0.1:8501
```

Change the model in `config.py` (one line).

**Free Gemini plan limits:** Google's free plan allows about 20 checks per day per model. NeVedis automatically falls back to the backup models listed in `config.py` when one runs out or is busy. If every model is unavailable, NeVedis says **"Couldn't check this yet"** instead of guessing. It only gives a rules-only verdict when the instant checks find real red flags. For heavier use, turn on billing for your key in Google AI Studio.

## Put it online (Vercel)

NeVedis deploys to Vercel with no code changes. Vercel finds the FastAPI `app` in `server.py` and serves `static/` from its CDN.

1. Push this repository to GitHub.
2. On [vercel.com](https://vercel.com), choose **Add New → Project** and import the repository. Vercel detects FastAPI on its own.
3. Under **Environment Variables**, add `GEMINI_API_KEY` with your key. Never commit the key.
4. Click **Deploy**. Every later push to `main` redeploys automatically.

Built for the web host:
- Screenshots are shrunk in the browser before upload. Recordings must be under 4 MB (Vercel accepts 4.5 MB per request).
- **Fair use:** each visitor gets 8 checks per 10 minutes and 40 per day, so nobody can drain the shared Gemini quota. This is counted per server instance, which is good enough for a free demo. Use the Vercel Firewall for stricter limits.
- `vercel.json` caps each check at 90 seconds.

## Privacy

Messages and files you check are sent to Google Gemini to be analyzed. Nothing is stored by NeVedis. The game and the field guide work fully offline.

*NeVedis gives advice, not a guarantee. When in doubt, call the company or agency using the number on its official website, your card, or your bill. All example messages are fictional (555 phone numbers, made-up names and domains).*
