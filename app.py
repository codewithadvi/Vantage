import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Vantage", layout="wide", page_icon="◆")

# ============================================================
# DESIGN SYSTEM — custom CSS injected into Streamlit
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Inter:wght@400;500;600&display=swap');

:root {
    --bg: #0E0F11;
    --bg-elevated: #17191C;
    --border: #2A2D32;
    --text: #EDEAE3;
    --text-muted: #8C8F96;
    --accent: #D4A24E;
    --accent-dim: #8A6D38;
    --stealth: #C77B4F;
    --founder: #6FA88A;
    --employed: #6B7280;
}

.stApp { background-color: var(--bg); color: var(--text); }
[data-testid="stSidebar"] { background-color: var(--bg-elevated); border-right: 1px solid var(--border); }
[data-testid="stSidebar"] * { color: var(--text) !important; }

h1, h2, h3 { font-family: 'Fraunces', serif !important; font-weight: 500 !important; letter-spacing: -0.01em; }
body, p, div, span, label { font-family: 'Inter', sans-serif; }

.ss-brand {
    font-family: 'Fraunces', serif;
    font-size: 1.6rem;
    font-weight: 600;
    color: var(--text);
    letter-spacing: -0.02em;
    margin-bottom: 0;
}
.ss-brand-tag {
    font-family: 'Inter', sans-serif;
    font-size: 0.72rem;
    color: var(--text-muted);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-top: -4px;
}

.ss-card {
    background: var(--bg-elevated);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent-dim);
    border-radius: 4px;
    padding: 18px 22px;
    margin-bottom: 14px;
}
.ss-card.high-conf { border-left: 3px solid var(--accent); }

.ss-name {
    font-family: 'Fraunces', serif;
    font-size: 1.15rem;
    font-weight: 500;
    color: var(--text);
    margin-bottom: 2px;
}
.ss-transition {
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    color: var(--text-muted);
    margin-bottom: 8px;
}
.ss-summary {
    font-size: 0.92rem;
    color: var(--text);
    line-height: 1.5;
    margin-bottom: 10px;
}

.ss-badge {
    display: inline-block;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    padding: 3px 9px;
    border-radius: 3px;
    margin-right: 6px;
}
.badge-stealth { background: rgba(199,123,79,0.15); color: var(--stealth); border: 1px solid rgba(199,123,79,0.3); }
.badge-founder { background: rgba(111,168,138,0.15); color: var(--founder); border: 1px solid rgba(111,168,138,0.3); }
.badge-employed { background: rgba(107,114,128,0.15); color: #9CA3AF; border: 1px solid rgba(107,114,128,0.3); }
.badge-tag { background: rgba(212,162,78,0.1); color: var(--accent); border: 1px solid rgba(212,162,78,0.25); }

.ss-conf-wrap { display: flex; align-items: center; gap: 8px; }
.ss-conf-bar-bg { width: 80px; height: 5px; background: var(--border); border-radius: 3px; overflow: hidden; }
.ss-conf-bar-fill { height: 100%; background: var(--accent); }
.ss-conf-label { font-size: 0.78rem; color: var(--text-muted); font-variant-numeric: tabular-nums; }

.ss-meta { font-size: 0.78rem; color: var(--text-muted); margin-top: 6px; }
.ss-divider { border: none; border-top: 1px solid var(--border); margin: 28px 0; }

.ss-stat-box {
    background: var(--bg-elevated);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 16px 20px;
}
.ss-stat-num { font-family: 'Fraunces', serif; font-size: 1.9rem; color: var(--accent); }
.ss-stat-label { font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.06em; }

.ss-timeline-item { padding-left: 18px; border-left: 2px solid var(--border); padding-bottom: 18px; position: relative; }
.ss-timeline-item.current { border-left: 2px solid var(--accent); }
.ss-timeline-dot { width: 9px; height: 9px; border-radius: 50%; background: var(--text-muted); position: absolute; left: -5.5px; top: 4px; }
.ss-timeline-dot.current { background: var(--accent); }

[data-testid="stMetricValue"] { font-family: 'Fraunces', serif; color: var(--accent); }
.stButton button {
    background: transparent; border: 1px solid var(--accent-dim); color: var(--accent);
    border-radius: 4px; font-size: 0.82rem;
}
.stButton button:hover { background: rgba(212,162,78,0.1); border-color: var(--accent); color: var(--accent); }
</style>
""", unsafe_allow_html=True)


# ============================================================
# DATA LAYER
# ============================================================
@st.cache_resource
def get_client():
    return create_client(st.secrets["supabase_url"], st.secrets["supabase_key"])

supabase = get_client()

@st.cache_data(ttl=60)
def load_alerts():
    resp = (supabase.table("alerts")
            .select("*, people(full_name, linkedin_url, is_repeat_founder, is_senior_operator, location, headline)")
            .order("detected_at", desc=True).execute())
    return resp.data

@st.cache_data(ttl=60)
def load_people():
    return supabase.table("people").select("*").execute().data

@st.cache_data(ttl=60)
def load_experience(person_id=None):
    q = supabase.table("experience").select("*, companies(name, sector)")
    if person_id:
        q = q.eq("person_id", person_id)
    return q.order("start_date").execute().data

@st.cache_data(ttl=60)
def load_companies():
    return supabase.table("companies").select("*").execute().data


def status_badge(status):
    cls = {"stealth": "badge-stealth", "founder": "badge-founder", "employed": "badge-employed"}.get(status, "badge-employed")
    return f'<span class="ss-badge {cls}">{status}</span>'

def confidence_bar(score):
    score = score or 50
    return f'''<div class="ss-conf-wrap">
        <div class="ss-conf-bar-bg"><div class="ss-conf-bar-fill" style="width:{score}%"></div></div>
        <span class="ss-conf-label">{score}% confidence</span>
    </div>'''


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown('<div class="ss-brand">◆ Vantage</div>', unsafe_allow_html=True)
    st.markdown('<div class="ss-brand-tag">Founder signal tracking — POC</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    view = st.radio("Navigate", ["Alert Feed", "Tracked Profiles", "Insights", "Scan Settings"], label_visibility="collapsed")
    st.markdown("<hr class='ss-divider'>", unsafe_allow_html=True)
    st.caption("Running on dummy data — no live LinkedIn connection in this prototype.")


# ============================================================
# VIEW: ALERT FEED
# ============================================================
if view == "Alert Feed":
    st.markdown('<div class="ss-brand">Alert Feed</div>', unsafe_allow_html=True)
    st.caption("Status changes detected across tracked profiles, ranked by confidence")

    alerts = load_alerts()

    if not alerts:
        st.info("No alerts yet.")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            min_conf = st.slider("Minimum confidence", 0, 100, 0, step=5)
        with col2:
            status_opts = sorted(set(a["new_status"] for a in alerts))
            status_pick = st.multiselect("Status type", status_opts, default=status_opts)
        with col3:
            sort_by = st.selectbox("Sort by", ["Most recent", "Highest confidence"])

        filtered = [a for a in alerts if (a.get("confidence_score") or 0) >= min_conf and a["new_status"] in status_pick]
        if sort_by == "Highest confidence":
            filtered.sort(key=lambda a: a.get("confidence_score") or 0, reverse=True)

        st.markdown(f"**{len(filtered)}** alerts match your filters")
        st.markdown("<br>", unsafe_allow_html=True)

        for a in filtered:
            person = a.get("people", {}) or {}
            conf = a.get("confidence_score") or 50
            card_cls = "high-conf" if conf >= 80 else ""
            tags = []
            if person.get("is_repeat_founder"):
                tags.append('<span class="ss-badge badge-tag">repeat founder</span>')
            if person.get("is_senior_operator"):
                tags.append('<span class="ss-badge badge-tag">senior operator</span>')

            detected = a.get("detected_at", "")[:10]
            reviewed_txt = " · reviewed" if a.get("reviewed") else ""

            st.markdown(f'''
            <div class="ss-card {card_cls}">
                <div class="ss-name">{person.get("full_name","Unknown")}</div>
                <div class="ss-transition">{a["old_status"]} → {status_badge(a["new_status"])} &nbsp;·&nbsp; {person.get("location","")}</div>
                <div class="ss-summary">{a.get("summary","")}</div>
                {''.join(tags)}
                <div class="ss-meta">{confidence_bar(conf)}<br>Detected {detected}{reviewed_txt}</div>
            </div>
            ''', unsafe_allow_html=True)


# ============================================================
# VIEW: TRACKED PROFILES
# ============================================================
elif view == "Tracked Profiles":
    st.markdown('<div class="ss-brand">Tracked Profiles</div>', unsafe_allow_html=True)
    st.caption("All profiles currently being monitored")

    people = load_people()
    if not people:
        st.info("No profiles found.")
    else:
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            search = st.text_input("Search by name or headline", placeholder="e.g. Razorpay, founder, stealth")
        with c2:
            status_filter = st.multiselect("Status", ["employed", "stealth", "founder"], default=["employed", "stealth", "founder"])
        with c3:
            only_senior = st.checkbox("Senior operators only")

        df = pd.DataFrame(people)
        if search:
            mask = df["full_name"].str.contains(search, case=False, na=False) | df["headline"].fillna("").str.contains(search, case=False, na=False)
            df = df[mask]
        df = df[df["current_status"].isin(status_filter)]
        if only_senior:
            df = df[df["is_senior_operator"] == True]

        st.markdown(f"**{len(df)}** profiles")
        st.markdown("<br>", unsafe_allow_html=True)

        cols = st.columns(3)
        for i, (_, row) in enumerate(df.iterrows()):
            with cols[i % 3]:
                tags = []
                if row.get("is_repeat_founder"):
                    tags.append('<span class="ss-badge badge-tag">repeat founder</span>')
                if row.get("is_senior_operator"):
                    tags.append('<span class="ss-badge badge-tag">senior op</span>')
                st.markdown(f'''
                <div class="ss-card">
                    <div class="ss-name">{row["full_name"]}</div>
                    <div class="ss-transition">{row.get("headline","")}</div>
                    {status_badge(row["current_status"])}
                    {''.join(tags)}
                    <div class="ss-meta">{row.get("location","")} · {row.get("years_experience","?")} yrs exp</div>
                </div>
                ''', unsafe_allow_html=True)
                if st.button("View profile →", key=f"view_{row['id']}"):
                    st.session_state["selected_person"] = row["id"]
                    st.session_state["nav_override"] = "detail"

    if st.session_state.get("nav_override") == "detail":
        pid = st.session_state["selected_person"]
        person = next((p for p in people if p["id"] == pid), None)
        exp = load_experience(pid)

        st.markdown("<hr class='ss-divider'>", unsafe_allow_html=True)
        st.markdown(f'<div class="ss-brand">{person["full_name"]}</div>', unsafe_allow_html=True)
        st.caption(f'{person.get("headline","")} · {person.get("location","")}')
        st.markdown(f'{status_badge(person["current_status"])}', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("**Career timeline**")
        exp_sorted = sorted(exp, key=lambda e: e.get("start_date") or "", reverse=True)
        for e in exp_sorted:
            company = (e.get("companies") or {}).get("name", "Unknown")
            current_cls = "current" if e.get("is_current") else ""
            end = e.get("end_date") or "Present"
            st.markdown(f'''
            <div class="ss-timeline-item {current_cls}">
                <div class="ss-timeline-dot {current_cls}"></div>
                <strong>{e.get("role_title","")}</strong> at {company}<br>
                <span class="ss-meta">{e.get("start_date","")} → {end}</span>
            </div>
            ''', unsafe_allow_html=True)

        if st.button("← Back to all profiles"):
            st.session_state["nav_override"] = None
            st.rerun()


# ============================================================
# VIEW: INSIGHTS (charts)
# ============================================================
elif view == "Insights":
    st.markdown('<div class="ss-brand">Insights</div>', unsafe_allow_html=True)
    st.caption("Patterns across tracked profiles and detected alerts")

    alerts = load_alerts()
    people = load_people()
    experience = load_experience()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="ss-stat-box"><div class="ss-stat-num">{len(people)}</div><div class="ss-stat-label">Tracked profiles</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="ss-stat-box"><div class="ss-stat-num">{len(alerts)}</div><div class="ss-stat-label">Total alerts</div></div>', unsafe_allow_html=True)
    with col3:
        repeat = sum(1 for p in people if p.get("is_repeat_founder"))
        st.markdown(f'<div class="ss-stat-box"><div class="ss-stat-num">{repeat}</div><div class="ss-stat-label">Repeat founders</div></div>', unsafe_allow_html=True)
    with col4:
        avg_conf = round(sum(a.get("confidence_score") or 0 for a in alerts) / max(len(alerts), 1))
        st.markdown(f'<div class="ss-stat-box"><div class="ss-stat-num">{avg_conf}%</div><div class="ss-stat-label">Avg. confidence</div></div>', unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Alerts over time**")
        if alerts:
            adf = pd.DataFrame(alerts)
            adf["date"] = pd.to_datetime(adf["detected_at"]).dt.date
            daily = adf.groupby("date").size().reset_index(name="count")
            fig = px.bar(daily, x="date", y="count")
            fig.update_traces(marker_color="#D4A24E")
            fig.update_layout(plot_bgcolor="#0E0F11", paper_bgcolor="#0E0F11", font_color="#EDEAE3",
                               margin=dict(l=10, r=10, t=10, b=10), height=300)
            st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("**Status breakdown**")
        if people:
            pdf = pd.DataFrame(people)
            counts = pdf["current_status"].value_counts().reset_index()
            counts.columns = ["status", "count"]
            colors = {"employed": "#6B7280", "stealth": "#C77B4F", "founder": "#6FA88A"}
            fig2 = px.pie(counts, names="status", values="count", color="status", color_discrete_map=colors, hole=0.55)
            fig2.update_layout(plot_bgcolor="#0E0F11", paper_bgcolor="#0E0F11", font_color="#EDEAE3",
                                margin=dict(l=10, r=10, t=10, b=10), height=300)
            st.plotly_chart(fig2, use_container_width=True)

    st.markdown("**Top source companies (where tracked people came from)**")
    if experience:
        edf = pd.DataFrame(experience)
        edf["company_name"] = edf["companies"].apply(lambda c: (c or {}).get("name", "Unknown"))
        top_companies = edf["company_name"].value_counts().head(8).reset_index()
        top_companies.columns = ["company", "people_count"]
        fig3 = px.bar(top_companies, x="people_count", y="company", orientation="h")
        fig3.update_traces(marker_color="#D4A24E")
        fig3.update_layout(plot_bgcolor="#0E0F11", paper_bgcolor="#0E0F11", font_color="#EDEAE3",
                            margin=dict(l=10, r=10, t=10, b=10), height=350,
                            yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig3, use_container_width=True)


# ============================================================
# VIEW: SCAN SETTINGS
# ============================================================
elif view == "Scan Settings":
    st.markdown('<div class="ss-brand">Scan Settings</div>', unsafe_allow_html=True)
    st.caption("Define what signals you want to be alerted on")

    prefs = supabase.table("signal_preferences").select("*").execute().data

    st.markdown("**Saved searches**")
    for p in (prefs or []):
        st.markdown(f'''
        <div class="ss-card">
            <div class="ss-name">{p["label"]}</div>
            <div class="ss-meta">Alerting on: {p.get("target_status","any")}</div>
        </div>
        ''', unsafe_allow_html=True)

    st.markdown("<hr class='ss-divider'>", unsafe_allow_html=True)
    st.markdown("**Create a new search**")
    st.caption("UI demo only — not yet wired to live scanning")

    companies = load_companies()
    company_names = [c["name"] for c in companies] if companies else []

    new_label = st.text_input("Search name", placeholder="e.g. Ex-fintech operators going stealth")
    target_companies = st.multiselect("Track people who previously worked at", company_names)
    target_status = st.selectbox("Alert me when status changes to", ["stealth", "founder", "employed"])
    min_years = st.slider("Minimum years of experience", 0, 20, 5)
    freq = st.selectbox("Scan frequency", ["Daily", "Every 3 days", "Weekly"])

    if st.button("Save search"):
        st.success(f"Would save '{new_label}' — watching {len(target_companies)} companies for '{target_status}' status, scanning {freq.lower()}.")
        st.caption("(Not yet connected to live scanning — this is a UI preview of the feature)")