"""CropCast premium visual design system.

Static HTML/CSS only: no external JavaScript, no fabricated analytics, no network
calls or credentials. Native Streamlit widgets remain the interactive elements.
"""
from html import escape


STYLES = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root{--cc-ink:#15322a;--cc-moss:#285f44;--cc-lime:#d7f28a;--cc-paper:#f5f6ef;--cc-muted:#607169;--cc-border:#dfe6dc;--cc-shadow:0 18px 48px rgba(21,50,42,.07)}
html,body{font-family:'DM Sans',sans-serif}
.stApp{background:linear-gradient(180deg,#f8faf5 0%,#f1f5ed 100%);color:var(--cc-ink)}
[data-testid="stAppViewContainer"]{background:transparent}
[data-testid="stHeader"]{background:transparent}
[data-testid="stToolbar"]{color:#15322a}
.block-container{max-width:1300px;padding-top:1.2rem;padding-bottom:2.7rem}
.block-container h1,.block-container h2,.block-container h3{font-family:'Manrope',sans-serif;color:var(--cc-ink);font-weight:800;letter-spacing:-.045em}
.block-container h3{font-size:1.35rem;line-height:1.35}
.block-container p{line-height:1.58}
a{color:#216643}
.cc-navbar{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:12px 2px 22px;flex-wrap:wrap}
.cc-brand{display:flex;align-items:center;gap:11px;text-decoration:none}
.cc-logo{width:41px;height:41px;display:grid;place-items:center;background:#173e30;color:#edffcc;border-radius:13px;box-shadow:inset 0 0 0 1px rgba(255,255,255,.14)}
.cc-logo svg{width:26px;height:26px}
.cc-name{font-family:'Manrope',sans-serif;font-size:1.18rem;line-height:1.1;letter-spacing:-.06em;font-weight:800;color:#173d30}
.cc-name span{color:#3b8860}
.cc-navbar-sub{font-size:.63rem;letter-spacing:.14em;font-weight:800;color:#6d8377;text-transform:uppercase;margin-top:3px}
.cc-status{display:flex;align-items:center;gap:8px;border:1px solid #dbe9d9;background:rgba(255,255,255,.86);padding:9px 13px;border-radius:99px;color:#35614a;font-size:.75rem;font-weight:800;box-shadow:0 4px 12px rgba(23,65,46,.03)}
.cc-status-dot{width:8px;height:8px;border-radius:50%;background:#4baf69;box-shadow:0 0 0 3px rgba(75,175,105,.13)}
.cc-status small{color:#8e9a91;font-size:.69rem;font-weight:600}
.cc-hero{position:relative;isolation:isolate;overflow:hidden;background:#113328;border:1px solid #1c4b39;border-radius:28px;min-height:340px;display:grid;grid-template-columns:minmax(0,1.25fr) minmax(290px,.75fr);gap:18px;align-items:center;padding:38px 44px 38px;color:#f6fbed;box-shadow:0 24px 45px rgba(22,64,45,.16)}
.cc-hero:before{content:"";position:absolute;inset:0;pointer-events:none;z-index:-2;background:radial-gradient(circle at 83% 18%,rgba(179,227,145,.21),transparent 37%),radial-gradient(circle at 12% 87%,rgba(88,164,122,.14),transparent 38%),linear-gradient(118deg,#112c24 0%,#1a513b 75%,#194432 100%)}
.cc-hero:after{content:"";position:absolute;inset:-20%;z-index:-1;opacity:.24;pointer-events:none;background:repeating-radial-gradient(circle at 80% 45%,transparent 0 27px,rgba(216,249,184,.17) 28px 29px,transparent 30px 51px);mask-image:linear-gradient(90deg,transparent,black 42%);}
.cc-hero-left{max-width:760px;position:relative;z-index:1}
.cc-eyebrow{display:inline-flex;align-items:center;gap:9px;font-size:.68rem;font-weight:800;letter-spacing:.16em;color:#cbf29e;text-transform:uppercase;padding:8px 12px;background:rgba(209,250,160,.09);border:1px solid rgba(201,241,156,.23);border-radius:100px}
.cc-eyebrow i{width:5px;height:5px;background:#c9ef8c;border-radius:50%;display:block}
.cc-hero h1{font-size:clamp(2.4rem,4.4vw,4.35rem);line-height:1.09;letter-spacing:-.066em;color:#f3f9ee;margin:18px 0 17px;max-width:680px;font-family:'Manrope',sans-serif;font-weight:800}
.cc-hero h1 em{font-style:normal;background:linear-gradient(94deg,#e2fb9e,#a8eab0);color:transparent;background-clip:text;-webkit-background-clip:text}
.cc-hero p{color:#b6d0be;max-width:570px;font-size:1.02rem;line-height:1.7;margin:0}
.cc-hero-tags{display:flex;gap:8px;flex-wrap:wrap;margin-top:24px}
.cc-hero-tags span{font-weight:700;font-size:.73rem;padding:8px 12px;border-radius:99px;border:1px solid rgba(210,241,195,.17);color:#def3dd;background:rgba(255,255,255,.06)}
.cc-visual{position:relative;align-self:stretch;min-height:265px;display:grid;place-items:center;z-index:1}
.cc-orbit{position:relative;width:min(100%,330px);aspect-ratio:1;border-radius:50%;border:1px solid rgba(210,251,184,.32);display:grid;place-items:center;box-shadow:inset 0 0 0 22px rgba(235,255,215,.017),inset 0 0 0 56px rgba(235,255,215,.025)}
.cc-orbit:before,.cc-orbit:after{content:"";position:absolute;border-radius:50%;inset:13%;border:1px dashed rgba(213,254,192,.27)}
.cc-orbit:after{inset:28%;border:1px solid rgba(213,254,192,.22)}
.cc-orbit-center{display:flex;flex-direction:column;align-items:center;justify-content:center;width:43%;aspect-ratio:1;background:radial-gradient(circle at 30% 20%,#3d8058,#174b35);border:1px solid rgba(216,255,184,.33);border-radius:50%;box-shadow:0 8px 35px rgba(2,20,16,.28)}
.cc-orbit-center svg{width:48%;height:48%;margin-bottom:2px}
.cc-orbit-center span{font-size:.55rem;font-weight:900;letter-spacing:.18em;color:#d8f5b4}
.cc-sat{position:absolute;background:rgba(11,42,30,.95);border:1px solid rgba(202,248,177,.31);color:#e5f8d5;border-radius:13px;padding:11px 14px;box-shadow:0 14px 35px rgba(0,20,12,.2);font-size:.72rem;line-height:1.55}
.cc-sat strong{display:block;font-family:'Manrope',sans-serif;font-size:.95rem;color:#effbdd}
.cc-sat-one{left:-5%;top:10%}
.cc-sat-two{right:-7%;bottom:11%}
.cc-sat-caption{position:absolute;bottom:1%;font-size:.61rem;color:#b5cdb8;letter-spacing:.17em;text-transform:uppercase}
.cc-pulse{animation:cc-float 6s ease-in-out infinite}
@keyframes cc-float{0%,100%{transform:translateY(0)}50%{transform:translateY(-9px)}}
.cc-metrics-title{font-size:.69rem;color:#718778;font-weight:800;text-transform:uppercase;letter-spacing:.14em;margin:25px 0 12px}
.cc-metric-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:13px}
.cc-metric{position:relative;overflow:hidden;border:1px solid #e0e8dc;border-radius:18px;background:#fff;padding:20px 19px;min-height:132px;box-shadow:var(--cc-shadow)}
.cc-metric:after{content:"";width:77px;height:77px;position:absolute;right:-34px;top:-34px;border-radius:50%;border:15px solid #f1f7e9}
.cc-metric-label{display:flex;gap:6px;align-items:center;font-size:.76rem;color:#66796d;font-weight:700}
.cc-metric-value{font-family:'Manrope',sans-serif;font-size:clamp(1.7rem,2.4vw,2.25rem);line-height:1.3;font-weight:800;letter-spacing:-.06em;color:#173c2b;margin:7px 0 3px}
.cc-metric-caption{color:#789085;font-size:.69rem}
.cc-workflows{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:13px;margin-top:13px}
.cc-workflow{border-radius:17px;padding:16px 18px;border:1px solid #e1e9dc;background:#fdfefb;min-height:97px;display:flex;align-items:center;gap:13px}
.cc-workflow-icon{display:grid;place-items:center;width:41px;height:41px;border-radius:13px;background:#eaf4db;color:#356046;font-size:1.1rem;flex-shrink:0}
.cc-workflow h4{font-family:'Manrope',sans-serif;font-size:.83rem;letter-spacing:-.02em;color:#1b392c;font-weight:800;margin:0 0 3px}
.cc-workflow p{font-size:.71rem;color:#7c8a7e;line-height:1.42;margin:0}
.cc-section-title{padding:10px 0 8px;margin:6px 0 4px}
.cc-section-kicker{font-size:.7rem;letter-spacing:.15em;color:#43805b;text-transform:uppercase;font-weight:900}
.cc-section-title h2{font-family:'Manrope',sans-serif!important;font-size:clamp(1.5rem,2.5vw,2rem)!important;letter-spacing:-.05em!important;margin:6px 0!important}
.cc-section-title p{font-size:.86rem;color:#758779;margin:0;max-width:720px}
[data-testid="stTabs"]{background:transparent}
[data-testid="stTabs"]>div:first-child{margin:16px 0 22px}
[data-testid="stTabs"] [data-baseweb="tab-list"]{gap:6px;flex-wrap:wrap;overflow-x:auto;background:#e7efe3;border:1px solid #dce7d8;padding:6px;border-radius:15px}
[data-testid="stTabs"] button[role="tab"]{font-family:'DM Sans',sans-serif;font-weight:800;color:#53685b!important;font-size:.82rem;border-radius:10px;padding:10px 16px;white-space:nowrap}
[data-testid="stTabs"] button[role="tab"]:hover{background:#d5e8d0;color:#16422d!important}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"]{background:#fff;color:#165038!important;box-shadow:0 3px 13px rgba(42,70,50,.1)}
[data-testid="stTabs"] [data-baseweb="tab-highlight"],[data-testid="stTabs"] [data-baseweb="tab-border"]{background:transparent}
[data-testid="stForm"]{border:1px solid #dbe5d9!important;border-radius:19px!important;background:#fff!important;padding:22px!important;box-shadow:var(--cc-shadow)}
[data-testid="stWidgetLabel"],[data-testid="stWidgetLabel"] p{color:#2d4839!important;font-weight:800!important;opacity:1!important}
[data-testid="stCaptionContainer"] p{color:#6b8272!important}
[data-testid="stSelectbox"] [data-baseweb="select"]>div,
[data-testid="stNumberInput"] input{background:#f8faf5!important;border-color:#d8e6d9!important;color:#173a28!important;border-radius:11px!important}
[data-testid="stSelectbox"] [data-baseweb="select"] *{color:#173a28}
[data-testid="stNumberInput"] button{background:#edf2e8!important}
[data-testid="stNumberInput"] button svg{color:#2d6042}
[data-testid="stFormSubmitButton"] button,[data-testid="stButton"] button[kind="primary"]{border:0!important;background:#1c6040!important;color:#fff!important;border-radius:12px!important;box-shadow:0 9px 22px rgba(28,96,64,.16);font-weight:800!important;transition:transform .18s,box-shadow .18s,background .18s}
[data-testid="stFormSubmitButton"] button:hover,[data-testid="stButton"] button[kind="primary"]:hover{background:#154e34!important;transform:translateY(-1px);box-shadow:0 12px 26px rgba(28,96,64,.24)}
[data-testid="stButton"] button:not([kind="primary"]),[data-testid="stDownloadButton"] button{border:1px solid #cddfcf!important;border-radius:11px!important;background:#fff!important;color:#245a3c!important;font-weight:800!important}
[data-testid="stButton"] button:not([kind="primary"]):hover,[data-testid="stDownloadButton"] button:hover{background:#edf6e7!important;border-color:#94cba4!important}
.cc-output{border-radius:20px;padding:26px 30px;background:linear-gradient(115deg,#163e2d,#246343);color:#f7fceb;display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;border:1px solid #20563d;box-shadow:0 19px 44px rgba(20,80,47,.18);margin:18px 0}
.cc-output-eyebrow{font-size:.7rem;font-weight:900;text-transform:uppercase;letter-spacing:.14em;color:#c7ef9f}
.cc-output-value{font-family:'Manrope',sans-serif;font-size:clamp(2.4rem,5vw,3.8rem);font-weight:800;letter-spacing:-.06em;line-height:1.26}
.cc-output-unit{font-size:.88rem;color:#cce8cf;font-weight:600}
.cc-output-note{font-size:.81rem;color:#d9efdc}
.cc-output-pill{border:1px solid rgba(217,251,201,.25);border-radius:13px;padding:13px 16px;background:rgba(255,255,255,.07);font-size:.7rem;color:#e8f1df}
.cc-output-pill strong{display:block;font-family:'Manrope',sans-serif;color:#f6fff2;font-size:.87rem;margin:5px 0}
[data-testid="stMetric"]{background:#fff;border:1px solid #dce9db;padding:17px;border-radius:14px;box-shadow:var(--cc-shadow)}
[data-testid="stMetricValue"]{color:#17452b!important}
[data-testid="stExpander"]{background:#fff;border:1px solid #dce8d9!important;border-radius:15px!important}
[data-testid="stExpander"] summary{color:#1d4832;font-weight:800}
[data-testid="stDataFrame"],[data-testid="stTable"]{border-radius:13px;overflow:hidden;border:1px solid #e2e9de}
[data-testid="stAlert"]{border-radius:13px}
.cc-footer{margin-top:32px;border-top:1px solid #d7e5d8;padding:22px 3px;display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;color:#6b7e70;font-size:.74rem}
.cc-footer strong{color:#264935}
.cc-step-row{display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;margin:16px 0}
.cc-step{border:1px solid #ddebd7;border-radius:11px;padding:11px 14px;font-weight:700;color:#3b694b;background:#fff;font-size:.76rem}
.cc-step b{font-family:'Manrope',sans-serif;margin-right:6px;color:#328456}
:focus-visible{outline:2px solid #5c9a54!important;outline-offset:2px}
@media(min-width:769px){[data-testid="stTabs"]>div:first-child{position:sticky;top:0;z-index:20}}
@media(max-width:1000px){.cc-hero{grid-template-columns:1fr;min-height:auto;padding:30px}.cc-visual{min-height:190px}.cc-orbit{width:240px}.cc-sat-one{left:8%}.cc-sat-two{right:8%}}
@media(max-width:750px){.block-container{padding:1rem .9rem 2.3rem}.cc-hero{border-radius:19px;padding:23px 21px}.cc-hero h1{font-size:2.25rem}.cc-hero p{font-size:.9rem}.cc-visual{display:none}.cc-metric-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.cc-workflows{grid-template-columns:1fr;gap:9px}.cc-metric{padding:13px;min-height:106px}.cc-metric-value{font-size:1.7rem}.cc-navbar{padding-bottom:13px}.cc-status small{display:none}.cc-output{padding:18px}.cc-output-value{font-size:2.6rem}[data-testid="stTabs"] button[role="tab"]{font-size:.76rem;padding:8px 11px}}
@media(prefers-reduced-motion:reduce){.cc-pulse{animation:none!important}*,*:before,*:after{scroll-behavior:auto!important;transition:none!important}}
</style>
"""


def brand_banner():
    return """<div class="cc-navbar">
      <div class="cc-brand">
        <span class="cc-logo" aria-hidden="true"><svg viewBox="0 0 32 32" fill="none"><path d="M16 27V11M16 19C8 19 5 13 6 6c7 0 11 4 10 13Zm0-3c0-7 4-10 11-10 0 7-4 10-11 10Z" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"/></svg></span>
        <span><div class="cc-name">crop<span>cast.</span></div><div class="cc-navbar-sub">Field intelligence / Research prototype</div></span>
      </div>
      <div class="cc-status"><span class="cc-status-dot"></span> Model B ready <small>· AI research demo</small></div>
    </div>"""


def hero_banner():
    return """<section class="cc-hero" aria-label="CropCast introduction">
      <div class="cc-hero-left">
        <div class="cc-eyebrow"><i></i> Agriculture meets intelligence</div>
        <h1>A clearer view of<br><em>what the field could yield.</em></h1>
        <p>Explore crop productivity using a trained Random Forest model. Compare conditions, test scenarios and understand model evidence—all in one research-ready workspace.</p>
        <div class="cc-hero-tags"><span>✓ Real model inference</span><span>✧ Six supported crops</span><span>↗ Interactive analysis</span></div>
      </div>
      <div class="cc-visual" aria-hidden="true">
        <div class="cc-orbit cc-pulse">
          <div class="cc-orbit-center">
            <svg viewBox="0 0 100 100" fill="none"><path d="M50 82V42M50 61C28 61 18 43 23 23c18 2 30 15 27 38Zm0-9c0-21 12-30 31-30 0 22-12 32-31 30Z" stroke="#e5fbaf" stroke-width="4.2" stroke-linejoin="round" stroke-linecap="round"/></svg>
            <span>MODEL B</span>
          </div>
          <div class="cc-sat cc-sat-one">MODEL INPUTS<strong>08 variables</strong></div>
          <div class="cc-sat cc-sat-two">CROP CATEGORIES<strong>06 supported</strong></div>
        </div>
        <div class="cc-sat-caption">Conceptual field-intelligence visual</div>
      </div>
    </section>"""


def metric_cards():
    items = [
        ("01 / Model fit", "0.9031", "R² · random held-out test"),
        ("02 / Prediction error", "0.5233", "RMSE · tonnes / hectare"),
        ("03 / Training examples", "40,000", "Sampled experiment records"),
        ("04 / Supported crops", "06", "Categories in deployed Model B"),
    ]
    body = "".join(
        f'<div class="cc-metric"><div class="cc-metric-label">{escape(title)}</div>'
        f'<div class="cc-metric-value">{escape(value)}</div>'
        f'<div class="cc-metric-caption">{escape(caption)}</div></div>'
        for title, value, caption in items
    )
    return '<div class="cc-metrics-title">Research overview <span style="font-weight:500;text-transform:none;letter-spacing:0">(recorded experiment)</span></div><div class="cc-metric-grid">' + body + '</div>'


def workflow_cards():
    return """<div class="cc-workflows">
    <div class="cc-workflow"><div class="cc-workflow-icon">◎</div><div><h4>Model predictions</h4><p>Eight inputs, one verified Random Forest pipeline</p></div></div>
    <div class="cc-workflow"><div class="cc-workflow-icon">◫</div><div><h4>Scenario explorer</h4><p>Compare crops and one-variable changes</p></div></div>
    <div class="cc-workflow"><div class="cc-workflow-icon">↗</div><div><h4>Research evidence</h4><p>Metrics, residual charts and transparent limitations</p></div></div>
    </div>"""


def section_heading(kicker: str, title: str, subtitle: str):
    return (
        f'<div class="cc-section-title"><div class="cc-section-kicker">{escape(kicker)}</div>'
        f'<h2>{escape(title)}</h2><p>{escape(subtitle)}</p></div>'
    )


def result_card(crop: str, region: str, predicted: float):
    return (
        f'<div class="cc-output"><div><div class="cc-output-eyebrow">Estimated yield · {escape(crop)}</div>'
        f'<div class="cc-output-value">{predicted:,.2f} <span class="cc-output-unit">t / ha</span></div>'
        f'<div class="cc-output-note">≈ {predicted * 1000:,.0f} kg per hectare · {escape(region)} region</div></div>'
        f'<div class="cc-output-pill">SOURCE<strong>Random Forest / Model B</strong>Educational estimate · not field-validated</div></div>'
    )


def footer():
    return (
        '<footer class="cc-footer"><div><strong>CropCast AI</strong> · Crop yield prediction & scenario analytics</div>'
        '<div>Research prototype · No independent farm validation · <a href="https://github.com/Kxni5hk/crop-yield-predictor" target="_blank" rel="noopener noreferrer">Source on GitHub ↗</a></div></footer>'
    )
