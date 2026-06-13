/* Páginas da aplicação ------------------------------------------- */
const Pages = {};

/* helper: define ações do topo da página */
function setTopbar(html) {
  document.getElementById("topbar-actions").innerHTML = html || "";
}

/* ============================ DASHBOARD ============================ */
Pages.dashboard = async function (el) {
  setTopbar("");
  el.innerHTML = UI.loading();
  const d = await API.get("/dashboard");

  const estadoCores = {
    otimo: "#22c55e", bom: "#3b82f6", regular: "#f59e0b",
    ruim: "#ef4444", inservivel: "#82828e",
  };
  const estadoLabels = {
    otimo: "Ótimo", bom: "Bom", regular: "Regular",
    ruim: "Ruim", inservivel: "Inservível",
  };

  /* donut por estado de conservação */
  const entries = Object.entries(d.por_estado);
  const totalEstado = entries.reduce((s, [, v]) => s + v, 0) || 1;
  let offset = 25; /* começa no topo */
  const circles = entries.map(([estado, qtd]) => {
    const frac = (qtd / totalEstado) * 100;
    const c = `<circle r="15.915" cx="21" cy="21" fill="none" stroke="${estadoCores[estado] || "#555"}"
      stroke-width="5" stroke-dasharray="${frac} ${100 - frac}" stroke-dashoffset="${offset}"></circle>`;
    offset -= frac;
    return c;
  }).join("");
  const legend = entries.map(([estado, qtd]) => `
    <div class="leg">
      <span class="dot" style="background:${estadoCores[estado] || "#555"}"></span>
      ${estadoLabels[estado] || estado} <b>${qtd}</b>
    </div>`).join("") || `<div class="leg">Nenhum bem cadastrado</div>`;

  const bars = (list) => {
    const max = Math.max(...list.map(i => i.total), 1);
    return list.slice(0, 8).map(i => `
      <div class="bar-row">
        <div class="bar-head"><span>${UI.esc(i.nome)}</span><span>${i.total} · ${UI.money(i.valor)}</span></div>
        <div class="bar-track"><div class="bar-fill" style="width:${(i.total / max) * 100}%"></div></div>
      </div>`).join("") || UI.empty("Sem dados ainda");
  };

  el.innerHTML = `
    <div class="stats-grid">
      <div class="stat-card" style="--accent:#dc2626">
        <div class="stat-label">Total de Bens</div>
        <div class="stat-value">${d.total_bens}</div>
        <div class="stat-sub">${d.bens_ativos} ativos</div>
      </div>
      <div class="stat-card" style="--accent:#22c55e">
        <div class="stat-label">Valor do Patrimônio</div>
        <div class="stat-value">${UI.money(d.valor_total)}</div>
        <div class="stat-sub">bens não baixados</div>
      </div>
      <div class="stat-card" style="--accent:#f59e0b">
        <div class="stat-label">Em Manutenção</div>
        <div class="stat-value">${d.em_manutencao}</div>
        <div class="stat-sub">${UI.money(d.custo_manutencoes)} em custos acumulados</div>
      </div>
      <div class="stat-card" style="--accent:#82828e">
        <div class="stat-label">Baixados</div>
        <div class="stat-value">${d.baixados}</div>
        <div class="stat-sub">retirados do acervo</div>
      </div>
    </div>

    <div class="dash-grid">
      <div>
        <div class="card">
          <div class="card-title">Bens por Setor</div>
          ${bars(d.por_setor)}
        </div>
        <div class="card">
          <div class="card-title">Bens por Categoria</div>
          ${bars(d.por_categoria)}
        </div>
      </div>
      <div>
        <div class="card">
          <div class="card-title">Estado de Conservação</div>
          <div class="donut-wrap">
            <svg width="150" height="150" viewBox="0 0 42 42" style="transform:rotate(0deg)">
              <circle r="15.915" cx="21" cy="21" fill="none" stroke="var(--surface-3)" stroke-width="5"></circle>
              ${circles}
              <text x="21" y="20" text-anchor="middle" fill="var(--text)" font-size="7" font-weight="700">${totalEstado === 1 && !entries.length ? 0 : entries.reduce((s, [, v]) => s + v, 0)}</text>
              <text x="21" y="27" text-anchor="middle" fill="var(--muted)" font-size="3.4">EM USO</text>
            </svg>
            <div class="donut-legend">${legend}</div>
          </div>
        </div>
        <div class="card">
          <div class="card-title">Últimas Movimentações</div>
          ${d.ultimas_movimentacoes.length ? `
            <table>
              <tbody>
                ${d.ultimas_movimentacoes.map(m => `
                  <tr>
                    <td class="td-strong" style="padding:9px 6px">${UI.esc(m.bem)}</td>
                    <td style="padding:9px 6px;white-space:nowrap">${UI.esc(m.origem)} → ${UI.esc(m.destino)}</td>
                    <td style="padding:9px 6px;white-space:nowrap;color:var(--muted)">${UI.date(m.data)}</td>
                  </tr>`).join("")}
              </tbody>
            </table>` : UI.empty("Nenhuma movimentação registrada")}
        </div>
      </div>
    </div>
  `;
};

/* ============================ BENS ============================ */
const bensState = { q: "", categoria_id: "", setor_id: "", status: "", page: 1 };

Pages.bens = async function (el) {
  setTopbar(`<button class="btn btn-primary" id="btn-novo-bem">+ Novo Bem</button>`);
  document.getElementById("btn-novo-bem").onclick = () => bemForm();

  el.innerHTML = `
    <div class="toolbar">
      <input type="text" id="f-q" placeholder="Buscar por nome, tombo ou nº de série…" value="${UI.esc(bensState.q)}">
      <select id="f-categoria"></select>
      <select id="f-setor"></select>
      <select id="f-status">
        <option value="">Todos os status</option>
        <option value="ativo">Ativo</option>
        <option value="manutencao">Em manutenção</option>
        <option value="baixado">Baixado</option>
      </select>
    </div>
    <div id="bens-list">${UI.loading()}</div>
  `;

  const [cats, sets] = await Promise.all([API.get("/categorias"), API.get("/setores")]);
  document.getElementById("f-categoria").innerHTML = UI.options(cats, bensState.categoria_id, { placeholder: "Todas as categorias" });
  document.getElementById("f-setor").innerHTML = UI.options(sets, bensState.setor_id, { placeholder: "Todos os setores" });
  document.getElementById("f-status").value = bensState.status;

  let debounce;
  document.getElementById("f-q").oninput = (e) => {
    clearTimeout(debounce);
    debounce = setTimeout(() => { bensState.q = e.target.value; bensState.page = 1; loadBens(); }, 350);
  };
  for (const [id, key] of [["f-categoria", "categoria_id"], ["f-setor", "setor_id"], ["f-status", "status"]]) {
    document.getElementById(id).onchange = (e) => { bensState[key] = e.target.value; bensState.page = 1; loadBens(); };
  }

  await loadBens();

  async function loadBens() {
    const box = document.getElementById("bens-list");
    if (!box) return;
    const params = new URLSearchParams({ page: bensState.page });
    if (bensState.q) params.set("q", bensState.q);
    if (bensState.categoria_id) params.set("categoria_id", bensState.categoria_id);
    if (bensState.setor_id) params.set("setor_id", bensState.setor_id);
    if (bensState.status) params.set("status", bensState.status);

    const data = await API.get(`/bens?${params}`);
    const isAdmin = App.user.role === "admin";

    box.innerHTML = data.items.length ? `
      <div class="table-wrap">
        <table>
          <thead><tr>
            <th>Tombo</th><th>Nome</th><th>Categoria</th><th>Setor</th>
            <th class="td-num">Valor</th><th>Estado</th><th>Status</th><th></th>
          </tr></thead>
          <tbody>
            ${data.items.map(b => `
              <tr>
                <td class="td-strong">${UI.esc(b.tombo)}</td>
                <td class="td-strong">${UI.esc(b.nome)}</td>
                <td>${UI.esc(b.categoria_nome ?? "—")}</td>
                <td>${UI.esc(b.setor_nome ?? "—")}</td>
                <td class="td-num">${UI.money(b.valor_aquisicao)}</td>
                <td>${UI.estadoBadge(b.estado)}</td>
                <td>${UI.statusBadge(b.status)}</td>
                <td class="td-actions">
                  <button class="btn-icon" data-ver="${b.id}" title="Detalhes">
                    <svg viewBox="0 0 24 24"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17a5 5 0 1 1 0-10 5 5 0 0 1 0 10zm0-8a3 3 0 1 0 0 6 3 3 0 0 0 0-6z"/></svg>
                  </button>
                  ${b.status !== "baixado" ? `
                  <button class="btn-icon" data-editar="${b.id}" title="Editar">
                    <svg viewBox="0 0 24 24"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04a1 1 0 0 0 0-1.41l-2.34-2.34a1 1 0 0 0-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/></svg>
                  </button>` : ""}
                  ${isAdmin ? `
                  <button class="btn-icon" data-excluir="${b.id}" data-nome="${UI.esc(b.nome)}" title="Excluir">
                    <svg viewBox="0 0 24 24"><path d="M6 19c0 1.1.9 2 2 2h8a2 2 0 0 0 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>
                  </button>` : ""}
                </td>
              </tr>`).join("")}
          </tbody>
        </table>
      </div>
      <div class="pagination">
        <span>${data.total} bem(ns) — página ${data.page} de ${data.pages}</span>
        <div class="pages">
          <button class="btn btn-ghost btn-sm" id="pg-prev" ${data.page <= 1 ? "disabled" : ""}>‹ Anterior</button>
          <button class="btn btn-ghost btn-sm" id="pg-next" ${data.page >= data.pages ? "disabled" : ""}>Próxima ›</button>
        </div>
      </div>
    ` : UI.empty("Nenhum bem encontrado com os filtros atuais");

    const prev = document.getElementById("pg-prev");
    const next = document.getElementById("pg-next");
    if (prev) prev.onclick = () => { bensState.page--; loadBens(); };
    if (next) next.onclick = () => { bensState.page++; loadBens(); };

    box.querySelectorAll("[data-ver]").forEach(btn => btn.onclick = () => bemDetalhe(btn.dataset.ver));
    box.querySelectorAll("[data-editar]").forEach(btn => btn.onclick = async () => {
      const bem = await API.get(`/bens/${btn.dataset.editar}`);
      bemForm(bem);
    });
    box.querySelectorAll("[data-excluir]").forEach(btn => btn.onclick = async () => {
      const ok = await UI.confirm("Excluir bem",
        `Excluir definitivamente <strong>${btn.dataset.nome}</strong>?<br>O histórico de movimentações e manutenções também será removido. Para retirada de uso, prefira registrar uma <strong>baixa</strong>.`,
        { confirmLabel: "Excluir" });
      if (!ok) return;
      try {
        await API.del(`/bens/${btn.dataset.excluir}`);
        UI.toast("Bem excluído", "success");
        loadBens();
      } catch (err) { UI.toast(err.message, "error"); }
    });
  }

  /* ---- formulário criar/editar ---- */
  async function bemForm(bem = null) {
    const [cats2, sets2] = await Promise.all([API.get("/categorias"), API.get("/setores")]);
    const box = UI.modal({
      title: bem ? `Editar — ${bem.tombo}` : "Novo Bem",
      body: `
        <form id="bem-form">
          <div class="form-row">
            <div class="field">
              <label>Tombo / Nº patrimônio *</label>
              <input name="tombo" required value="${UI.esc(bem?.tombo ?? "")}" ${bem ? "disabled" : ""} placeholder="ex.: PAT-0001">
            </div>
            <div class="field">
              <label>Nome *</label>
              <input name="nome" required value="${UI.esc(bem?.nome ?? "")}" placeholder="ex.: Notebook Dell">
            </div>
          </div>
          <div class="form-row">
            <div class="field">
              <label>Categoria</label>
              <select name="categoria_id">${UI.options(cats2, bem?.categoria_id)}</select>
            </div>
            <div class="field">
              <label>Setor</label>
              <select name="setor_id" ${bem ? "disabled" : ""}>${UI.options(sets2, bem?.setor_id)}</select>
            </div>
          </div>
          <div class="form-row">
            <div class="field">
              <label>Valor de aquisição (R$)</label>
              <input name="valor_aquisicao" type="number" step="0.01" min="0" value="${bem?.valor_aquisicao ?? ""}" placeholder="0,00">
            </div>
            <div class="field">
              <label>Data de aquisição</label>
              <input name="data_aquisicao" type="date" value="${bem?.data_aquisicao ?? ""}">
            </div>
          </div>
          <div class="form-row">
            <div class="field">
              <label>Fornecedor</label>
              <input name="fornecedor" value="${UI.esc(bem?.fornecedor ?? "")}">
            </div>
            <div class="field">
              <label>Nº de série</label>
              <input name="num_serie" value="${UI.esc(bem?.num_serie ?? "")}">
            </div>
          </div>
          <div class="field">
            <label>Estado de conservação</label>
            <select name="estado">${UI.options(ESTADOS, bem?.estado ?? "bom", { placeholder: "" })}</select>
          </div>
          <div class="field">
            <label>Descrição</label>
            <textarea name="descricao" placeholder="detalhes, configuração, observações…">${UI.esc(bem?.descricao ?? "")}</textarea>
          </div>
          ${bem ? `<p style="font-size:12px;color:var(--muted)">Para trocar o setor, registre uma <strong>movimentação</strong>.</p>` : ""}
        </form>
      `,
      footer: `
        <button class="btn btn-ghost" data-cancel>Cancelar</button>
        <button class="btn btn-primary" data-salvar>${bem ? "Salvar alterações" : "Cadastrar"}</button>
      `,
      maxWidth: "640px",
    });
    box.querySelector("[data-cancel]").onclick = UI.closeModal;
    box.querySelector("[data-salvar]").onclick = async () => {
      const f = box.querySelector("#bem-form");
      if (!f.reportValidity()) return;
      const fd = new FormData(f);
      const payload = {
        nome: fd.get("nome").trim(),
        descricao: fd.get("descricao").trim(),
        categoria_id: fd.get("categoria_id") ? Number(fd.get("categoria_id")) : null,
        fornecedor: fd.get("fornecedor").trim(),
        num_serie: fd.get("num_serie").trim(),
        valor_aquisicao: Number(fd.get("valor_aquisicao") || 0),
        data_aquisicao: fd.get("data_aquisicao") || null,
        estado: fd.get("estado"),
      };
      try {
        if (bem) {
          await API.put(`/bens/${bem.id}`, payload);
          UI.toast("Bem atualizado", "success");
        } else {
          payload.tombo = fd.get("tombo").trim();
          payload.setor_id = fd.get("setor_id") ? Number(fd.get("setor_id")) : null;
          await API.post("/bens", payload);
          UI.toast("Bem cadastrado", "success");
        }
        UI.closeModal();
        loadBens();
      } catch (err) { UI.toast(err.message, "error"); }
    };
  }

  /* ---- detalhe + histórico ---- */
  async function bemDetalhe(id) {
    const [bem, movs, mans] = await Promise.all([
      API.get(`/bens/${id}`),
      API.get(`/movimentacoes?bem_id=${id}`),
      API.get(`/manutencoes?bem_id=${id}`),
    ]);
    const item = (k, v) => `<div class="detail-item"><div class="k">${k}</div><div class="v">${v}</div></div>`;
    UI.modal({
      title: `${bem.tombo} — ${bem.nome}`,
      body: `
        <div class="detail-grid">
          ${item("Status", UI.statusBadge(bem.status))}
          ${item("Estado", UI.estadoBadge(bem.estado))}
          ${item("Categoria", UI.esc(bem.categoria_nome ?? "—"))}
          ${item("Setor atual", UI.esc(bem.setor_nome ?? "—"))}
          ${item("Valor de aquisição", UI.money(bem.valor_aquisicao))}
          ${item("Data de aquisição", UI.date(bem.data_aquisicao))}
          ${item("Fornecedor", UI.esc(bem.fornecedor || "—"))}
          ${item("Nº de série", UI.esc(bem.num_serie || "—"))}
        </div>
        ${bem.descricao ? `<p style="margin-top:14px;font-size:13.5px;color:var(--text-soft);line-height:1.5">${UI.esc(bem.descricao)}</p>` : ""}

        <div class="card-title" style="margin-top:22px">Histórico de movimentações</div>
        ${movs.length ? `<table><tbody>${movs.map(m => `
          <tr>
            <td style="padding:8px 6px;white-space:nowrap;color:var(--muted)">${UI.dateTime(m.data)}</td>
            <td style="padding:8px 6px">${UI.esc(m.setor_origem_nome ?? "—")} → <strong>${UI.esc(m.setor_destino_nome)}</strong></td>
            <td style="padding:8px 6px;color:var(--muted)">${UI.esc(m.motivo || "")}</td>
          </tr>`).join("")}</tbody></table>` : `<p style="font-size:13px;color:var(--muted)">Nenhuma movimentação.</p>`}

        <div class="card-title" style="margin-top:20px">Histórico de manutenções</div>
        ${mans.length ? `<table><tbody>${mans.map(m => `
          <tr>
            <td style="padding:8px 6px;white-space:nowrap;color:var(--muted)">${UI.date(m.data_inicio)}</td>
            <td style="padding:8px 6px">${UI.esc(m.tipo)} — ${UI.esc(m.descricao || "sem descrição")}</td>
            <td style="padding:8px 6px">${UI.statusBadge(m.status)}</td>
            <td style="padding:8px 6px" class="td-num">${UI.money(m.custo)}</td>
          </tr>`).join("")}</tbody></table>` : `<p style="font-size:13px;color:var(--muted)">Nenhuma manutenção.</p>`}
      `,
      footer: `<button class="btn btn-ghost" onclick="UI.closeModal()">Fechar</button>`,
      maxWidth: "680px",
    });
  }
};

/* ============================ CATEGORIAS / SETORES ============================ */
function cadastroSimples({ titulo, singular, endpoint, campos, colunas }) {
  return async function (el) {
    setTopbar(`<button class="btn btn-primary" id="btn-novo">+ ${singular}</button>`);
    document.getElementById("btn-novo").onclick = () => form();
    el.innerHTML = UI.loading();
    await load();

    async function load() {
      const rows = await API.get(endpoint);
      el.innerHTML = rows.length ? `
        <div class="table-wrap">
          <table>
            <thead><tr>${colunas.map(c => `<th>${c.label}</th>`).join("")}<th class="td-num">Bens</th><th></th></tr></thead>
            <tbody>
              ${rows.map(r => `
                <tr>
                  ${colunas.map((c, i) => `<td class="${i === 0 ? "td-strong" : ""}">${UI.esc(r[c.key] || "—")}</td>`).join("")}
                  <td class="td-num">${r.total_bens}</td>
                  <td class="td-actions">
                    <button class="btn-icon" data-editar="${r.id}" title="Editar">
                      <svg viewBox="0 0 24 24"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04a1 1 0 0 0 0-1.41l-2.34-2.34a1 1 0 0 0-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/></svg>
                    </button>
                    <button class="btn-icon" data-excluir="${r.id}" data-nome="${UI.esc(r.nome)}" title="Excluir">
                      <svg viewBox="0 0 24 24"><path d="M6 19c0 1.1.9 2 2 2h8a2 2 0 0 0 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>
                    </button>
                  </td>
                </tr>`).join("")}
            </tbody>
          </table>
        </div>` : UI.empty(`Nenhum registro. Clique em “+ ${singular}” para criar.`);

      el.querySelectorAll("[data-editar]").forEach(btn => btn.onclick = () => {
        const item = rows.find(r => r.id == btn.dataset.editar);
        form(item);
      });
      el.querySelectorAll("[data-excluir]").forEach(btn => btn.onclick = async () => {
        const ok = await UI.confirm(`Excluir ${singular.toLowerCase()}`,
          `Excluir <strong>${btn.dataset.nome}</strong>?`, { confirmLabel: "Excluir" });
        if (!ok) return;
        try {
          await API.del(`${endpoint}/${btn.dataset.excluir}`);
          UI.toast(`${singular} excluído(a)`, "success");
          load();
        } catch (err) { UI.toast(err.message, "error"); }
      });
    }

    function form(item = null) {
      const box = UI.modal({
        title: item ? `Editar ${singular}` : `Novo(a) ${singular}`,
        body: `
          <form id="cad-form">
            ${campos.map(c => `
              <div class="field">
                <label>${c.label}${c.required ? " *" : ""}</label>
                ${c.textarea
                  ? `<textarea name="${c.key}">${UI.esc(item?.[c.key] ?? "")}</textarea>`
                  : `<input name="${c.key}" ${c.required ? "required" : ""} value="${UI.esc(item?.[c.key] ?? "")}" placeholder="${c.placeholder || ""}">`}
              </div>`).join("")}
          </form>`,
        footer: `
          <button class="btn btn-ghost" data-cancel>Cancelar</button>
          <button class="btn btn-primary" data-salvar>${item ? "Salvar" : "Criar"}</button>`,
      });
      box.querySelector("[data-cancel]").onclick = UI.closeModal;
      box.querySelector("[data-salvar]").onclick = async () => {
        const f = box.querySelector("#cad-form");
        if (!f.reportValidity()) return;
        const fd = new FormData(f);
        const payload = Object.fromEntries(campos.map(c => [c.key, (fd.get(c.key) || "").trim()]));
        try {
          if (item) await API.put(`${endpoint}/${item.id}`, payload);
          else await API.post(endpoint, payload);
          UI.toast(`${singular} salvo(a)`, "success");
          UI.closeModal();
          load();
        } catch (err) { UI.toast(err.message, "error"); }
      };
    }
  };
}

Pages.categorias = cadastroSimples({
  titulo: "Categorias", singular: "Categoria", endpoint: "/categorias",
  campos: [
    { key: "nome", label: "Nome", required: true, placeholder: "ex.: Informática" },
    { key: "descricao", label: "Descrição", textarea: true },
  ],
  colunas: [
    { key: "nome", label: "Nome" },
    { key: "descricao", label: "Descrição" },
  ],
});

Pages.setores = cadastroSimples({
  titulo: "Setores", singular: "Setor", endpoint: "/setores",
  campos: [
    { key: "nome", label: "Nome", required: true, placeholder: "ex.: Financeiro" },
    { key: "responsavel", label: "Responsável", placeholder: "nome do responsável" },
    { key: "localizacao", label: "Localização", placeholder: "ex.: Prédio A — 2º andar" },
  ],
  colunas: [
    { key: "nome", label: "Nome" },
    { key: "responsavel", label: "Responsável" },
    { key: "localizacao", label: "Localização" },
  ],
});

/* ============================ MOVIMENTAÇÕES ============================ */
Pages.movimentacoes = async function (el) {
  setTopbar(`<button class="btn btn-primary" id="btn-nova-mov">+ Nova Movimentação</button>`);
  document.getElementById("btn-nova-mov").onclick = novaMov;
  el.innerHTML = UI.loading();
  await load();

  async function load() {
    const rows = await API.get("/movimentacoes");
    el.innerHTML = rows.length ? `
      <div class="table-wrap">
        <table>
          <thead><tr><th>Data</th><th>Bem</th><th>Origem</th><th>Destino</th><th>Motivo</th><th>Por</th></tr></thead>
          <tbody>
            ${rows.map(m => `
              <tr>
                <td style="white-space:nowrap;color:var(--muted)">${UI.dateTime(m.data)}</td>
                <td class="td-strong">${UI.esc(m.bem_tombo)} — ${UI.esc(m.bem_nome)}</td>
                <td>${UI.esc(m.setor_origem_nome ?? "—")}</td>
                <td class="td-strong">${UI.esc(m.setor_destino_nome)}</td>
                <td>${UI.esc(m.motivo || "—")}</td>
                <td style="color:var(--muted)">${UI.esc(m.usuario_nome ?? "—")}</td>
              </tr>`).join("")}
          </tbody>
        </table>
      </div>` : UI.empty("Nenhuma movimentação registrada");
  }

  async function novaMov() {
    const [bens, setores] = await Promise.all([API.get("/bens/todos"), API.get("/setores")]);
    const opcoes = bens.map(b => ({ id: b.id, nome: `${b.tombo} — ${b.nome} (${b.setor_nome ?? "sem setor"})` }));
    const box = UI.modal({
      title: "Nova Movimentação",
      body: `
        <form id="mov-form">
          <div class="field">
            <label>Bem *</label>
            <select name="bem_id" required>${UI.options(opcoes, "", { placeholder: "Selecione o bem…" })}</select>
          </div>
          <div class="field">
            <label>Setor de destino *</label>
            <select name="setor_destino_id" required>${UI.options(setores, "", { placeholder: "Selecione o destino…" })}</select>
          </div>
          <div class="field">
            <label>Motivo</label>
            <textarea name="motivo" placeholder="ex.: remanejamento, novo posto de trabalho…"></textarea>
          </div>
        </form>`,
      footer: `
        <button class="btn btn-ghost" data-cancel>Cancelar</button>
        <button class="btn btn-primary" data-salvar>Registrar</button>`,
    });
    box.querySelector("[data-cancel]").onclick = UI.closeModal;
    box.querySelector("[data-salvar]").onclick = async () => {
      const f = box.querySelector("#mov-form");
      if (!f.reportValidity()) return;
      const fd = new FormData(f);
      try {
        await API.post("/movimentacoes", {
          bem_id: Number(fd.get("bem_id")),
          setor_destino_id: Number(fd.get("setor_destino_id")),
          motivo: (fd.get("motivo") || "").trim(),
        });
        UI.toast("Movimentação registrada", "success");
        UI.closeModal();
        load();
      } catch (err) { UI.toast(err.message, "error"); }
    };
  }
};

/* ============================ MANUTENÇÕES ============================ */
Pages.manutencoes = async function (el) {
  setTopbar(`<button class="btn btn-primary" id="btn-nova-man">+ Nova Manutenção</button>`);
  document.getElementById("btn-nova-man").onclick = novaMan;
  el.innerHTML = UI.loading();
  await load();

  async function load() {
    const rows = await API.get("/manutencoes");
    el.innerHTML = rows.length ? `
      <div class="table-wrap">
        <table>
          <thead><tr><th>Início</th><th>Bem</th><th>Tipo</th><th>Responsável</th><th class="td-num">Custo</th><th>Status</th><th></th></tr></thead>
          <tbody>
            ${rows.map(m => `
              <tr>
                <td style="white-space:nowrap;color:var(--muted)">${UI.date(m.data_inicio)}</td>
                <td class="td-strong">${UI.esc(m.bem_tombo)} — ${UI.esc(m.bem_nome)}</td>
                <td style="text-transform:capitalize">${UI.esc(m.tipo)}</td>
                <td>${UI.esc(m.responsavel || "—")}</td>
                <td class="td-num">${UI.money(m.custo)}</td>
                <td>${UI.statusBadge(m.status)}</td>
                <td class="td-actions">
                  ${m.status === "aberta"
                    ? `<button class="btn btn-ghost btn-sm" data-concluir="${m.id}">Concluir</button>`
                    : `<span style="color:var(--muted);font-size:12px">${UI.date(m.data_fim)}</span>`}
                </td>
              </tr>`).join("")}
          </tbody>
        </table>
      </div>` : UI.empty("Nenhuma manutenção registrada");

    el.querySelectorAll("[data-concluir]").forEach(btn => btn.onclick = () => concluir(btn.dataset.concluir));
  }

  async function novaMan() {
    const bens = await API.get("/bens/todos");
    const opcoes = bens.filter(b => b.status === "ativo")
      .map(b => ({ id: b.id, nome: `${b.tombo} — ${b.nome}` }));
    const box = UI.modal({
      title: "Nova Manutenção",
      body: `
        <form id="man-form">
          <div class="field">
            <label>Bem *</label>
            <select name="bem_id" required>${UI.options(opcoes, "", { placeholder: "Selecione o bem…" })}</select>
          </div>
          <div class="form-row">
            <div class="field">
              <label>Tipo</label>
              <select name="tipo">
                <option value="corretiva">Corretiva</option>
                <option value="preventiva">Preventiva</option>
              </select>
            </div>
            <div class="field">
              <label>Custo estimado (R$)</label>
              <input name="custo" type="number" step="0.01" min="0" placeholder="0,00">
            </div>
          </div>
          <div class="field">
            <label>Responsável / prestador</label>
            <input name="responsavel" placeholder="técnico ou empresa">
          </div>
          <div class="field">
            <label>Descrição do problema/serviço</label>
            <textarea name="descricao"></textarea>
          </div>
        </form>`,
      footer: `
        <button class="btn btn-ghost" data-cancel>Cancelar</button>
        <button class="btn btn-primary" data-salvar>Abrir manutenção</button>`,
    });
    box.querySelector("[data-cancel]").onclick = UI.closeModal;
    box.querySelector("[data-salvar]").onclick = async () => {
      const f = box.querySelector("#man-form");
      if (!f.reportValidity()) return;
      const fd = new FormData(f);
      try {
        await API.post("/manutencoes", {
          bem_id: Number(fd.get("bem_id")),
          tipo: fd.get("tipo"),
          custo: Number(fd.get("custo") || 0),
          responsavel: (fd.get("responsavel") || "").trim(),
          descricao: (fd.get("descricao") || "").trim(),
        });
        UI.toast("Manutenção aberta — bem marcado como 'Em manutenção'", "success");
        UI.closeModal();
        load();
      } catch (err) { UI.toast(err.message, "error"); }
    };
  }

  function concluir(id) {
    const box = UI.modal({
      title: "Concluir Manutenção",
      body: `
        <form id="conc-form">
          <div class="field">
            <label>Custo final (R$) — deixe em branco para manter o estimado</label>
            <input name="custo" type="number" step="0.01" min="0" placeholder="0,00">
          </div>
          <p style="font-size:13px;color:var(--muted)">O bem voltará ao status <strong>Ativo</strong>.</p>
        </form>`,
      footer: `
        <button class="btn btn-ghost" data-cancel>Cancelar</button>
        <button class="btn btn-primary" data-salvar>Concluir</button>`,
      maxWidth: "440px",
    });
    box.querySelector("[data-cancel]").onclick = UI.closeModal;
    box.querySelector("[data-salvar]").onclick = async () => {
      const custo = box.querySelector("[name=custo]").value;
      try {
        await API.post(`/manutencoes/${id}/concluir`, { custo: custo === "" ? null : Number(custo) });
        UI.toast("Manutenção concluída", "success");
        UI.closeModal();
        load();
      } catch (err) { UI.toast(err.message, "error"); }
    };
  }
};

/* ============================ BAIXAS ============================ */
Pages.baixas = async function (el) {
  setTopbar(`<button class="btn btn-primary" id="btn-nova-baixa">+ Registrar Baixa</button>`);
  document.getElementById("btn-nova-baixa").onclick = novaBaixa;
  el.innerHTML = UI.loading();
  await load();

  async function load() {
    const rows = await API.get("/baixas");
    el.innerHTML = rows.length ? `
      <div class="table-wrap">
        <table>
          <thead><tr><th>Data</th><th>Bem</th><th>Motivo</th><th>Observação</th><th>Por</th></tr></thead>
          <tbody>
            ${rows.map(b => `
              <tr>
                <td style="white-space:nowrap;color:var(--muted)">${UI.dateTime(b.data)}</td>
                <td class="td-strong">${UI.esc(b.bem_tombo)} — ${UI.esc(b.bem_nome)}</td>
                <td style="text-transform:capitalize">${UI.esc(b.motivo)}</td>
                <td>${UI.esc(b.observacao || "—")}</td>
                <td style="color:var(--muted)">${UI.esc(b.usuario_nome ?? "—")}</td>
              </tr>`).join("")}
          </tbody>
        </table>
      </div>` : UI.empty("Nenhuma baixa registrada");
  }

  async function novaBaixa() {
    const bens = await API.get("/bens/todos");
    const opcoes = bens.map(b => ({ id: b.id, nome: `${b.tombo} — ${b.nome}` }));
    const box = UI.modal({
      title: "Registrar Baixa",
      body: `
        <form id="baixa-form">
          <div class="field">
            <label>Bem *</label>
            <select name="bem_id" required>${UI.options(opcoes, "", { placeholder: "Selecione o bem…" })}</select>
          </div>
          <div class="field">
            <label>Motivo *</label>
            <select name="motivo" required>${UI.options(MOTIVOS_BAIXA, "inservivel", { placeholder: "" })}</select>
          </div>
          <div class="field">
            <label>Observação</label>
            <textarea name="observacao" placeholder="nº do processo, justificativa…"></textarea>
          </div>
          <p style="font-size:13px;color:var(--red-bright)">⚠ A baixa retira o bem do acervo ativo. Esta ação não pode ser desfeita pelo sistema.</p>
        </form>`,
      footer: `
        <button class="btn btn-ghost" data-cancel>Cancelar</button>
        <button class="btn btn-danger-soft" data-salvar>Registrar baixa</button>`,
    });
    box.querySelector("[data-cancel]").onclick = UI.closeModal;
    box.querySelector("[data-salvar]").onclick = async () => {
      const f = box.querySelector("#baixa-form");
      if (!f.reportValidity()) return;
      const fd = new FormData(f);
      try {
        await API.post("/baixas", {
          bem_id: Number(fd.get("bem_id")),
          motivo: fd.get("motivo"),
          observacao: (fd.get("observacao") || "").trim(),
        });
        UI.toast("Baixa registrada", "success");
        UI.closeModal();
        load();
      } catch (err) { UI.toast(err.message, "error"); }
    };
  }
};

/* ============================ RELATÓRIOS ============================ */
Pages.relatorios = async function (el) {
  setTopbar("");
  const reports = [
    { path: "/relatorios/bens.csv", titulo: "Inventário de Bens", desc: "Lista completa do patrimônio com tombo, categoria, setor, valores e status." },
    { path: "/relatorios/bens.csv?status=ativo", titulo: "Bens Ativos", desc: "Somente os bens em uso (exclui baixados e em manutenção)." },
    { path: "/relatorios/movimentacoes.csv", titulo: "Movimentações", desc: "Histórico completo de transferências entre setores." },
    { path: "/relatorios/manutencoes.csv", titulo: "Manutenções", desc: "Manutenções abertas e concluídas, com custos e responsáveis." },
    { path: "/relatorios/baixas.csv", titulo: "Baixas", desc: "Bens baixados do acervo, com motivo e responsável pelo registro." },
  ];
  el.innerHTML = `
    <div class="report-grid">
      ${reports.map((r, i) => `
        <div class="report-card">
          <h4>${r.titulo}</h4>
          <p>${r.desc}</p>
          <button class="btn btn-ghost" data-dl="${i}">⬇ Baixar CSV</button>
        </div>`).join("")}
    </div>
    <p style="margin-top:18px;font-size:12.5px;color:var(--muted)">
      Os arquivos são gerados em CSV (separador “;”) compatível com Excel e LibreOffice.
    </p>
  `;
  el.querySelectorAll("[data-dl]").forEach(btn => btn.onclick = async () => {
    btn.disabled = true;
    try {
      await API.download(reports[btn.dataset.dl].path);
      UI.toast("Relatório gerado", "success");
    } catch (err) { UI.toast(err.message, "error"); }
    btn.disabled = false;
  });
};

/* ============================ USUÁRIOS ============================ */
Pages.usuarios = async function (el) {
  if (App.user.role !== "admin") {
    el.innerHTML = UI.empty("Acesso restrito a administradores");
    setTopbar("");
    return;
  }
  setTopbar(`<button class="btn btn-primary" id="btn-novo-user">+ Novo Usuário</button>`);
  document.getElementById("btn-novo-user").onclick = () => form();
  el.innerHTML = UI.loading();
  await load();

  async function load() {
    const rows = await API.get("/usuarios");
    el.innerHTML = `
      <div class="table-wrap">
        <table>
          <thead><tr><th>Nome</th><th>Usuário</th><th>Perfil</th><th>Situação</th><th>Criado em</th><th></th></tr></thead>
          <tbody>
            ${rows.map(u => `
              <tr>
                <td class="td-strong">${UI.esc(u.nome)}</td>
                <td>${UI.esc(u.username)}</td>
                <td><span class="badge ${u.role === "admin" ? "badge-red" : "badge-blue"}">${u.role === "admin" ? "Administrador" : "Operador"}</span></td>
                <td>${u.ativo ? '<span class="badge badge-green">Ativo</span>' : '<span class="badge badge-gray">Inativo</span>'}</td>
                <td style="color:var(--muted)">${UI.date(u.criado_em)}</td>
                <td class="td-actions">
                  <button class="btn-icon" data-editar="${u.id}" title="Editar">
                    <svg viewBox="0 0 24 24"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04a1 1 0 0 0 0-1.41l-2.34-2.34a1 1 0 0 0-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/></svg>
                  </button>
                  ${u.id !== App.user.id ? `
                  <button class="btn-icon" data-excluir="${u.id}" data-nome="${UI.esc(u.nome)}" title="Excluir">
                    <svg viewBox="0 0 24 24"><path d="M6 19c0 1.1.9 2 2 2h8a2 2 0 0 0 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>
                  </button>` : ""}
                </td>
              </tr>`).join("")}
          </tbody>
        </table>
      </div>`;

    el.querySelectorAll("[data-editar]").forEach(btn => btn.onclick = () => {
      form(rows.find(u => u.id == btn.dataset.editar));
    });
    el.querySelectorAll("[data-excluir]").forEach(btn => btn.onclick = async () => {
      const ok = await UI.confirm("Excluir usuário",
        `Excluir o usuário <strong>${btn.dataset.nome}</strong>?`, { confirmLabel: "Excluir" });
      if (!ok) return;
      try {
        await API.del(`/usuarios/${btn.dataset.excluir}`);
        UI.toast("Usuário excluído", "success");
        load();
      } catch (err) { UI.toast(err.message, "error"); }
    });
  }

  function form(user = null) {
    const box = UI.modal({
      title: user ? `Editar — ${user.nome}` : "Novo Usuário",
      body: `
        <form id="user-form">
          <div class="field">
            <label>Nome completo *</label>
            <input name="nome" required value="${UI.esc(user?.nome ?? "")}">
          </div>
          <div class="form-row">
            <div class="field">
              <label>Usuário (login) *</label>
              <input name="username" required minlength="3" value="${UI.esc(user?.username ?? "")}" ${user ? "disabled" : ""}>
            </div>
            <div class="field">
              <label>${user ? "Nova senha (opcional)" : "Senha *"}</label>
              <input name="password" type="password" minlength="4" ${user ? "" : "required"} placeholder="${user ? "manter atual" : "mín. 4 caracteres"}">
            </div>
          </div>
          <div class="form-row">
            <div class="field">
              <label>Perfil</label>
              <select name="role">
                <option value="operador" ${user?.role === "operador" ? "selected" : ""}>Operador</option>
                <option value="admin" ${user?.role === "admin" ? "selected" : ""}>Administrador</option>
              </select>
            </div>
            ${user ? `
            <div class="field">
              <label>Situação</label>
              <select name="ativo">
                <option value="true" ${user.ativo ? "selected" : ""}>Ativo</option>
                <option value="false" ${!user.ativo ? "selected" : ""}>Inativo</option>
              </select>
            </div>` : ""}
          </div>
        </form>`,
      footer: `
        <button class="btn btn-ghost" data-cancel>Cancelar</button>
        <button class="btn btn-primary" data-salvar>${user ? "Salvar" : "Criar"}</button>`,
    });
    box.querySelector("[data-cancel]").onclick = UI.closeModal;
    box.querySelector("[data-salvar]").onclick = async () => {
      const f = box.querySelector("#user-form");
      if (!f.reportValidity()) return;
      const fd = new FormData(f);
      try {
        if (user) {
          await API.put(`/usuarios/${user.id}`, {
            nome: fd.get("nome").trim(),
            password: fd.get("password") || null,
            role: fd.get("role"),
            ativo: fd.get("ativo") === "true",
          });
        } else {
          await API.post("/usuarios", {
            nome: fd.get("nome").trim(),
            username: fd.get("username").trim().toLowerCase(),
            password: fd.get("password"),
            role: fd.get("role"),
          });
        }
        UI.toast("Usuário salvo", "success");
        UI.closeModal();
        load();
      } catch (err) { UI.toast(err.message, "error"); }
    };
  }
};
