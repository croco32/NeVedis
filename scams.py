"""NeVedis scam library: one source of truth for scam families, reporting places, emergency
steps, and the "Spot the Scam" game. All example messages are fictional (555 numbers etc.).

Report links were checked to resolve (Nov 2026). Phone numbers are the official public lines.
"""

FIELDS = [
    {"id": "delivery", "name": "Packages & tolls", "emoji": "📦"},
    {"id": "money", "name": "Banks & accounts", "emoji": "🏦"},
    {"id": "gov", "name": "Government & police", "emoji": "🏛️"},
    {"id": "family", "name": "Family & love", "emoji": "💞"},
    {"id": "earn", "name": "Jobs & 'easy money'", "emoji": "💸"},
    {"id": "shop", "name": "Buying & selling", "emoji": "🛍️"},
    {"id": "tech", "name": "Tech & subscriptions", "emoji": "💻"},
    {"id": "home", "name": "Home & bills", "emoji": "💡"},
    {"id": "luck", "name": "Prizes & giving", "emoji": "🎁"},
]

# Where to report. kind: link | email | sms | action (no link, just do it)
REPORTS = {
    "ftc": {"label": "Report to the FTC", "kind": "link", "target": "https://reportfraud.ftc.gov", "note": "The main U.S. scam report. Takes 5 minutes."},
    "spam_text": {"label": "Forward the text to 7726", "kind": "sms", "target": "7726", "note": "7726 spells SPAM. Your phone company blocks the sender. Free."},
    "ic3": {"label": "Report to the FBI (IC3)", "kind": "link", "target": "https://www.ic3.gov", "note": "For online, crypto, romance and investment scams. Report fast if money was sent."},
    "uspis": {"label": "Email USPS inspectors", "kind": "email", "target": "spam@uspis.gov", "note": "Forward fake USPS texts (as a screenshot) or emails."},
    "tigta": {"label": "Report IRS impersonation", "kind": "link", "target": "https://www.tigta.gov", "note": "The office that investigates fake IRS calls."},
    "irs_phishing": {"label": "Forward to phishing@irs.gov", "kind": "email", "target": "phishing@irs.gov", "note": "For fake IRS emails. Forward, don't reply."},
    "ssa_oig": {"label": "Report fake Social Security calls", "kind": "link", "target": "https://oig.ssa.gov", "note": "Social Security's inspector general."},
    "uscis": {"label": "Report immigration scams", "kind": "link", "target": "https://www.uscis.gov/report-fraud", "note": "USCIS never asks for payment by phone, gift card or Zelle."},
    "medicare": {"label": "Call 1-800-MEDICARE", "kind": "action", "target": "1-800-633-4227", "note": "The official Medicare line."},
    "elder": {"label": "Elder Fraud Hotline", "kind": "action", "target": "1-833-372-8311", "note": "Free U.S. Justice Department help for people 60+ (1-833-FRAUD-11)."},
    "identity": {"label": "IdentityTheft.gov", "kind": "link", "target": "https://www.identitytheft.gov", "note": "Gives you a step-by-step recovery plan."},
    "amazon": {"label": "Report to Amazon", "kind": "link", "target": "https://www.amazon.com/reportascam", "note": "For fake Amazon calls, texts and emails."},
    "microsoft": {"label": "Report to Microsoft", "kind": "link", "target": "https://www.microsoft.com/reportascam", "note": "For fake Microsoft / Windows support."},
    "apple": {"label": "Email Apple", "kind": "email", "target": "reportphishing@apple.com", "note": "For fake Apple ID and iCloud messages."},
    "bank": {"label": "Call your bank", "kind": "action", "target": "the number on the back of your card", "note": "Never use a number from the message."},
    "platform": {"label": "Report the profile in the app", "kind": "action", "target": "Use the app's Report button", "note": "Facebook, Instagram, WhatsApp, dating apps and marketplaces all have one."},
    "takeitdown": {"label": "Take It Down (under 18)", "kind": "link", "target": "https://takeitdown.ncmec.org", "note": "Free help removing private photos of minors."},
    "studentaid": {"label": "Check at StudentAid.gov", "kind": "link", "target": "https://studentaid.gov", "note": "Real federal loan help is always free."},
    "local": {"label": "Call the real office", "kind": "action", "target": "the number on its official website", "note": "Courts, police and utilities never collect fines by phone or gift card."},
}

FAMILIES = [
    # ---------- Packages & tolls ----------
    {"id": "package_delivery", "field": "delivery", "emoji": "📦", "name": "Fake package delivery",
     "hook": "A text says your package is stuck and needs a small fee or a new address.",
     "steps": ["A text says your package is on hold", "You tap a link to a copy of the delivery website", "You 'pay' $1.99 with your card", "They drain your card and sell your details"],
     "tell": "Delivery companies don't text you a link to pay a fee.", "never": "Never tap delivery links. Type the official website yourself.",
     "report": ["uspis", "spam_text", "ftc"], "keywords": r"package|parcel|redeliver|shipment|tracking|usps|fedex|\bups\b|dhl|delivery",
     "example": {"channel": "sms", "from": "+1 (205) 555-0119", "text": "USPS: Your package US9514901185421 is on hold due to an incomplete address. Update your details within 24 hours or it will be returned to sender: https://usps.com-redelivery.info/track\nReply Y, then reopen this message to activate the link.",
                 "flags": [["https://usps.com-redelivery.info/track", "Not usps.com. The real domain is com-redelivery.info."], ["within 24 hours", "A fake deadline to rush you."], ["Reply Y, then reopen", "A trick to make the link clickable."]]}},
    {"id": "toll_road", "field": "delivery", "emoji": "🛣️", "name": "Unpaid toll text",
     "hook": "A text claims you owe a few dollars in tolls, plus a big late fee if you don't pay today.",
     "steps": ["A text says you owe a small toll", "It threatens a $50 fee or a license suspension", "The link asks for your card", "Your card gets charged much more"],
     "tell": "Toll agencies mail invoices or use your account. They don't text payment links with hour-long deadlines.", "never": "Pay tolls only in the official toll app or the website on your bill.",
     "report": ["ic3", "spam_text", "ftc"], "keywords": r"toll|e-?zpass|sunpass|fastrak|i-?pass|peach pass|txtag",
     "example": {"channel": "sms", "from": "+44 7700 900461", "text": "E-ZPass Notice: You have an unpaid toll balance of $6.89. To avoid a $50.00 late fee and license suspension, pay within 12 hours: https://ezpass-tollpay.top/pay",
                 "flags": [["+44 7700 900461", "A foreign number for a U.S. toll."], ["license suspension", "A scary threat over $6."], ["ezpass-tollpay.top", "Not the real E-ZPass website."]]}},
    # ---------- Banks & accounts ----------
    {"id": "bank_impersonation", "field": "money", "emoji": "🏦", "name": "Fake bank fraud alert",
     "hook": "A 'fraud alert' text asks if you made a purchase. Answer, and a fake bank agent calls.",
     "steps": ["A text asks: did you spend $750?", "You reply NO, and a 'fraud specialist' calls", "They say your account is hacked", "They make you move money to a 'protected' account or read a code"],
     "tell": "Your bank will never ask you to move money to protect it, or to send a Zelle to yourself.", "never": "Hang up and call the number on the back of your card.",
     "report": ["bank", "ftc"], "keywords": r"bank|fraud (department|alert|specialist)|zelle|account (locked|suspended)|card ending|debit|chase|wells fargo|bank of america|bofa|citi",
     "example": {"channel": "sms", "from": "72166", "text": "BofA ALERT: Did you attempt a Zelle payment of $750.00 to MARK DAVIS? Reply YES or NO. If NO, a fraud specialist will call you shortly to secure your account.",
                 "flags": [["Reply YES or NO", "Replying tells them your number is real and gets you a scam call."], ["a fraud specialist will call you", "The 'specialist' is the scammer."]]}},
    {"id": "verification_code", "field": "money", "emoji": "🔢", "name": "'Read me the code' trick",
     "hook": "A stranger, buyer or 'support agent' asks you to read back a code you were just texted.",
     "steps": ["Someone says they need to 'verify' you", "A code arrives by text", "They ask you to read it back", "They use it to take your account or phone number"],
     "tell": "That code is a key to your account. Anyone asking for it is breaking in.", "never": "Never share a code, with anyone, ever.",
     "report": ["ftc", "platform"], "keywords": r"\bcode\b|verify (you|that)|google voice|6-?digit|one-?time",
     "example": {"channel": "messenger", "from": "Marketplace buyer 'Kelly R.'", "text": "Hi! Is the couch still available? Before I come I need to make sure you're not a scammer lol 😅 I'm sending you a code from Google, just text it back to me 🙏",
                 "flags": [["make sure you're not a scammer", "They flip it around to look careful."], ["just text it back to me", "This code would let them make a phone number in your name."]]}},
    {"id": "account_phishing", "field": "money", "emoji": "🔐", "name": "'Account locked' sign-in trap",
     "hook": "An email or text says your Apple, Netflix, Microsoft or email account is locked or a payment failed.",
     "steps": ["A message says your account has a problem", "The link goes to a perfect copy of the login page", "You type your password", "They log in as you and lock you out"],
     "tell": "The link's real website is not the company's website.", "never": "Open the official app or type the website yourself.",
     "report": ["apple", "microsoft", "ftc"], "keywords": r"sign-?in|password|account (locked|suspended|disabled)|payment (declined|failed)|apple id|icloud|netflix|microsoft|outlook|verify your account",
     "example": {"channel": "email", "from": "Netflix <billing@netfIix-support.com>", "text": "Hi,\nYour payment was declined and your membership will be suspended within 48 hours.\nUpdate your billing details now: http://netflix-billing-update.com/login\nThe Netflix Team",
                 "flags": [["netfIix-support.com", "That's a capital I, not an L. A look-alike sender."], ["netflix-billing-update.com", "Not netflix.com."]]}},
    {"id": "fake_check", "field": "money", "emoji": "💵", "name": "Fake check / overpayment",
     "hook": "Someone sends you a check for MORE than they owe and asks you to send back the difference.",
     "steps": ["A buyer or 'employer' mails you a big check", "They say it was too much, by mistake", "You send the extra back by Zelle or gift card", "Days later the check bounces and you lose it all"],
     "tell": "A bank 'clearing' a check doesn't mean it's real. Fake checks bounce weeks later.", "never": "Never send money back from a check someone gave you.",
     "report": ["ftc", "bank"], "keywords": r"check|cheque|overpa|mystery shopper|send (back|the difference)|refund the extra",
     "example": {"channel": "email", "from": "Secret Shopper Program <hr@shopper-eval.example>", "text": "Congratulations! You were selected as a Mystery Shopper. A check for $2,450 is in the mail. Deposit it, keep $350 as your pay, and use the rest to buy Target gift cards to evaluate the store. Send us photos of the card numbers.",
                 "flags": [["keep $350 as your pay", "Real jobs don't pay you before work."], ["buy Target gift cards", "The check will bounce. The gift cards are your money."]]}},
    # ---------- Government & police ----------
    {"id": "government_irs", "field": "gov", "emoji": "🏛️", "name": "IRS tax threat",
     "hook": "A call or message says you owe taxes and will be arrested today unless you pay.",
     "steps": ["An 'officer' says you owe back taxes", "They threaten arrest or deportation today", "They demand gift cards, a wire or crypto", "They tell you not to tell anyone"],
     "tell": "The IRS sends letters by mail first and never takes gift cards.", "never": "Hang up. Check what you owe only at irs.gov.",
     "report": ["tigta", "irs_phishing", "ftc"], "keywords": r"\birs\b|internal revenue|tax(es)? (owed|due)|back taxes|treasury",
     "example": {"channel": "phone_call", "from": "Caller ID: 'IRS Washington DC'", "text": "Caller said: \"This is Officer Daniel Brooks from the Internal Revenue Service, badge 4471. You owe $4,850 in unpaid taxes. A warrant for your arrest will be issued TODAY unless you pay. Buy Apple gift cards for the full amount and call me back at (202) 555-0147 with the card numbers within 2 hours. Do not tell anyone about this case.\"",
                 "flags": [["warrant for your arrest will be issued TODAY", "The IRS doesn't arrest people by phone."], ["Buy Apple gift cards", "No government takes gift cards. Ever."], ["Do not tell anyone", "Secrecy protects the scammer, not you."]]}},
    {"id": "government_ssa", "field": "gov", "emoji": "🪪", "name": "Social Security 'suspended'",
     "hook": "A call says your Social Security number is 'suspended' because of crime.",
     "steps": ["A recording says your SSN is suspended", "A fake agent says it was used in a crime", "They ask to 'verify' your number", "They make you 'protect' your money by moving it"],
     "tell": "Social Security numbers can't be suspended.", "never": "Social Security won't threaten you or ask for payment by phone.",
     "report": ["ssa_oig", "ftc"], "keywords": r"social security|\bssn\b|\bssa\b|suspended",
     "example": {"channel": "voicemail", "from": "+1 (800) 555-0102", "text": "Voicemail: \"This is an urgent message from the Social Security Administration. Your Social Security number has been suspended due to suspicious activity in Texas. Press 1 now to speak with an officer, or a legal case will be filed against you.\"",
                 "flags": [["Social Security number has been suspended", "That isn't a real thing."], ["a legal case will be filed against you", "A threat to make you panic."]]}},
    {"id": "immigration", "field": "gov", "emoji": "🛂", "name": "Immigration / visa threat",
     "hook": "Someone posing as USCIS or ICE says there's a problem with your papers and you must pay a fine now.",
     "steps": ["A caller knows your name and country", "They say your visa or green card has an error", "They threaten deportation", "They demand a 'fee' by Zelle, gift card or crypto"],
     "tell": "USCIS never asks for payment by phone, gift card, Zelle or crypto.", "never": "Check your case only at uscis.gov or with a licensed lawyer.",
     "report": ["uscis", "ftc"], "keywords": r"uscis|\bice\b|immigration|visa|green card|deport|citizenship|asylum|work permit",
     "example": {"channel": "phone_call", "from": "Caller ID: 'USCIS'", "text": "Caller said: \"This is Agent Ramirez from U.S. Citizenship and Immigration Services. There is an error in your green card application. To avoid deportation you must pay a $1,200 correction fee today by Zelle. Stay on the line and do not contact a lawyer.\"",
                 "flags": [["pay a $1,200 correction fee today by Zelle", "USCIS fees are never paid by Zelle."], ["do not contact a lawyer", "A real agency never says that."]]}},
    {"id": "jury_duty", "field": "gov", "emoji": "👮", "name": "Missed jury duty / police warrant",
     "hook": "A 'deputy' says you missed jury duty or have a warrant, and must pay a fine to avoid jail.",
     "steps": ["A 'sheriff's deputy' calls with real-sounding names", "They say you missed jury duty", "They demand a fine now to cancel the warrant", "They send you to a payment kiosk or gift cards"],
     "tell": "Courts send missed-jury notices by mail. Police don't collect fines by phone.", "never": "Call the court's clerk using the number on the court's official website.",
     "report": ["local", "ftc"], "keywords": r"jury|sheriff|deputy|warrant|court|bail|police",
     "example": {"channel": "phone_call", "from": "+1 (312) 555-0164", "text": "Caller said: \"This is Lieutenant Harris with the County Sheriff's Office. You failed to appear for jury duty and a bench warrant was issued. You can clear it today with a $1,500 bond paid at a Bitcoin kiosk, or deputies will come to your home tonight.\"",
                 "flags": [["Bitcoin kiosk", "No court takes Bitcoin."], ["deputies will come to your home tonight", "A threat to rush you."]]}},
    {"id": "medicare", "field": "gov", "emoji": "🩺", "name": "Medicare / health benefits",
     "hook": "A call offers a 'new Medicare card', free equipment or extra benefits if you confirm your number.",
     "steps": ["A caller offers a new card or free gear", "They ask you to 'confirm' your Medicare number", "They bill Medicare for things you never got", "Your benefits can get used up"],
     "tell": "Medicare won't call to sell you anything or ask for your number.", "never": "Treat your Medicare number like a credit card.",
     "report": ["medicare", "ftc"], "keywords": r"medicare|medicaid|health (plan|benefit)|knee brace|back brace|genetic test|otc card|grocery allowance",
     "example": {"channel": "phone_call", "from": "+1 (877) 555-0133", "text": "Caller said: \"Hi, I'm calling from Medicare about your new plastic Medicare card and a $900 grocery allowance you qualify for. I just need you to read me your Medicare number to activate it.\"",
                 "flags": [["read me your Medicare number", "Medicare already has it. Scammers don't."], ["$900 grocery allowance", "A bait reward."]]}},
    {"id": "student_loan", "field": "gov", "emoji": "🎓", "name": "Student loan forgiveness",
     "hook": "A message says you qualify for full loan forgiveness. You just pay a fee and share your login.",
     "steps": ["A text says your loans can be erased", "They ask for an upfront 'processing fee'", "They ask for your FSA ID login", "They change your contact info and take payments"],
     "tell": "Real federal loan help is free, at StudentAid.gov.", "never": "Never pay for loan forgiveness or share your FSA ID.",
     "report": ["studentaid", "ftc"], "keywords": r"student loan|forgiveness|fsa id|loan discharge|biden|navient|nelnet|mohela",
     "example": {"channel": "sms", "from": "+1 (415) 555-0178", "text": "FINAL NOTICE: You are pre-approved for 100% Student Loan Forgiveness under the new federal program. Enrollment closes Friday. Call (855) 555-0191 with your FSA ID ready. One-time processing fee $499.",
                 "flags": [["processing fee $499", "Federal forgiveness has no fee."], ["with your FSA ID ready", "That's the password to your loan account."]]}},
    # ---------- Family & love ----------
    {"id": "relative_emergency", "field": "family", "emoji": "👵", "name": "Family emergency / 'new number'",
     "hook": "A 'grandchild' or 'son/daughter' is in trouble or has a new number, and needs money fast.",
     "steps": ["A message or call: 'Mom, it's me, new number'", "There's an emergency: jail, an accident, a bill", "They beg you not to tell anyone", "They ask for a wire, Zelle, gift cards or a cash courier"],
     "tell": "Voices can be faked with AI now. A new number plus an urgent money ask is the classic sign.", "never": "Hang up and call them on the number you already know. Agree on a family code word.",
     "report": ["elder", "ftc"], "keywords": r"\bmom\b|\bdad\b|grandma|grandpa|new number|broke my phone|bail|jail|accident|it'?s me",
     "example": {"channel": "messenger", "from": "Unknown number +1 (646) 555-0127", "text": "Hi Mom, I dropped my phone in the toilet 😭 this is my new number. Can you help me pay a bill today? I'll pay you back tomorrow, I can't call right now, my mic is broken",
                 "flags": [["this is my new number", "Check by calling their old number."], ["I can't call right now", "They avoid calls so you can't hear it's not them."]]}},
    {"id": "romance", "field": "family", "emoji": "💘", "name": "Online romance",
     "hook": "A sweet person you met online never video-calls, and soon needs money for an emergency or a trip to you.",
     "steps": ["Kind messages every day for weeks", "They can't video call (always an excuse)", "Then a crisis: customs fee, hospital, plane ticket", "They ask for gift cards, crypto or wire"],
     "tell": "Someone you've never met in person asking for money is a scam, every time.", "never": "Never send money to someone you only know online.",
     "report": ["ic3", "platform", "ftc"], "keywords": r"my love|darling|sweetheart|honey|oil rig|deploy|customs|plane ticket|military|in your arms|dating",
     "example": {"channel": "messenger", "from": "'Capt. James Walker' (dating app match)", "text": "My love, I can't stop thinking about you ❤️ I finally got leave from my deployment, but they won't release me until I pay a $2,800 fee. I can't use my bank from here. Could you send it in Bitcoin? I'll pay you back the day I land in your arms.",
                 "flags": [["pay a $2,800 fee", "Real soldiers don't pay to get leave."], ["send it in Bitcoin", "Crypto can't be recovered."]]}},
    {"id": "sextortion", "field": "family", "emoji": "🫣", "name": "'I recorded you' threat",
     "hook": "An email or chat says they have embarrassing photos or video and will share them unless you pay.",
     "steps": ["A scary message claims they hacked your camera, or got photos", "They show an old leaked password to seem real", "They demand crypto within 48 hours", "Paying only brings more demands"],
     "tell": "Most of these emails are bluffs sent to millions. They usually have nothing.", "never": "Don't pay and don't reply. Save the message and report it.",
     "report": ["ic3", "takeitdown", "platform"], "keywords": r"recorded you|webcam|video of you|your contacts|bitcoin|private (photos|pictures)|embarrass",
     "example": {"channel": "email", "from": "Anonymous <noreply@protonmail.example>", "text": "I know your password is Summer2019. I hacked your device and recorded you through your webcam. Send $1,200 in Bitcoin to the wallet below within 48 hours or I will send the video to all your contacts.",
                 "flags": [["Summer2019", "An old password from a data leak, not proof of hacking."], ["within 48 hours", "Pressure. These emails go to millions of people."]]}},
    # ---------- Jobs & easy money ----------
    {"id": "job_task", "field": "earn", "emoji": "💼", "name": "Easy job / 'task' scam",
     "hook": "A recruiter offers good pay for easy online tasks like liking videos or rating products.",
     "steps": ["A 'recruiter' texts about remote work", "You earn a few real dollars at first", "Then you must 'top up' to unlock bigger tasks", "Your money vanishes"],
     "tell": "Real jobs never make you pay to work.", "never": "If a job asks you to pay or deposit crypto, walk away.",
     "report": ["ftc", "platform"], "keywords": r"remote|part-?time|recruit|hiring|\$\d+.{0,10}(per|a) day|tasks?|like (videos|posts)|rate products|commission",
     "example": {"channel": "messenger", "from": "WhatsApp: 'Emily | Talent Team'", "text": "Hello! I'm Emily from a recruitment agency. We have a flexible part-time job: like YouTube videos and rate products from home and earn $200–$500 per day. No experience needed. Can I tell you more? 😊",
                 "flags": [["earn $200–$500 per day", "Too much pay for too little work."], ["like YouTube videos", "The classic 'task scam' opening."]]}},
    {"id": "investment_crypto", "field": "earn", "emoji": "📈", "name": "Crypto 'investment' / pig butchering",
     "hook": "A friendly contact or 'mentor' shows big crypto profits and an app where your money 'grows'.",
     "steps": ["A new online friend talks about investing", "The app shows your money growing fast", "To withdraw, you must pay 'taxes' or fees", "The app disappears with everything"],
     "tell": "Guaranteed high returns don't exist. Neither do fees to withdraw your own money.", "never": "Only invest through a regulated broker you found yourself.",
     "report": ["ic3", "ftc"], "keywords": r"crypto|bitcoin|usdt|invest|trading|returns?|profit|mentor|platform|withdraw",
     "example": {"channel": "messenger", "from": "Telegram: 'Linda W.'", "text": "My uncle is a financial analyst and he showed me this crypto trading platform. I made $38,000 last month 🤑 Returns are guaranteed 30% per week. Let me help you open an account, start with just $1,000!",
                 "flags": [["Returns are guaranteed 30% per week", "No real investment guarantees that."], ["start with just $1,000", "First the small 'test', then much more."]]}},
    {"id": "wrong_number", "field": "earn", "emoji": "👋", "name": "Wrong-number 'hello'",
     "hook": "A friendly 'wrong number' text that turns into a friendship, then into a money pitch.",
     "steps": ["'Hi, is this Anna? Still on for dinner?'", "You say wrong number, and they're charming about it", "Weeks of friendly chat", "Then an investment or a crisis"],
     "tell": "The 'mistake' is on purpose. It's the opening line of a long scam.", "never": "Don't reply to wrong-number texts from strangers. Just block.",
     "report": ["spam_text", "ftc"], "keywords": r"is this .{2,15}\?|wrong number|still on for|we met at|nice to meet you",
     "example": {"channel": "sms", "from": "+1 (929) 555-0158", "text": "Hi David, it's Jessica! Are we still on for golf this Saturday at 10? 🏌️‍♀️",
                 "flags": [["Hi David", "You're not David, and that's the plan."], ["still on for golf", "An innocent start to get you chatting."]]}},
    # ---------- Buying & selling ----------
    {"id": "marketplace", "field": "shop", "emoji": "🛋️", "name": "Marketplace buyer/seller tricks",
     "hook": "A buyer 'already paid' but needs you to upgrade your Zelle, or a seller wants a deposit first.",
     "steps": ["A quick, eager buyer or seller", "They push for Zelle or a shipping link", "A fake 'payment pending' email says you must pay to receive", "You pay; the item or money never comes"],
     "tell": "Zelle has no 'business upgrade' you pay for. Payment emails come from fakes.", "never": "Meet in person, pay or get paid in person or with the platform's protected checkout.",
     "report": ["platform", "ftc"], "keywords": r"marketplace|craigslist|offerup|still available|business account|upgraded? to business|zelle support|courier|shipping label|i'?ll take it|full price|pick ?up",
     "example": {"channel": "messenger", "from": "Facebook Marketplace: 'Jake M.'", "text": "I'll take it for full price! I sent $650 by Zelle but it says your account must be upgraded to Business to receive it. Just send $300 to upgrade and Zelle refunds it with my payment. Check your email from Zelle Support 🙏",
                 "flags": [["upgraded to Business", "Zelle has no paid 'business upgrade'."], ["Just send $300", "That's the real goal: your money."]]}},
    {"id": "fake_store", "field": "shop", "emoji": "🛍️", "name": "Too-good-to-be-true store",
     "hook": "An ad or text shows famous brands at 80% off, 'today only, closing sale'.",
     "steps": ["A social media ad with huge discounts", "A brand-new website with a countdown", "You pay; nothing arrives, or a cheap fake", "Your card is reused"],
     "tell": "Brand-new websites with giant discounts and countdown timers are the classic fake store.", "never": "Buy from stores you know. Search the store name + 'scam' first.",
     "report": ["ftc"], "keywords": r"\d{2}% off|clearance|closing (sale|down)|today only|only \d+ left|outlet|free gift",
     "example": {"channel": "social_media", "from": "Sponsored ad", "text": "🔥 CLOSING SALE: Brand-new Dyson Airwrap only $49 today! 90% off, just 7 left. Free shipping 👉 dyson-outlet-store.shop",
                 "flags": [["$49", "A $600 product for $49 is fake or never ships."], ["dyson-outlet-store.shop", "Not dyson.com."]]}},
    {"id": "rental_housing", "field": "shop", "emoji": "🏠", "name": "Fake rental listing",
     "hook": "A great apartment at a low price, but the 'owner' is away and wants a deposit before you see it.",
     "steps": ["A cheap, beautiful listing", "The owner is abroad or 'busy'", "They want a deposit to 'hold' it", "The keys never come. The real owner never knew"],
     "tell": "Never pay to rent a place you haven't seen in person.", "never": "Visit first, and pay by check or card only after signing a real lease.",
     "report": ["platform", "ftc"], "keywords": r"\brent\b|apartment|lease|landlord|deposit|keys|listing|bedroom|/month|per month|show (it|the place)",
     "example": {"channel": "email", "from": "Pastor Mark Ellis <mark.ellis.rentals@gmail.com>", "text": "The 2-bedroom is still available for $850/month. I am on a mission trip overseas so I cannot show it, but if you send the first month and deposit by Zelle today I will mail you the keys.",
                 "flags": [["I cannot show it", "If you can't see it, it may not be his."], ["mail you the keys", "A classic fake landlord line."]]}},
    # ---------- Tech & subscriptions ----------
    {"id": "tech_support", "field": "tech", "emoji": "🖥️", "name": "Fake virus warning",
     "hook": "A loud pop-up says your computer is infected and you must call 'Microsoft' or 'Apple' now.",
     "steps": ["A pop-up freezes your screen with alarms", "You call the number", "They install a remote-control app", "They 'find' problems and take payment or bank access"],
     "tell": "Real virus warnings never show a phone number to call.", "never": "Close the browser (or restart). Never call the number.",
     "report": ["microsoft", "ftc"], "keywords": r"virus|infected|trojan|spyware|windows defender|microsoft support|apple support|do not (shut|turn) (down|off)|anydesk|teamviewer",
     "example": {"channel": "social_media", "from": "Browser pop-up", "text": "⚠️ WINDOWS DEFENDER ALERT ⚠️ Your PC is infected with Trojan Spyware. Your banking passwords are at risk. DO NOT shut down your computer. Call Microsoft Support immediately: 1-888-555-0143",
                 "flags": [["Call Microsoft Support immediately", "Microsoft never puts a phone number in a warning."], ["DO NOT shut down", "Closing it is exactly what you should do."]]}},
    {"id": "fake_invoice", "field": "tech", "emoji": "🧾", "name": "Fake invoice or refund",
     "hook": "An 'invoice' says you were charged $399 for Geek Squad, Norton or PayPal. Call to cancel.",
     "steps": ["A scary invoice for something you never bought", "You call the number to cancel", "They 'refund' you but 'too much'", "They make you send the difference back"],
     "tell": "The goal is to make you call. The phone number is the scam.", "never": "Check charges in your bank app, not by calling numbers in emails.",
     "report": ["ftc", "amazon"], "keywords": r"invoice|renew(al|ed)|subscription|geek squad|norton|mcafee|paypal|refund|charged|order #",
     "example": {"channel": "email", "from": "Geek Squad Billing <service.desk.4471@gmail.com>", "text": "Your Geek Squad Total Protection plan renewed for $399.99 today. If you did not authorize this charge, call our billing team at (888) 555-0182 within 24 hours to cancel and get a refund.",
                 "flags": [["@gmail.com", "Best Buy doesn't send invoices from Gmail."], ["call our billing team", "Calling is the trap."]]}},
    # ---------- Home & bills ----------
    {"id": "utility_shutoff", "field": "home", "emoji": "💡", "name": "Utility shut-off threat",
     "hook": "A call or text says your power or water will be cut off within an hour unless you pay now.",
     "steps": ["'Your power will be disconnected in 30 minutes'", "They demand payment immediately", "They want Cash App, Zelle, gift cards or a Bitcoin ATM", "Your real account was fine all along"],
     "tell": "Utilities send written notices weeks before a shut-off, and never take gift cards or crypto.", "never": "Call the number on your bill or log in to the official app.",
     "report": ["local", "ftc"], "keywords": r"power|electric|gas bill|water|disconnect|shut-?off|utility|comed|pg&e|con ?ed|duke energy",
     "example": {"channel": "sms", "from": "+1 (708) 555-0174", "text": "ComEd: Your electric service will be DISCONNECTED in 30 minutes due to an overdue balance of $286.40. To avoid disconnection pay now via Cash App to $ComEdBilling or call 1-833-555-0109.",
                 "flags": [["DISCONNECTED in 30 minutes", "Real shut-offs come with weeks of notice."], ["pay now via Cash App", "Utilities don't take Cash App."]]}},
    {"id": "qr_code", "field": "home", "emoji": "🅿️", "name": "Fake QR code",
     "hook": "A QR code on a parking meter, flyer, letter or package goes to a fake payment site.",
     "steps": ["A sticker QR code covers the real one", "You scan to pay parking or 'reschedule delivery'", "A copy site takes your card", "Your card is charged again and again"],
     "tell": "Look at the website after scanning. Stickers on meters are a red flag.", "never": "Pay parking in the official city app or by card at the meter.",
     "report": ["local", "ftc"], "keywords": r"qr|scan (the|this)|parking|towed|meter",
     "example": {"channel": "sms", "from": "Parking notice on windshield", "text": "PARKING VIOLATION: Payment required within 2 hours or your vehicle will be towed. Scan the QR code or visit city-parking-pay.com to pay $45.",
                 "flags": [["city-parking-pay.com", "Not your city's .gov website."], ["will be towed", "Fear plus a deadline."]]}},
    {"id": "insurance_quote", "field": "home", "emoji": "🚗", "name": "Insurance quote spam or trap",
     "hook": "After a price comparison, you get flooded with quote emails. Some are real spam, some are traps.",
     "steps": ["You compare insurance prices online", "Your contact info gets sold as a 'lead'", "Real quotes arrive, and so do fakes", "Fakes ask for your SSN or license by email"],
     "tell": "Real insurers don't ask for your SSN by email reply.", "never": "Get quotes only on the insurer's own website or app.",
     "report": ["ftc"], "keywords": r"insurance|quote|premium|coverage|geico|progressive|state farm|allstate|policy",
     "example": {"channel": "email", "from": "\"GEICO Quotes\" <quotes@autoinsure-savings.net>", "text": "From: \"GEICO Quotes\" <quotes@autoinsure-savings.net>\nReply-To: agent.mike.r@gmail.com\nSubject: Your car insurance quote is ready - save $612/year\nAuthentication-Results: mx.example.com; spf=fail smtp.mailfrom=autoinsure-savings.net; dkim=none; dmarc=fail header.from=autoinsure-savings.net\nReceived-SPF: fail (domain of autoinsure-savings.net does not designate 203.0.113.25 as permitted sender)\n\nDear customer,\n\nThanks for comparing car insurance rates! You qualify for our lowest rate of $39/month.\nTo lock in this price, reply with your driver's license number, date of birth and the last 4 of your SSN by tonight. Offer expires at midnight.\n\nTo unsubscribe click here: http://bit.ly/3xQz9Lm",
                 "flags": [["quotes@autoinsure-savings.net", "Says GEICO, but it's not geico.com."], ["spf=fail", "The email failed the sender check."], ["last 4 of your SSN", "Never send this by email."]]}},
    # ---------- Prizes & giving ----------
    {"id": "prize_lottery", "field": "luck", "emoji": "🎰", "name": "'You won!' prize or lottery",
     "hook": "You 'won' a car, cash or a sweepstakes you never entered. You just pay taxes or fees first.",
     "steps": ["Big news: you won!", "To claim it, pay 'taxes' or 'shipping' first", "Pay by gift card or wire", "There is no prize, and they ask again"],
     "tell": "Real prizes never make you pay to collect.", "never": "If you have to pay to win, you didn't win.",
     "report": ["ftc"], "keywords": r"you('ve| have)? won|winner|prize|sweepstakes|lottery|publishers clearing|claim",
     "example": {"channel": "phone_call", "from": "+1 (876) 555-0111", "text": "Caller said: \"Congratulations! This is Publishers Clearing House. You've won $2.5 million and a new Mercedes! To release your prize, you just need to pay $1,850 in taxes today with Walmart gift cards.\"",
                 "flags": [["pay $1,850 in taxes today", "Real winners never prepay taxes to collect."], ["Walmart gift cards", "The gift card is the scam."]]}},
    {"id": "charity", "field": "luck", "emoji": "🤝", "name": "Fake charity / disaster relief",
     "hook": "After a disaster or in the holidays, a 'charity' asks for a fast donation by gift card, crypto or Zelle.",
     "steps": ["A touching story with photos", "Pressure to give right now", "Only cash apps, gift cards or crypto accepted", "Nothing reaches the victims"],
     "tell": "Real charities take checks and cards, and don't rush you.", "never": "Give through the charity's own website you looked up yourself.",
     "report": ["ftc"], "keywords": r"donat|charity|relief|victims|hurricane|wildfire|orphan|church|fundrais",
     "example": {"channel": "messenger", "from": "Facebook: 'Hurricane Relief Fund'", "text": "🙏 Families who lost everything in the hurricane need help TONIGHT. Every $50 feeds a family for a week. Please donate now via Cash App $HurricaneHelpNow or in Bitcoin. Share with everyone!",
                 "flags": [["via Cash App $HurricaneHelpNow", "Real charities don't collect through personal Cash App names."], ["TONIGHT", "Pressure stops you from checking."]]}},
]

# Real-looking legitimate messages for the game. 'why' explains what makes them believable.
LEGIT = [
    {"channel": "sms", "from": "Chase (24273)", "text": "Chase: Your one-time code is 482913. Don't share it with anyone. We'll never call to ask for it.", "why": "You asked for this code, and it tells you not to share it. There's no link and no request."},
    {"channel": "sms", "from": "CVS Pharmacy", "text": "CVS Pharmacy: Your prescription is ready for pickup at 120 Main St. Reply HELP for help, STOP to opt out.", "why": "Just information. No link, no payment, no pressure."},
    {"channel": "sms", "from": "Wells Fargo (93557)", "text": "Wells Fargo: A $52.10 purchase at SHELL was made on card ending 4412. If this wasn't you, call the number on the back of your card.", "why": "It sends you to the number on YOUR card, not a number in the message."},
    {"channel": "email", "from": "Amazon.com <shipment-tracking@amazon.com>", "text": "Your order #112-4431982-5512 has shipped and arrives Thursday. Track your package: https://www.amazon.com/progress-tracker/package", "why": "Real amazon.com sender and link, an order you placed, and no request for anything."},
    {"channel": "sms", "from": "Lincoln Elementary", "text": "Lincoln Elementary: Early dismissal today at 1:30 pm due to weather. Buses will run on the early schedule.", "why": "Information only. Nothing to pay, click or share."},
    {"channel": "email", "from": "Google <no-reply@accounts.google.com>", "text": "New sign-in to your Google Account on a Mac. If this was you, you don't need to do anything. If not, we'll help you secure your account in your Google Account settings.", "why": "Real google.com sender, no link to type a password, and 'you don't need to do anything'."},
    {"channel": "sms", "from": "Delta (33582)", "text": "Delta: Flight DL1423 to ATL is now boarding at gate B12. Have a great flight!", "why": "An update for a trip you booked. No link, no money."},
    {"channel": "sms", "from": "Dr. Patel Dental", "text": "Reminder: Your cleaning with Dr. Patel is Tue Nov 18 at 9:00 AM. Reply C to confirm or call our office to reschedule.", "why": "From an office you know, about an appointment you made. Nothing risky to do."},
    {"channel": "email", "from": "ComEd <billing@comed.com>", "text": "Your ComEd bill of $84.21 is ready and due Nov 20. View or pay in the ComEd app or at comed.com.", "why": "The real comed.com sender, a normal due date weeks away, and it points you to the official app."},
    {"channel": "messenger", "from": "Sara (saved contact)", "text": "Hey! Are we still on for coffee Thursday at 10? ☕", "why": "From a saved contact you already know, about plans you made. No money ask."},
    {"channel": "sms", "from": "USPS (28777)", "text": "USPS: Your item was delivered in or at the mailbox at 2:14 pm in CHICAGO, IL 60614. Reply STOP to cancel.", "why": "Tracking updates you signed up for come from short code 28777, with no fee and no link to pay."},
    {"channel": "email", "from": "Progressive <quotes@email.progressive.com>", "text": "Thanks for getting a quote! Your car insurance quote #4471-221 is saved. Pick up where you left off at progressive.com.", "why": "Marketing after you asked for a quote: the real progressive.com sender, and no SSN request."},
]

# "Uh-oh, I already..." emergency steps. Each step: (text, optional report id)
DAMAGE = {
    "clicked": {"label": "I tapped the link", "emoji": "👆", "steps": [
        ("Close the page. Don't type anything into it.", None),
        ("If you typed a password there, change it now in the real app or website, plus anywhere you reuse it. Turn on 2-step verification.", None),
        ("If you typed card details, call your bank right away and ask them to block the card.", "bank"),
        ("Update your phone or computer, then report the message.", "spam_text")]},
    "shared_info": {"label": "I shared personal info", "emoji": "🪪", "steps": [
        ("If you gave your Social Security number, freeze your credit (free) at Equifax, Experian and TransUnion today.", None),
        ("Go to IdentityTheft.gov. It builds your personal recovery plan.", "identity"),
        ("Watch your bank, mail and credit for anything you don't recognize.", None)]},
    "shared_card": {"label": "I gave card or bank details", "emoji": "💳", "steps": [
        ("Call your bank now using the number on the back of your card. Ask them to block the card and watch for fraud.", "bank"),
        ("Check your recent transactions and dispute anything you didn't make.", None),
        ("Report it so others are warned.", "ftc")]},
    "paid": {"label": "I sent money", "emoji": "💸", "methods": {
        "card": [("Call your card company now and dispute the charge. Card payments can often be reversed.", "bank")],
        "gift_card": [("Call the gift card company right away, using the number on the back of the card. Tell them it was a scam. Keep the card and receipt.", None)],
        "wire": [("Call your bank or the wire company (Western Union, MoneyGram) now. Ask for a wire recall. Speed matters.", "bank"),
                 ("Report to the FBI within 72 hours. It helps them try to freeze the money.", "ic3")],
        "p2p": [("Call your bank and the app (Zelle, Cash App, Venmo) now. Report it as fraud. Ask them to stop or reverse it.", "bank")],
        "crypto": [("Contact the crypto exchange or ATM company you used. Report the scammer's wallet address.", None),
                   ("Report to the FBI. Then beware: 'recovery services' that promise your crypto back are the next scam.", "ic3")],
        "cash": [("If a courier picked up cash, call your local police with the description and time.", "local")],
    }, "steps": [("You're not alone, and it's not your fault. Scammers are professionals. Report it, even if the money is gone.", "ftc")]},
    "gave_code": {"label": "I read them a code", "emoji": "🔢", "steps": [
        ("Open the real app or website (not a link) and change your password. Sign out all other devices.", None),
        ("Call the company using its official number and tell them someone may be in your account.", "bank"),
        ("Turn on 2-step verification with an app, not just texts.", None)]},
    "installed_app": {"label": "I installed an app they asked for", "emoji": "📲", "steps": [
        ("Turn off Wi-Fi or unplug the internet right now.", None),
        ("Uninstall the app (AnyDesk, TeamViewer, etc.). Don't log in to anything on that device yet.", None),
        ("From a different, clean device, change your email and bank passwords.", None),
        ("Call your bank, and have a trusted tech person check the computer.", "bank")]},
}
PAY_METHODS = {"card": "Credit/debit card", "gift_card": "Gift card", "wire": "Wire / Western Union", "p2p": "Zelle / Cash App / Venmo", "crypto": "Crypto / Bitcoin ATM", "cash": "Cash"}

BY_ID = {f["id"]: f for f in FAMILIES}
IDS = [f["id"] for f in FAMILIES]


def prompt_list() -> str:
    """Scam family list for the {scam_families} placeholder."""
    return "\n".join(f"- {f['id']}: {f['name']}. {f['hook']}" for f in FAMILIES)


def guess_family(text: str) -> str | None:
    """Keyword fallback when the AI is unavailable: the family with the most keyword hits."""
    import re
    best, hits = None, 0
    for f in FAMILIES:
        n = len({m.group(0).lower() for m in re.finditer(f["keywords"], text or "", re.I)})  # distinct terms
        if n > hits:
            best, hits = f["id"], n
    return best if hits >= 1 else None


def public_family(fid: str | None) -> dict | None:
    f = BY_ID.get(fid or "")
    if not f:
        return None
    field = next(x for x in FIELDS if x["id"] == f["field"])
    return {k: f[k] for k in ("id", "emoji", "name", "hook", "steps", "tell", "never")} | {
        "field": field, "report": [REPORTS[r] | {"id": r} for r in f["report"]]}


def library() -> dict:
    """Everything the field guide and the game need (no AI involved)."""
    return {
        "fields": FIELDS,
        "families": [public_family(f["id"]) | {"example": f["example"]} for f in FAMILIES],
        "legit": LEGIT,
        "damage": {k: {"label": v["label"], "emoji": v["emoji"],
                       "steps": [{"text": t, "report": REPORTS[r] | {"id": r} if r else None} for t, r in v["steps"]],
                       "methods": {m: [{"text": t, "report": REPORTS[r] | {"id": r} if r else None} for t, r in s] for m, s in v.get("methods", {}).items()}}
                   for k, v in DAMAGE.items()},
        "pay_methods": PAY_METHODS,
        "reports": REPORTS,
    }
