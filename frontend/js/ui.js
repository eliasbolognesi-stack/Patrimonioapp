/* Utilitários de interface --------------------------------------- */
const UI = {
  esc(str) {
    return String(str ?? "")
      .replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;").replaceAll("'", "&#39;");
  },

  money(v) {
    return (v ?? 0).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
  },

  date(iso) {
    if (!iso) return "—";
    const d = new Date(iso.length <= 10 ? iso + "T00:00:00" : iso);
    return d.toLocaleDateString("pt-BR");
  },

  dateTime(iso) {
    if (!iso) return "—";
    return new Date(iso).toLocaleString("pt-BR", {
      day: "2-digit", month: "2-digit", year: "numeric",
      hour: "2-digit", minute: "2-digit",
    });
  },

  toast(message, type = "info", ms = 3500) {
    const el = document.createElement("div");
    el.className = `toast toast-${type}`;
    el.textContent = message;
    document.getElementById("toast-container").appendChild(el);
    setTimeout(() => {
      el.style.transition = "opacity .3s";
      el.style.opacity = "0";
      setTimeout(() => el.remove(), 300);
    }, ms);
  },

  /* ---------- modal ---------- */
  modal({ title, body, footer, maxWidth }) {
    const backdrop = document.getElementById("modal-backdrop");
    const box = document.getElementById("modal-box");
    box.style.maxWidth = maxWidth || "560px";
    box.innerHTML = `
      <div class="modal-header">
        <h3>${UI.esc(title)}</h3>
        <button class="btn-icon" data-close title="Fechar">
          <svg viewBox="0 0 24 24"><path d="M19 6.41 17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
        </button>
      </div>
      <div class="modal-body">${body}</div>
      ${footer ? `<div class="modal-footer">${footer}</div>` : ""}
    `;
    backdrop.classList.remove("hidden");
    box.querySelector("[data-close]").onclick = UI.closeModal;
    backdrop.onclick = (e) => { if (e.target === backdrop) UI.closeModal(); };
    const first = box.querySelector("input, select, textarea");
    if (first) setTimeout(() => first.focus(), 60);
    return box;
  },

  closeModal() {
    document.getElementById("modal-backdrop").classList.add("hidden");
    document.getElementById("modal-box").innerHTML = "";
  },

  confirm(title, message, { confirmLabel = "Confirmar", danger = true } = {}) {
    return new Promise((resolve) => {
      const box = UI.modal({
        title,
        body: `<p style="color:var(--text-soft);line-height:1.55">${message}</p>`,
        footer: `
          <button class="btn btn-ghost" data-cancel>Cancelar</button>
          <button class="btn ${danger ? "btn-danger-soft" : "btn-primary"}" data-ok>${UI.esc(confirmLabel)}</button>
        `,
        maxWidth: "420px",
      });
      box.querySelector("[data-cancel]").onclick = () => { UI.closeModal(); resolve(false); };
      box.querySelector("[data-ok]").onclick = () => { UI.closeModal(); resolve(true); };
    });
  },

  /* ---------- badges ---------- */
  statusBadge(status) {
    const map = {
      ativo: ["Ativo", "green"],
      manutencao: ["Em manutenção", "amber"],
      baixado: ["Baixado", "red"],
      aberta: ["Aberta", "amber"],
      concluida: ["Concluída", "green"],
    };
    const [label, color] = map[status] || [status, "gray"];
    return `<span class="badge badge-${color}">${UI.esc(label)}</span>`;
  },

  estadoBadge(estado) {
    const map = {
      otimo: ["Ótimo", "green"],
      bom: ["Bom", "blue"],
      regular: ["Regular", "amber"],
      ruim: ["Ruim", "red"],
      inservivel: ["Inservível", "gray"],
    };
    const [label, color] = map[estado] || [estado, "gray"];
    return `<span class="badge badge-${color}">${UI.esc(label)}</span>`;
  },

  loading() {
    return `<div class="loading"><div class="spinner"></div>Carregando…</div>`;
  },

  empty(message) {
    return `<div class="empty-state"><div class="big">◌</div>${UI.esc(message)}</div>`;
  },

  options(list, selected, { placeholder = "Selecione…", value = "id", label = "nome" } = {}) {
    let html = `<option value="">${UI.esc(placeholder)}</option>`;
    for (const item of list) {
      const sel = String(item[value]) === String(selected ?? "") ? " selected" : "";
      html += `<option value="${item[value]}"${sel}>${UI.esc(item[label])}</option>`;
    }
    return html;
  },
};

const ESTADOS = [
  { id: "otimo", nome: "Ótimo" },
  { id: "bom", nome: "Bom" },
  { id: "regular", nome: "Regular" },
  { id: "ruim", nome: "Ruim" },
  { id: "inservivel", nome: "Inservível" },
];

const MOTIVOS_BAIXA = [
  { id: "inservivel", nome: "Inservível / obsoleto" },
  { id: "extravio", nome: "Extravio / perda" },
  { id: "doacao", nome: "Doação" },
  { id: "venda", nome: "Venda / leilão" },
  { id: "outro", nome: "Outro" },
];
