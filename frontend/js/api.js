/* Cliente da API ------------------------------------------------ */
const API = {
  base: "/api",

  get token() { return localStorage.getItem("patrimonio_token"); },
  set token(v) {
    if (v) localStorage.setItem("patrimonio_token", v);
    else localStorage.removeItem("patrimonio_token");
  },

  async request(method, path, body) {
    const headers = {};
    if (body !== undefined) headers["Content-Type"] = "application/json";
    if (this.token) headers["Authorization"] = `Bearer ${this.token}`;

    const res = await fetch(this.base + path, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });

    if (res.status === 401 && path !== "/auth/login") {
      this.token = null;
      window.dispatchEvent(new Event("session-expired"));
      throw new ApiError(401, "Sessão expirada. Faça login novamente.");
    }

    if (!res.ok) {
      let detail = `Erro ${res.status}`;
      try {
        const data = await res.json();
        if (typeof data.detail === "string") detail = data.detail;
        else if (Array.isArray(data.detail) && data.detail[0])
          detail = `${data.detail[0].loc?.slice(-1)[0] ?? ""}: ${data.detail[0].msg}`;
      } catch { /* corpo não-JSON */ }
      throw new ApiError(res.status, detail);
    }

    if (res.status === 204) return null;
    return res.json();
  },

  get(path) { return this.request("GET", path); },
  post(path, body) { return this.request("POST", path, body); },
  put(path, body) { return this.request("PUT", path, body); },
  del(path) { return this.request("DELETE", path); },

  /* baixa um relatório CSV autenticado */
  async download(path) {
    const res = await fetch(this.base + path, {
      headers: { Authorization: `Bearer ${this.token}` },
    });
    if (!res.ok) throw new ApiError(res.status, "Falha ao gerar o relatório");
    const blob = await res.blob();
    const cd = res.headers.get("Content-Disposition") || "";
    const match = cd.match(/filename="?([^";]+)"?/);
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = match ? match[1] : "relatorio.csv";
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(a.href);
  },
};

class ApiError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}
