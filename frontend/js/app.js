/* Inicialização e roteamento -------------------------------------- */
const App = {
  user: null,

  TITLES: {
    dashboard: "Dashboard",
    bens: "Bens Patrimoniais",
    movimentacoes: "Movimentações",
    manutencoes: "Manutenções",
    baixas: "Baixas",
    categorias: "Categorias",
    setores: "Setores",
    relatorios: "Relatórios",
    usuarios: "Usuários",
  },

  async init() {
    document.getElementById("login-form").addEventListener("submit", (e) => {
      e.preventDefault();
      App.login();
    });
    document.getElementById("logout-btn").addEventListener("click", App.logout);
    window.addEventListener("hashchange", () => App.route());
    window.addEventListener("session-expired", () => {
      UI.closeModal();
      App.showLogin("Sua sessão expirou. Entre novamente.");
    });

    if (API.token) {
      try {
        App.user = await API.get("/auth/me");
        App.showApp();
        return;
      } catch { API.token = null; }
    }
    App.showLogin();
  },

  async login() {
    const btn = document.getElementById("login-btn");
    const errBox = document.getElementById("login-error");
    errBox.classList.add("hidden");
    btn.disabled = true;
    btn.textContent = "Entrando…";
    try {
      const data = await API.post("/auth/login", {
        username: document.getElementById("login-username").value.trim(),
        password: document.getElementById("login-password").value,
      });
      API.token = data.token;
      App.user = data.usuario;
      App.showApp();
    } catch (err) {
      errBox.textContent = err.message;
      errBox.classList.remove("hidden");
    } finally {
      btn.disabled = false;
      btn.textContent = "Entrar";
    }
  },

  logout() {
    API.token = null;
    App.user = null;
    location.hash = "";
    App.showLogin();
  },

  showLogin(message) {
    document.getElementById("app-shell").classList.add("hidden");
    const screen = document.getElementById("login-screen");
    screen.classList.remove("hidden");
    document.getElementById("login-password").value = "";
    const errBox = document.getElementById("login-error");
    if (message) {
      errBox.textContent = message;
      errBox.classList.remove("hidden");
    } else {
      errBox.classList.add("hidden");
    }
  },

  showApp() {
    document.getElementById("login-screen").classList.add("hidden");
    document.getElementById("app-shell").classList.remove("hidden");

    document.getElementById("user-name").textContent = App.user.nome;
    document.getElementById("user-role").textContent = App.user.role === "admin" ? "Administrador" : "Operador";
    document.getElementById("user-avatar").textContent = App.user.nome.charAt(0).toUpperCase();
    document.getElementById("nav-usuarios").classList.toggle("hidden", App.user.role !== "admin");

    if (!location.hash || location.hash === "#") location.hash = "#/dashboard";
    else App.route();
  },

  async route() {
    if (!App.user) return;
    const page = (location.hash.replace("#/", "") || "dashboard").split("?")[0];
    const render = Pages[page];
    const el = document.getElementById("page-content");

    document.querySelectorAll(".sidebar-nav a").forEach(a => {
      a.classList.toggle("active", a.dataset.page === page);
    });
    document.getElementById("page-title").textContent = App.TITLES[page] || "Patrimônio";

    if (!render) {
      location.hash = "#/dashboard";
      return;
    }
    try {
      await render(el);
    } catch (err) {
      if (err.status !== 401) {
        el.innerHTML = UI.empty("Erro ao carregar a página: " + err.message);
      }
    }
  },
};

document.addEventListener("DOMContentLoaded", () => App.init());
