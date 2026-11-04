"""CropCast v6 navigation rail and action-first workspace shell.

Original CSS and Streamlit-native controls. No copied third-party components.
"""
from html import escape
import streamlit as st


PAGES = (
    "Overview",
    "Yield Predictor",
    "Crop Scenarios",
    "Model A Research",
    "Batch Studio",
    "Weather Context",
    "Session History",
    "Research & About",
)
LABELS = {
    "Overview": "⌂   Overview",
    "Yield Predictor": "◈   Yield Predictor",
    "Crop Scenarios": "◫   Crop Scenarios",
    "Model A Research": "◎   Model A Research",
    "Batch Studio": "▤   Batch Studio",
    "Weather Context": "☼   Weather Context",
    "Session History": "◷   Session History",
    "Research & About": "◉   Research & About",
}

WORKSPACE_STYLES = r"""
<style>
/* Left-hand product rail: Streamlit radio buttons remain keyboard-accessible. */
[data-testid="stSidebar"]{background:#102f25!important;border-right:1px solid #315641!important}
[data-testid="stSidebar"] [data-testid="stSidebarContent"]{padding-top:1.2rem!important}
[data-testid="stSidebar"] [data-testid="stVerticalBlock"]{gap:.65rem!important}
[data-testid="stSidebar"] [data-testid="stWidgetLabel"]{display:none!important}
[data-testid="stSidebar"] [role="radiogroup"]{gap:7px!important}
[data-testid="stSidebar"] [role="radiogroup"] label{
    display:flex;align-items:center;min-height:46px;
    padding:9px 12px!important;border-radius:12px!important;
    border:1px solid transparent!important;background:transparent;
    color:#d0e7d8!important;cursor:pointer;
    transition:background .17s ease,border-color .17s ease,transform .17s ease;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover{
    background:#214b37!important;border-color:#376a49!important;transform:translateX(2px);
}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked){
    background:#e5f3da!important;border-color:#e5f3da!important;
    box-shadow:0 8px 18px rgba(0,0,0,.12);
}
[data-testid="stSidebar"] [role="radiogroup"] label div[data-testid="stMarkdownContainer"] p{
    color:#d8eee0!important;font-family:'DM Sans',sans-serif;
    font-size:.89rem!important;font-weight:700!important;
}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) div[data-testid="stMarkdownContainer"] p{
    color:#17482d!important;font-weight:900!important;
}
[data-testid="stSidebar"] [role="radiogroup"] input{accent-color:#9cdc8a!important}
[data-testid="stSidebar"] .stCaption p{color:#a8c8ad!important}
.cc-sidebar-brand{padding:10px 5px 17px;color:#fff;border-bottom:1px solid rgba(220,255,218,.13);margin-bottom:10px}
.cc-sidebar-brand .cc-brand-logo{display:inline-flex;align-items:center;justify-content:center;width:43px;height:43px;background:#d9f5b6;color:#153828;border-radius:13px;font-size:1.2rem;margin-bottom:14px}
.cc-sidebar-brand strong{display:block;font-family:'Manrope',sans-serif;font-weight:900;font-size:1.43rem;letter-spacing:-.07em;color:#f4fdef}
.cc-sidebar-brand small{display:block;font-size:.59rem;letter-spacing:.17em;text-transform:uppercase;color:#a5c7b2;margin-top:4px}
.cc-sidebar-kicker{font-size:.62rem;font-weight:900;letter-spacing:.17em;color:#91b99d;text-transform:uppercase;padding:4px 10px 9px}
.cc-rail-footer{margin-top:13px;border:1px solid rgba(212,248,200,.16);border-radius:15px;background:rgba(232,251,215,.065);padding:15px;color:#cde5d1}
.cc-rail-footer strong{font-size:.81rem;color:#e9f8df;display:block;margin-bottom:4px}
.cc-rail-footer p{font-size:.73rem;color:#afc7b8;line-height:1.6;margin:0}
.cc-rail-footer .cc-dot{display:inline-block;width:7px;height:7px;border-radius:50%;background:#a4e78b;margin-right:6px}
.cc-page-heading{display:flex;justify-content:space-between;gap:12px;align-items:center;flex-wrap:wrap;margin:8px 0 20px;padding:8px 0 11px;border-bottom:1px solid #dce8dc}
.cc-page-heading .cc-breadcrumb{font-size:.72rem;color:#6c8576;font-weight:800;text-transform:uppercase;letter-spacing:.12em}
.cc-page-heading .cc-breadcrumb span{color:#2e8052}
.cc-page-heading .cc-mode{border:1px solid #cfe5d0;background:#f7fff0;border-radius:100px;padding:8px 12px;font-size:.7rem;color:#316344;font-weight:800}
.cc-page-heading .cc-mode i{display:inline-block;background:#55ad6c;width:7px;height:7px;border-radius:50%;margin-right:6px}
.cc-home-kicker{font-size:.73rem;font-weight:900;letter-spacing:.16em;color:#4c8660;text-transform:uppercase;margin:23px 0 14px}
.cc-home-intro{max-width:740px;color:#617d6c;font-size:.88rem;margin:5px 0 15px}
.cc-launch{background:#fff;border:1px solid #dee9de;border-radius:18px;padding:22px 22px 16px;
    min-height:153px;box-shadow:0 7px 22px rgba(31,73,42,.045);
    transition:transform .2s,border-color .2s,box-shadow .2s}
.cc-launch:hover{transform:translateY(-4px);border-color:#9dc7a6;box-shadow:0 15px 29px rgba(24,80,48,.09)}
.cc-launch-kicker{display:flex;align-items:center;justify-content:space-between;color:#3d8558;font-size:.7rem;font-weight:900;letter-spacing:.12em}
.cc-launch-kicker b{display:grid;place-items:center;background:#e7f3dd;color:#1d6641;width:34px;height:34px;border-radius:10px;font-size:1.06rem;letter-spacing:normal}
.cc-launch h3{font-family:'Manrope',sans-serif;font-weight:900;color:#19392a;font-size:1.12rem;letter-spacing:-.04em;margin:12px 0 8px}
.cc-launch p{font-size:.76rem;line-height:1.62;color:#718578;margin:0}
.cc-launch-dark{background:linear-gradient(132deg,#1b4e36,#173b2b);border-color:#194a35}
.cc-launch-dark h3{color:#f5fff2}
.cc-launch-dark p{color:#bad8bf}
.cc-launch-dark .cc-launch-kicker{color:#d4f5b9}
.cc-launch-dark .cc-launch-kicker b{background:#32684a;color:#edffdf}
.cc-open-arrow{font-weight:900;color:#4b8559}
.cc-section-divider{border-top:1px solid #dbe8d9;margin:21px 0}
.cc-method-note{border-left:3px solid #9fc779;padding:10px 15px;background:#f3f9ec;color:#466652;border-radius:0 11px 11px 0;font-size:.77rem;line-height:1.6}
.cc-factline{display:flex;flex-wrap:wrap;gap:9px;margin:15px 0}
.cc-factline span{display:inline-block;padding:6px 11px;border:1px solid #d8e8d6;border-radius:99px;background:white;color:#49775b;font-size:.73rem;font-weight:800}
.cc-feature-label{color:#6c8a79;font-size:.68rem;text-transform:uppercase;letter-spacing:.13em;font-weight:900}
[data-testid="stSidebarCollapseButton"] button,[data-testid="stSidebarCollapsedControl"] button{color:#1f5d3e!important}
[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button{color:#e9fce9!important}
/* Homepage CTA nav buttons are real Streamlit controls, never inert HTML. */
[data-testid="stButton"] button[kind="secondary"]{transition:transform .16s ease,background .16s ease}
[data-testid="stButton"] button[kind="secondary"]:hover{transform:translateY(-1px)}
@media(min-width:1000px){[data-testid="stSidebar"]{min-width:280px!important;max-width:280px!important}}
@media(max-width:760px){.cc-launch{min-height:123px;padding:15px}.cc-sidebar-brand strong{font-size:1.25rem}.cc-page-heading{margin:4px 0 13px}.cc-home-kicker{margin:18px 0 9px}}
@media(prefers-reduced-motion:reduce){.cc-launch,[data-testid="stSidebar"] label{transition:none!important;transform:none!important}}
</style>
"""


def route_to(page):
    if page not in PAGES:
        raise ValueError(f"Unknown workspace: {page}")
    st.session_state["cc_page"] = page


def navigation():
    if st.session_state.get("cc_page") not in PAGES:
        st.session_state["cc_page"] = "Overview"
    with st.sidebar:
        st.markdown("""<div class="cc-sidebar-brand">
          <span class="cc-brand-logo" aria-hidden="true">✳</span>
          <strong>cropcast<span style="color:#bcf19b">.</span></strong>
          <small>Agricultural intelligence suite</small>
          </div><div class="cc-sidebar-kicker">Research workspace</div>""", unsafe_allow_html=True)
        st.radio(
            "Select workspace",
            options=PAGES,
            key="cc_page",
            format_func=lambda x: LABELS[x],
            label_visibility="collapsed",
        )
        st.markdown("""<div class="cc-rail-footer">
          <strong><span class="cc-dot"></span> Model B · online prediction</strong>
          <p>Model A research is available as recorded offline evaluation. No real-farm validation is claimed.</p>
        </div>""", unsafe_allow_html=True)
    return st.session_state["cc_page"]


def page_header(page):
    return (
        f'<div class="cc-page-heading"><div class="cc-breadcrumb">'
        f'CROPCAST / <span>{escape(page)}</span></div>'
        f'<div class="cc-mode"><i></i> Research prototype · Model B live</div></div>'
    )


def launch_card(kicker, title, description, icon, dark=False):
    dark_css = " cc-launch-dark" if dark else ""
    return (
        f'<div class="cc-launch{dark_css}">'
        f'<div class="cc-launch-kicker">{escape(kicker)}<b>{escape(icon)}</b></div>'
        f'<h3>{escape(title)}</h3><p>{escape(description)}</p></div>'
    )


def home_launchers():
    st.markdown('<div class="cc-home-kicker">Choose a workspace</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="cc-home-intro">Launch a dedicated tool. Each workspace has a clear '
        'purpose and is backed by the actual research project, not demo-only mock data.</div>',
        unsafe_allow_html=True,
    )
    modules = [
        ("01 / PREDICT", "Yield Predictor", "Run trusted Model B on eight farm conditions.", "◈", True),
        ("02 / COMPARE", "Crop Scenarios", "Compare all six crop outputs and explore sensitivity.", "◫", False),
        ("03 / RESEARCH", "Model A Research", "Examine the 1M-row A/B evaluation and harvest-duration data.", "◎", False),
        ("04 / BATCH", "Batch Studio", "Upload up to 50 scenarios; export actual model outputs.", "▤", False),
        ("05 / CONTEXT", "Weather Context", "Search a city and view a real five-day forecast.", "☼", False),
        ("06 / EVIDENCE", "Research & About", "Explore the model, test evidence and limitations.", "◉", False),
    ]
    for offset in range(0, len(modules), 3):
        columns = st.columns(3, gap="medium")
        for i, module in enumerate(modules[offset : offset + 3]):
            kicker, title, description, icon, dark = module
            with columns[i]:
                st.markdown(launch_card(kicker, title, description, icon, dark), unsafe_allow_html=True)
                st.button(
                    "Open " + title + "  ↗",
                    key="goto_" + title.replace(" ", "_").lower(),
                    use_container_width=True,
                    on_click=route_to,
                    args=(title,),
                    help=description,
                )
    st.markdown(
        '<div class="cc-method-note">Prediction is a model-generated scenario estimate, '
        'not a guarantee of yield, crop suitability or profit. Model A and B have both '
        'been evaluated on a random hold-out split, not independent farms or future seasons.</div>',
        unsafe_allow_html=True,
    )
