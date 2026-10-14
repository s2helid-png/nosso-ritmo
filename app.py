import calendar
import datetime as dt
import json
import os
import random
from zoneinfo import ZoneInfo

import requests
import streamlit as st

st.set_page_config(page_title="Nosso Ritmo a Dois", page_icon="🔥", layout="centered")

HOJE = dt.datetime.now(ZoneInfo("America/Sao_Paulo")).date()
AGORA = dt.datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%d/%m %H:%M")
ARQUIVO = "dados.json"

MESES = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho",
         "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
HUMORES = ["—", "😊 Feliz", "😌 Tranquilo(a)", "😴 Cansado(a)", "😢 Sensível",
           "😠 Irritado(a)", "😍 Apaixonado(a)"]
SINTOMAS = ["Cólica", "Dor de cabeça", "Inchaço", "Sono", "Desejo de doce",
            "Energia alta", "Dor nas costas"]
IDEIAS = [
    "O Xodó na Rede: noite de sofá, chá e conversa sem pressa (mesmo por vídeo).",
    "Abraço de Urso virtual: mandem um áudio de 1 minuto um para o outro.",
    "A Brisa da Manhã: bom-dia por vídeo bem cedinho, só pra ver o sorriso.",
    "Jantar juntos à distância: o mesmo prato, cada um na sua casa, em videochamada.",
    "Filme em sincronia: deem play juntos e comentem por mensagem.",
    "Carta de 3 coisas: cada um escreve 3 coisas que admira no outro.",
    "Playlist da semana: cada um adiciona 3 músicas que lembram o outro.",
    "Foto do dia: mandem uma foto de algo que lembrou o outro.",
    "Viagem dos sonhos: montem juntos o roteiro de uma viagem a dois.",
    "O Fogão Aceso: um elogio sincero por hora, durante o dia todo.",
]
PERGUNTAS = [
    "Qual foi o momento mais feliz que vivemos juntos?",
    "Qual lugar você gostaria de conhecer comigo?",
    "O que eu faço que mais te deixa sorrindo?",
    "Qual é o seu maior sonho para nós dois?",
    "O que você mais gosta no nosso dia a dia?",
    "Qual foi a primeira coisa que você notou em mim?",
    "Qual música é a cara do nosso casal?",
    "O que posso fazer para te ajudar mais esta semana?",
    "Qual lembrança nossa faz seu coração aquecer?",
    "Como você imagina a gente daqui a 10 anos?",
]

FASES = {
    "men": ("Menstruação ❄️ (Inverno)",
            "Fogão descansando e se limpando. Brasa baixa.",
            "Leve uma bolsa de água quente, um chá ou chocolate. Zero cobrança, só acolhimento!",
            "Permita-se desacelerar. O corpo está em renovação."),
    "fol": ("Fase Folicular 🌱 (Primavera)",
            "Lenha seca e pronta para acender com facilidade!",
            "Hora de ser romântico e elogiar. Convide para um passeio ou um café a dois.",
            "Aproveite a boa energia para conversas e projetos gostosos a dois."),
    "fer": ("Período fértil ☀️ (Verão)",
            "🔥 Brasa viva! Energia e conexão no pico.",
            "Sem pressa de micro-ondas: curta o preparo, elogie e crie clima.",
            "Momento de alta conexão e sintonia. Aproveitem!"),
    "lut": ("Fase Lútea / TPM 🍂 (Outono)",
            "Vento frio lá fora. Lenha mansa e muita paciência.",
            "Lave a louça sem pedir, dê um abraço demorado e ouça sem tentar resolver tudo com lógica.",
            "Se sentir irritação ou choro fácil, avise com carinho: 'Amor, é só o hormônio hoje!'"),
}

PADRAO = {
    "nomes": {"ele": "Helton", "ela": "Isabela"},
    "ciclo": {"inicio": None, "duracao": 28, "menstruacao": 5, "modo": "Precaução"},
    "registros": {},
    "carinho": [],
    "recados": [],
    "ideia": "",
    "quiz": {"pergunta": "", "respostas": {}},
}

st.markdown(
    """
<style>
.cal{width:100%;border-collapse:separate;border-spacing:3px;table-layout:fixed;text-align:center}
.cal th{font-size:12px;opacity:.7;font-weight:600}
.cal td{height:54px;border-radius:10px;font-size:15px;position:relative;
        background:rgba(128,128,128,.13);vertical-align:top;padding:3px 0}
.cal td small{display:block;font-size:10px;opacity:.6}
.cal td.out{background:none}
.cal td.men{background:#c4607f;color:#fff}
.cal td.fer::after{content:"";position:absolute;bottom:5px;left:50%;margin-left:-4px;
        width:8px;height:8px;border-radius:50%;background:#ec4899}
.cal td.ov{background:#7c3aed;color:#fff}
.cal td.hoje{background:#a78bfa;color:#111}
.cal td.prox{box-shadow:inset 0 -5px 0 #f9a8a8}
.cal td.sel{outline:2px solid #fbbf24}
.cal .m{position:absolute;right:2px;top:1px;font-size:9px}
.cal.mini td{height:34px;font-size:12px}
.cal.mini td small, .cal.mini .m{display:none}
.stButton>button{border-radius:12px;font-weight:bold}
</style>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------- dados
def _supabase():
    try:
        return st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]
    except Exception:
        return None


def carregar():
    dados = json.loads(json.dumps(PADRAO))
    st.session_state["carga_ok"] = True
    sb = _supabase()
    try:
        salvo = {}
        if sb:
            url, key = sb
            r = requests.get(
                f"{url}/rest/v1/dados",
                params={"id": "eq.1", "select": "conteudo"},
                headers={"apikey": key, "Authorization": f"Bearer {key}"},
                timeout=10,
            )
            r.raise_for_status()
            linhas = r.json()
            if linhas:
                salvo = linhas[0]["conteudo"]
        elif os.path.exists(ARQUIVO):
            with open(ARQUIVO, encoding="utf-8") as f:
                salvo = json.load(f)
        for k, v in salvo.items():
            dados[k] = v
        for k, v in PADRAO["ciclo"].items():
            dados["ciclo"].setdefault(k, v)
    except Exception as e:
        st.session_state["carga_ok"] = False
        st.warning(f"Não consegui carregar os dados agora: {e}")
    return dados


def salvar(d):
    if not st.session_state.get("carga_ok", True):
        st.error("Não salvei para não apagar nada. Toque em Atualizar e tente de novo.")
        return
    sb = _supabase()
    try:
        if sb:
            url, key = sb
            r = requests.post(
                f"{url}/rest/v1/dados",
                headers={
                    "apikey": key,
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                    "Prefer": "resolution=merge-duplicates",
                },
                json={"id": 1, "conteudo": d},
                timeout=10,
            )
            r.raise_for_status()
        else:
            with open(ARQUIVO, "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False)
    except Exception as e:
        st.error(f"Não consegui salvar: {e}")


# ---------------------------------------------------------------- ciclo
def info_dia(dia, c):
    ini = dt.date.fromisoformat(c["inicio"])
    dur, men = c["duracao"], c["menstruacao"]
    n = (dia - ini).days % dur
    nov = dur - 14  # ovulação ~14 dias antes da próxima menstruação
    if n < men:
        fase = "men"
    elif nov - 5 <= n <= nov + 1:
        fase = "fer"
    elif n < nov - 5:
        fase = "fol"
    else:
        fase = "lut"
    return {"fase": fase, "ov": n == nov, "dia": n + 1, "prox": n == 0 and dia > ini}


def calendario_html(ano, mes, c, sel, regs, carinho, mini=False):
    cab = "".join(f"<th>{x}</th>" for x in "STQQSSD")
    corpo = ""
    for semana in calendar.Calendar(0).monthdatescalendar(ano, mes):
        linha = ""
        for dia in semana:
            if dia.month != mes:
                linha += "<td class='out'></td>"
                continue
            inf = info_dia(dia, c)
            cls = "ov" if inf["ov"] else inf["fase"]
            if inf["prox"]:
                cls += " prox"
            if dia == HOJE:
                cls += " hoje"
            if dia == sel:
                cls += " sel"
            iso = dia.isoformat()
            marca = ("💗" if iso in carinho else "") + ("📝" if iso in regs else "")
            linha += (f"<td class='{cls}'>{dia.day}<small>{inf['dia']}</small>"
                      f"<span class='m'>{marca}</span></td>")
        corpo += f"<tr>{linha}</tr>"
    extra = " mini" if mini else ""
    return f"<table class='cal{extra}'><tr>{cab}</tr>{corpo}</table>"


def calcular_ofensiva(datas):
    s = set(datas)
    dia = HOJE if HOJE.isoformat() in s else HOJE - dt.timedelta(days=1)
    n = 0
    while dia.isoformat() in s:
        n += 1
        dia -= dt.timedelta(days=1)
    return n


# ---------------------------------------------------------------- app
d = carregar()
nomes = d["nomes"]
c = d["ciclo"]

st.markdown("<h2 style='text-align:center'>🔥 Nosso Ritmo a Dois 🐘🦋</h2>", unsafe_allow_html=True)
quem = st.radio("Quem está usando?", ["ele", "ela"], format_func=lambda k: nomes[k],
                horizontal=True, key="quem")
outro = "ela" if quem == "ele" else "ele"
if st.button("🔄 Atualizar"):
    st.rerun()

aba_cal, aba_rec, aba_of, aba_div, aba_aj = st.tabs(
    ["📅 Calendário", "💌 Recados", "🏆 Ofensiva", "🎲 Ideias e Quiz", "⚙️ Ajustes"]
)

# ------------------------------------------------------------ calendário
with aba_cal:
    if not c["inicio"]:
        st.info("Vá na aba ⚙️ Ajustes e informe o primeiro dia da última menstruação.")
    else:
        sel = st.date_input("Dia", value=HOJE, format="DD/MM/YYYY", key="dia_sel")
        visao = st.radio("Visão", ["Mês", "Ano"], horizontal=True, label_visibility="collapsed")
        if visao == "Mês":
            st.markdown(f"**{MESES[sel.month - 1]} de {sel.year}**")
            st.markdown(calendario_html(sel.year, sel.month, c, sel, d["registros"], d["carinho"]),
                        unsafe_allow_html=True)
        else:
            for m in range(1, 13):
                with st.expander(MESES[m - 1], expanded=(m == sel.month)):
                    st.markdown(calendario_html(sel.year, m, c, sel, d["registros"], d["carinho"], True),
                                unsafe_allow_html=True)
        st.caption("🟥 menstruação · ● período fértil · 🟣 ovulação · 🟪 hoje · "
                   "barra salmão = próxima menstruação · número pequeno = dia do ciclo")

        inf = info_dia(sel, c)
        nome_fase, status, dica_ele, dica_ela = FASES[inf["fase"]]
        st.subheader(f"{sel:%d/%m} · Dia {inf['dia']} do ciclo")
        st.write(f"**{nome_fase}**: {status}")
        if inf["ov"]:
            st.write("💜 Provável dia da ovulação (estimativa).")
        if inf["fase"] == "fer":
            if c["modo"] == "Precaução":
                st.warning("Dias de maior fertilidade. É só uma estimativa e não é método contraceptivo.")
            else:
                st.success("Janela fértil 💛 Boa hora para tentar! (estimativa)")
        st.success(f"💡 Para {nomes['ele']}: {dica_ele}")
        st.info(f"🌸 Para {nomes['ela']}: {dica_ela}")

        st.markdown("#### Meu registro do dia")
        iso = sel.isoformat()
        reg = d["registros"].get(iso, {}).get(quem, {})
        with st.form("registro"):
            humor = st.selectbox("Como estou", HUMORES,
                                 index=HUMORES.index(reg["humor"]) if reg.get("humor") in HUMORES else 0)
            sintomas = st.multiselect("Sintomas", SINTOMAS, default=reg.get("sintomas", []))
            nota = st.text_area("Anotação", value=reg.get("nota", ""))
            if st.form_submit_button("Salvar registro"):
                d["registros"].setdefault(iso, {})[quem] = {"humor": humor, "sintomas": sintomas, "nota": nota}
                salvar(d)
                st.rerun()

        reg_outro = d["registros"].get(iso, {}).get(outro)
        if reg_outro:
            st.markdown(f"**Registro de {nomes[outro]}:** {reg_outro.get('humor', '—')}")
            if reg_outro.get("sintomas"):
                st.write("Sintomas: " + ", ".join(reg_outro["sintomas"]))
            if reg_outro.get("nota"):
                st.write(f"📝 {reg_outro['nota']}")

# ------------------------------------------------------------ recados
with aba_rec:
    with st.form("recado", clear_on_submit=True):
        texto = st.text_input(f"Recado para {nomes[outro]}")
        if st.form_submit_button("💌 Enviar") and texto.strip():
            d["recados"].append({"de": quem, "texto": texto.strip(), "quando": AGORA})
            salvar(d)
            st.rerun()
    if not d["recados"]:
        st.caption("Nenhum recado ainda. Que tal começar com um 'bom dia'? ☀️")
    for r in reversed(d["recados"][-15:]):
        st.markdown(f"**{nomes[r['de']]}** · {r['quando']}")
        st.write(r["texto"])
        st.divider()

# ------------------------------------------------------------ ofensiva
with aba_of:
    ofensiva = calcular_ofensiva(d["carinho"])
    col1, col2 = st.columns(2)
    col1.metric("Dias seguidos", f"{ofensiva} 🔥")
    col2.metric("Total de momentos", len(d["carinho"]))
    st.info("Perdeu um dia por cansaço? Sem problema: dá para repor ontem com carinho dobrado!")
    if HOJE.isoformat() not in d["carinho"]:
        if st.button("💗 Registrar momento de carinho de hoje"):
            d["carinho"].append(HOJE.isoformat())
            salvar(d)
            st.balloons()
            st.rerun()
    else:
        st.success("Hoje já foi registrado! 🎉")
    ontem = (HOJE - dt.timedelta(days=1)).isoformat()
    if ontem not in d["carinho"]:
        if st.button("↩️ Repor ontem"):
            d["carinho"].append(ontem)
            salvar(d)
            st.rerun()

# ------------------------------------------------------------ ideias e quiz
with aba_div:
    st.markdown("### 🎲 Roleta de ideias")
    if st.button("Sortear ideia da semana"):
        d["ideia"] = random.choice(IDEIAS)
        salvar(d)
        st.rerun()
    if d["ideia"]:
        st.success(d["ideia"])

    st.markdown("### ❓ Quiz do casal")
    q = d["quiz"]
    if st.button("🎲 Nova pergunta"):
        q["pergunta"] = random.choice(PERGUNTAS)
        q["respostas"] = {}
        salvar(d)
        st.rerun()
    if q["pergunta"]:
        st.markdown(f"**{q['pergunta']}**")
        resp = q["respostas"]
        if quem not in resp:
            txt = st.text_area("Sua resposta", key=f"resp_{q['pergunta']}_{quem}")
            if st.button("Enviar resposta") and txt.strip():
                resp[quem] = txt.strip()
                salvar(d)
                st.rerun()
        else:
            st.caption("Você já respondeu ✅")
        if len(resp) == 2:
            for k in ("ele", "ela"):
                st.write(f"**{nomes[k]}:** {resp[k]}")
        else:
            st.caption("As respostas aparecem quando os dois responderem 😉")

# ------------------------------------------------------------ ajustes
with aba_aj:
    with st.form("ajustes"):
        n_ele = st.text_input("Nome dele", nomes["ele"])
        n_ela = st.text_input("Nome dela", nomes["ela"])
        ini_padrao = dt.date.fromisoformat(c["inicio"]) if c["inicio"] else HOJE
        ini = st.date_input("Primeiro dia da última menstruação", ini_padrao, format="DD/MM/YYYY")
        dur = st.slider("Duração do ciclo (dias)", 21, 40, c["duracao"])
        men = st.slider("Dias de menstruação", 2, 8, c["menstruacao"])
        modo = st.radio("Objetivo", ["Precaução", "Tentantes"],
                        index=0 if c["modo"] == "Precaução" else 1, horizontal=True)
        if st.form_submit_button("Salvar ajustes"):
            d["nomes"] = {"ele": n_ele.strip() or "Ele", "ela": n_ela.strip() or "Ela"}
            d["ciclo"] = {"inicio": ini.isoformat(), "duracao": dur, "menstruacao": men, "modo": modo}
            salvar(d)
            st.rerun()
    if st.button("🩸 A menstruação começou hoje"):
        c["inicio"] = HOJE.isoformat()
        salvar(d)
        st.rerun()

st.caption("Previsões são estimativas e não substituem orientação médica nem servem como método contraceptivo. ❤️")
