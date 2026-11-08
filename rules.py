"""NeVedis rule engine: fast, deterministic English-keyword checks that run before Gemini.

check(text) -> {"rule_score": 0-100, "signals": [Signal, ...]}
Each signal is "hard" (a classic scam marker, forces the final score to 80+) or "soft"
(suspicious on its own, adds weight). Hard signal ids match the schema's hard_red_flags enum.
"""
import re
from dataclasses import dataclass, asdict

HARD_WEIGHT = 45
SOFT_WEIGHT = {"shortened_link": 20, "urgency": 15, "brand_link_mismatch": 20, "payment_app_mention": 15,
               "personal_data_request": 20, "generic_greeting": 8, "spf_softfail": 15, "threat_language": 15}


@dataclass
class Signal:
    id: str
    kind: str        # "hard" or "soft"
    label: str       # plain-English explanation
    evidence: str    # exact text from the item

    def as_dict(self):
        return asdict(self)


# ---------- reference data ----------
# Brand keyword -> its official registrable domains.
BRANDS = {
    "usps": ["usps.com"], "irs": ["irs.gov"], "paypal": ["paypal.com"], "amazon": ["amazon.com"],
    "apple": ["apple.com", "icloud.com"], "chase": ["chase.com"], "bankofamerica": ["bankofamerica.com"],
    "wellsfargo": ["wellsfargo.com"], "citibank": ["citi.com", "citibank.com"], "fedex": ["fedex.com"],
    "ups": ["ups.com"], "dhl": ["dhl.com"], "microsoft": ["microsoft.com", "live.com", "outlook.com"],
    "netflix": ["netflix.com"], "google": ["google.com", "gmail.com"], "geico": ["geico.com"],
    "progressive": ["progressive.com"], "statefarm": ["statefarm.com"], "allstate": ["allstate.com"],
    "ssa": ["ssa.gov"], "uscis": ["uscis.gov"], "ezpass": ["e-zpassny.com", "ezpassnj.com", "ezpassva.com"],
    "venmo": ["venmo.com"], "zelle": ["zellepay.com"], "coinbase": ["coinbase.com"], "medicare": ["medicare.gov"],
    "walmart": ["walmart.com"], "costco": ["costco.com"], "verizon": ["verizon.com"], "att": ["att.com"],
    "target": ["target.com"], "ebay": ["ebay.com"], "facebook": ["facebook.com", "fb.com"], "instagram": ["instagram.com"],
    "whatsapp": ["whatsapp.com"], "docusign": ["docusign.com", "docusign.net"], "dropbox": ["dropbox.com"],
    "norton": ["norton.com"], "mcafee": ["mcafee.com"], "bestbuy": ["bestbuy.com"], "dyson": ["dyson.com"],
    "comed": ["comed.com"], "studentaid": ["studentaid.gov"], "spectrum": ["spectrum.com", "spectrum.net"],
    "tmobile": ["t-mobile.com"], "sunpass": ["sunpass.com"], "fastrak": ["bayareafastrak.org"], "binance": ["binance.com", "binance.us"],
}
# Names as people write them in a message -> brand key above.
BRAND_NAMES = {
    r"\busps\b|postal service": "usps", r"\birs\b|internal revenue": "irs", r"paypal": "paypal",
    r"\bamazon\b": "amazon", r"\bapple\b|icloud": "apple", r"\bchase\b": "chase", r"bank of america": "bankofamerica",
    r"wells fargo": "wellsfargo", r"\bciti(bank)?\b": "citibank", r"fedex": "fedex", r"\bups\b": "ups", r"\bdhl\b": "dhl",
    r"microsoft|outlook": "microsoft", r"netflix": "netflix", r"\bgeico\b": "geico", r"progressive": "progressive",
    r"state farm": "statefarm", r"allstate": "allstate", r"social security": "ssa", r"uscis": "uscis",
    r"e-?zpass": "ezpass", r"venmo": "venmo", r"coinbase": "coinbase", r"medicare": "medicare",
    r"\btarget\b": "target", r"\bebay\b": "ebay", r"facebook": "facebook", r"instagram": "instagram", r"whatsapp": "whatsapp",
    r"docusign": "docusign", r"dropbox": "dropbox", r"norton": "norton", r"mcafee": "mcafee", r"geek squad|best buy": "bestbuy",
    r"\bdyson\b": "dyson", r"comed": "comed", r"sunpass": "sunpass", r"fastrak": "fastrak", r"t-?mobile": "tmobile",
}
SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "buff.ly", "cutt.ly", "rebrand.ly", "rb.gy",
              "shorturl.at", "t.ly", "tiny.cc", "s.id", "lnkd.in", "bl.ink", "short.io", "v.gd", "qrco.de", "shorturl.com"}
REMOTE_APPS = r"anydesk|teamviewer|ultraviewer|rustdesk|logmein|splashtop|quick ?assist|screenconnect|connectwise|supremo|zoho assist|ammyy"
MULTI_TLDS = {"co.uk", "com.au", "co.in", "com.br", "co.jp", "com.mx", "co.nz", "org.uk", "gov.uk"}

URL_RE = re.compile(r"""(?:https?://|www\.)[^\s<>"'()]+|\b(?:[a-z0-9-]+\.)+(?:com|net|org|info|xyz|top|site|online|live|shop|app|io|co|us|gov|ly|me|cc|click|link|help|support|vip|icu|buzz|cn|ru)\b(?:/[^\s<>"'()]*)?""", re.I)


def _find(pattern, text, flags=re.I):
    m = re.search(pattern, text, flags)
    return _context(text, m.start(), m.end()) if m else None


def _context(text, a, b, pad=40):
    """The matched text plus a little context on each side, kept within its own line."""
    line_start = text.rfind("\n", 0, a) + 1
    line_end = text.find("\n", b)
    line_end = len(text) if line_end == -1 else line_end
    return text[max(line_start, a - pad):min(line_end, b + pad)].strip()


def _host(url):
    u = re.sub(r"^[a-z]+://", "", url.strip(), flags=re.I)
    return u.split("/")[0].split("?")[0].split("#")[0].split(":")[0].lower().rstrip(".")


def registrable(host):
    parts = host.split(".")
    if len(parts) >= 3 and ".".join(parts[-2:]) in MULTI_TLDS:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


def _deleet(s):
    s = s.replace("rn", "m").replace("vv", "w")
    return s.translate(str.maketrans({"0": "o", "1": "l", "3": "e", "4": "a", "5": "s", "7": "t", "@": "a", "$": "s"}))


def _edit1(a, b):
    """True if a and b differ by exactly one insert/delete/substitute."""
    if a == b or abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) == 1
    if len(a) > len(b): a, b = b, a
    return any(b[:i] + b[i + 1:] == a for i in range(len(b)))


def _official(reg):
    return any(reg == d for ds in BRANDS.values() for d in ds)


def _brand_name(b):
    return {"bankofamerica": "Bank of America", "wellsfargo": "Wells Fargo", "statefarm": "State Farm", "ezpass": "E-ZPass",
            "bestbuy": "Best Buy / Geek Squad", "tmobile": "T-Mobile", "studentaid": "StudentAid.gov", "comed": "ComEd",
            "fastrak": "FasTrak", "sunpass": "SunPass", "paypal": "PayPal", "icloud": "iCloud"}.get(b, b.upper() if len(b) <= 4 else b.title())


def check_links(text, out, links=None):
    links = [] if links is None else links
    add = lambda raw, host, reg, status, pretends=None, real=None: links.append(
        {"url": raw, "host": host, "domain": reg, "status": status, "pretends": pretends, "real": real})
    # Header lines (From:, Reply-To:, Authentication-Results: ...) are checked by check_email_headers.
    text = "\n".join("" if re.match(r"^\s*(From|To|Cc|Reply-To|Return-Path|Subject|Date|Message-ID|Authentication-Results|ARC-[\w-]+|Received(-SPF)?|DKIM-Signature)\s*:", ln, re.I) else ln for ln in text.splitlines())
    mentioned = {key for pat, key in BRAND_NAMES.items() if re.search(pat, text, re.I)}
    seen = set()
    for m in URL_RE.finditer(text):
        if m.start() > 0 and text[m.start() - 1] == "@":
            continue  # part of an email address, not a link
        raw = m.group(0).rstrip(".,;:!?")
        host = _host(raw)
        if not host or host in seen or "." not in host:
            continue
        seen.add(host)
        reg = registrable(host)
        ev = raw
        if "xn--" in host or re.search(r"[^\x00-\x7f]", host):
            add(raw, host, reg, "punycode")
            out.append(Signal("lookalike_or_mismatched_link", "hard", f"The link {host} uses special look-alike letters (punycode) to imitate a real website.", ev)); continue
        if reg in SHORTENERS:
            add(raw, host, reg, "shortener")
            out.append(Signal("shortened_link", "soft", f"The link is shortened ({reg}), which hides where it really goes.", ev)); continue
        if _official(reg):
            add(raw, host, reg, "official", real=reg)
            continue
        label = _deleet(reg.split(".")[0])
        whole = _deleet(host.replace(".", "-"))
        hit = None
        tokens = [_deleet(t) for t in re.split(r"[-.]", host)]
        for brand, domains in BRANDS.items():
            names = {brand, *(d.split(".")[0].replace("-", "") for d in domains)}
            if any(len(n) >= 4 and n in whole.replace("-", "") for n in names) or any(len(n) == 3 and n in tokens for n in names):
                hit = brand; break
            if any(len(n) >= 5 and (_edit1(label, n) or any(_edit1(t, n) for t in tokens)) for n in names):
                hit = brand; break
        if hit:
            add(raw, host, reg, "lookalike", _brand_name(hit), BRANDS[hit][0])
            out.append(Signal("lookalike_or_mismatched_link", "hard",
                              f"The link {host} pretends to be {_brand_name(hit)}, but the real website is {BRANDS[hit][0]}.", ev))
        elif mentioned:
            b = sorted(mentioned)[0]
            add(raw, host, reg, "brand_mismatch", _brand_name(b), BRANDS[b][0])
            out.append(Signal("brand_link_mismatch", "soft",
                              f"The message talks about {_brand_name(b)}, but the link goes to {reg}, not {BRANDS[b][0]}.", ev))
        else:
            add(raw, host, reg, "unknown")


def check_email_headers(text, out):
    hdr = {}
    for line in text.splitlines()[:60]:
        m = re.match(r"^(From|Reply-To|Return-Path|Authentication-Results|Received-SPF|ARC-Authentication-Results)\s*:\s*(.+)$", line.strip(), re.I)
        if m:
            hdr.setdefault(m.group(1).lower(), m.group(0).strip())
    if not hdr:
        return
    addr = lambda s: (re.findall(r"[\w.+-]+@([\w.-]+\.[a-z]{2,})", s or "", re.I) or [None])[-1]
    frm = hdr.get("from"); from_dom = addr(frm)
    if frm and from_dom:
        disp = frm.split(":", 1)[1].split("<")[0].lower()
        for pat, key in BRAND_NAMES.items():
            if re.search(pat, disp, re.I) and not any(registrable(from_dom.lower()) == d for d in BRANDS[key]):
                out.append(Signal("sender_domain_mismatch_or_auth_fail", "hard",
                                  f"The sender name says {key.upper() if len(key) <= 5 else key.title()}, but the email really comes from {from_dom}.", frm)); break
    rt = hdr.get("reply-to"); rt_dom = addr(rt)
    if from_dom and rt_dom and registrable(rt_dom.lower()) != registrable(from_dom.lower()):
        out.append(Signal("sender_domain_mismatch_or_auth_fail", "hard",
                          f"Replies go to {rt_dom}, a different address than the sender ({from_dom}).", rt))
    auth = " ".join(hdr.get(k, "") for k in ("authentication-results", "arc-authentication-results", "received-spf"))
    for proto in ("spf", "dkim", "dmarc"):
        if re.search(rf"\b{proto}\s*=\s*(fail|permerror)\b", auth, re.I) or (proto == "spf" and re.search(r"received-spf:\s*fail\b", auth, re.I)):
            line = next(v for k, v in hdr.items() if re.search(rf"{proto}\s*=\s*(fail|permerror)|received-spf:\s*fail", v, re.I))
            out.append(Signal("sender_domain_mismatch_or_auth_fail", "hard",
                              f"The email failed the {proto.upper()} check, so the sender is probably faked.", line))
        elif proto == "spf" and re.search(r"\bspf\s*=\s*softfail\b|received-spf:\s*softfail", auth, re.I):
            out.append(Signal("spf_softfail", "soft", "The email only partly passed the sender check (SPF softfail).", hdr.get("received-spf") or hdr.get("authentication-results")))


def check_words(text, out):
    t = text
    # Unusual payment methods
    ev = _find(r"gift ?cards?|itunes card|google play card|steam card|apple card balance|bitcoin|\bbtc\b|crypto(currency)?|\busdt\b|ethereum|bitcoin atm|wire transfer|wire the|western union|moneygram|safe account|secure account", t)
    if ev:
        out.append(Signal("unusual_payment_method", "hard", "Asks for payment by gift card, crypto or wire. Real companies and agencies never do this.", ev))
    ev = _find(r"(pay|send|transfer|deposit)\b[^.\n]{0,40}\b(zelle|cash ?app|venmo)\b|\b(zelle|cash ?app|venmo)\b[^.\n]{0,40}\b(pay|send|transfer|payment)", t)
    if ev:
        out.append(Signal("unusual_payment_method", "hard", "Asks you to pay a person through Zelle, Cash App or Venmo. That money usually can't be returned.", ev))
    elif (ev := _find(r"\b(zelle|cash ?app|venmo)\b", t)):
        out.append(Signal("payment_app_mention", "soft", "Mentions a person-to-person payment app.", ev))
    # Code / password requests (but not legit "never share this code" notices)
    m = re.search(r"\b(send|share|read|tell|give|provide|reply with|confirm|enter|forward)\b[^.\n]{0,40}\b(code|passcode|password|pin|otp)\b"
                  r"|\b(verification|one[- ]time|security|6[- ]digit|confirmation) code\b[^.\n]{0,30}\b(to us|back|with us|to the agent|to me)\b"
                  r"|\bcode\b[^\n]{0,60}\b(text|send|read|give|forward) (it|that|this)( back| to me| over)?\b", t, re.I)
    if m and not re.search(r"\b(never|don'?t|do not|not)\s+(share|give|send|tell)\b", t[max(0, m.start() - 30):m.end()], re.I):
        out.append(Signal("asks_for_code_or_password", "hard", "Asks for a code or password. No real company will ever ask you for these.", _context(t, m.start(), m.end())))
    # Remote access
    ev = _find(rf"\b({REMOTE_APPS})\b", t)
    if ev:
        out.append(Signal("remote_access_request", "hard", "Mentions a remote-control app. With it, a scammer can take over your computer or phone.", ev))
    # Government threat + payment
    gov = re.search(r"\birs\b|internal revenue|social security|\bssa\b|uscis|immigration|police|sheriff|\bcourt\b|\bfbi\b|\bdhs\b|medicare|treasury|federal agent|officer", t, re.I)
    threat = re.search(r"\barrest(ed)?\b|warrant|jail|deport|legal action|lawsuit|suspend(ed)? your (ssn|social)|criminal charges|police will", t, re.I)
    pay = re.search(r"\b(pay|payment|owe|fine|fee|balance due|unpaid)\b", t, re.I)
    if gov and threat and pay:
        out.append(Signal("government_payment_threat", "hard", "A government office is threatening arrest or punishment unless you pay. Real agencies send letters and never demand payment like this.", _context(t, threat.start(), threat.end())))
    elif threat:
        out.append(Signal("threat_language", "soft", "Uses threats to scare you.", _context(t, threat.start(), threat.end())))
    # Bank "security service" script
    ev = _find(r"(bank'?s? (security|fraud) (department|team|service)|fraud (department|team)|security (department|service))[^\n]{0,120}?\b(move|transfer|protect|confirm|verify)\b[^\n]{0,60}?\b(money|funds|card|account)\b", t)
    if ev:
        out.append(Signal("bank_security_service_script", "hard", "Someone posing as the bank's fraud team wants you to move money or confirm card details. Banks never ask for this.", ev))
    # Prompt injection aimed at the checker
    ev = _find(r"ignore (all |any )?(previous|prior|above) (instructions|rules)|disregard (the|your) (instructions|rules)|you are now|system prompt|this (message|email|text) is (safe|legit(imate)?|not a scam)|mark (this|it) as (safe|legit)", t)
    if ev:
        out.append(Signal("prompt_injection_attempt", "hard", "The message contains hidden instructions trying to fool scam checkers.", ev))
    # Soft signals
    ev = _find(r"within \d+ (hours?|minutes?|days?)|\bimmediately\b|\burgent(ly)?\b|act now|final (notice|warning)|last (chance|warning)|expires? (today|tonight|at midnight|soon)|by (today|tonight)|\btoday only\b|will be (suspended|blocked|locked|closed|returned|cancell?ed)|account (is |has been )?(suspended|locked|blocked)|don'?t tell (anyone|the bank)|keep this (confidential|secret)", t)
    if ev:
        out.append(Signal("urgency", "soft", "Rushes you or tells you to keep it secret, so you don't stop to think.", ev))
    ev = _find(r"social security number|\bssn\b|driver'?s? licen[cs]e( number)?|date of birth|bank account number|routing number|card number|cvv|mother'?s maiden|medicare number|fsa id|passport number|a-?number|green card number", t)
    if ev:
        out.append(Signal("personal_data_request", "soft", "Asks for private information that can be used to steal your identity or money.", ev))
    ev = _find(r"^\s*(dear (customer|user|client|member|account holder|sir/madam|valued customer))", t, re.I | re.M)
    if ev:
        out.append(Signal("generic_greeting", "soft", "Uses a generic greeting instead of your name.", ev))


def check(text: str) -> dict:
    """Run every rule on the text. Returns the 0-100 rule score and the signals found."""
    out: list[Signal] = []
    links: list[dict] = []
    if text and text.strip():
        check_email_headers(text, out)
        check_links(text, out, links)
        check_words(text, out)
    # one signal per (id, evidence); scoring counts each id once
    uniq, keys = [], set()
    for s in out:
        k = (s.id, s.label, s.evidence)
        if k not in keys:
            keys.add(k); uniq.append(s)
    ids_hard = {s.id for s in uniq if s.kind == "hard"}
    ids_soft = {s.id for s in uniq if s.kind == "soft"}
    score = min(100, HARD_WEIGHT * len(ids_hard) + sum(SOFT_WEIGHT.get(i, 10) for i in ids_soft))
    uniq.sort(key=lambda s: s.kind != "hard")
    return {"rule_score": score, "signals": [s.as_dict() for s in uniq], "links": links}


def format_for_prompt(result: dict) -> str:
    """Text block for the {rule_signals} placeholder."""
    if not result["signals"]:
        return f"Rule score: {result['rule_score']}/100. No rule signals found."
    lines = [f"Rule score: {result['rule_score']}/100."]
    for s in result["signals"]:
        lines.append(f"- [{s['kind'].upper()}] {s['id']}: {s['label']} Evidence: \"{s['evidence']}\"")
    return "\n".join(lines)
