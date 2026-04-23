/**
 * Script.js - Utilitários e funções compartilhadas
 * API de Patrimônio - Frontend
 */

// Configuração da API
const API_BASE_URL = 'http://localhost:5000/api';

// Classe para fazer requisições à API
class PatrimonioAPI {
    static async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.mensagem || 'Erro ao comunicar com a API');
            }

            return data;
        } catch (error) {
            console.error('Erro na requisição:', error);
            throw error;
        }
    }

    // GET - Listar patrimônios
    static async getPatrimonios() {
        return this.request('/patrimonios');
    }

    // GET - Obter patrimônio específico
    static async getPatrimonio(id) {
        return this.request(`/patrimonios/${id}`);
    }

    // POST - Adicionar patrimônio
    static async createPatrimonio(data) {
        return this.request('/patrimonios', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // PUT - Atualizar patrimônio
    static async updatePatrimonio(id, data) {
        return this.request(`/patrimonios/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    // DELETE - Deletar patrimônio
    static async deletePatrimonio(id) {
        return this.request(`/patrimonios/${id}`, {
            method: 'DELETE'
        });
    }

    // POST - Dar baixa
    static async darBaixa(id, motivo) {
        return this.request(`/patrimonios/${id}/baixa`, {
            method: 'POST',
            body: JSON.stringify({ motivo })
        });
    }

    // GET - Relatório ativos
    static async getRelatorioAtivos() {
        return this.request('/relatorios/ativos');
    }

    // GET - Relatório inativos
    static async getRelatorioInativos() {
        return this.request('/relatorios/inativos');
    }

    // GET - Relatório geral
    static async getRelatorioGeral() {
        return this.request('/relatorios/geral');
    }

    // GET - Status da API
    static async checkHealth() {
        return this.request('/saude');
    }
}

// Utilitários de formatação
const Formatter = {
    // Formatar moeda
    formatCurrency(value) {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(value);
    },

    // Formatar data
    formatDate(dateString) {
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('pt-BR', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit'
        }).format(date);
    },

    // Formatar data e hora
    formatDateTime(dateString) {
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('pt-BR', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        }).format(date);
    },

    // Truncar texto
    truncate(text, length = 50) {
        if (text.length > length) {
            return text.substring(0, length) + '...';
        }
        return text;
    }
};

// Utilitários de validação
const Validator = {
    // Validar email
    isValidEmail(email) {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    },

    // Validar senha
    isValidPassword(password) {
        return password.length >= 6;
    },

    // Validar campo obrigatório
    isEmpty(value) {
        return value === null || value === undefined || value.trim() === '';
    },

    // Validar campo numérico
    isNumber(value) {
        return !isNaN(parseFloat(value)) && isFinite(value);
    }
};

// Utilitários de storage
const Storage = {
    // Salvar dados
    set(key, value) {
        try {
            sessionStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.error('Erro ao salvar no storage:', e);
        }
    },

    // Obter dados
    get(key) {
        try {
            const item = sessionStorage.getItem(key);
            return item ? JSON.parse(item) : null;
        } catch (e) {
            console.error('Erro ao obter do storage:', e);
            return null;
        }
    },

    // Remover dados
    remove(key) {
        try {
            sessionStorage.removeItem(key);
        } catch (e) {
            console.error('Erro ao remover do storage:', e);
        }
    },

    // Limpar tudo
    clear() {
        try {
            sessionStorage.clear();
        } catch (e) {
            console.error('Erro ao limpar storage:', e);
        }
    }
};

// Utilitários de notificação
const Notify = {
    // Mostrar notificação
    show(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            background: ${this.getBackground(type)};
            color: white;
            border-radius: 8px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            z-index: 500;
            animation: slideInRight 0.3s ease-out;
        `;
        notification.textContent = message;

        document.body.appendChild(notification);

        if (duration > 0) {
            setTimeout(() => {
                notification.style.animation = 'slideOutRight 0.3s ease-out';
                setTimeout(() => notification.remove(), 300);
            }, duration);
        }
    },

    getBackground(type) {
        const colors = {
            'success': '#10b981',
            'error': '#ef4444',
            'warning': '#f59e0b',
            'info': '#3b82f6'
        };
        return colors[type] || colors.info;
    },

    success(message) { this.show(message, 'success'); },
    error(message) { this.show(message, 'error'); },
    warning(message) { this.show(message, 'warning'); },
    info(message) { this.show(message, 'info'); }
};

// Utilitários de DOM
const DOM = {
    // Selecionar um elemento
    select(selector) {
        return document.querySelector(selector);
    },

    // Selecionar múltiplos elementos
    selectAll(selector) {
        return document.querySelectorAll(selector);
    },

    // Criar elemento
    create(tag, className = '', id = '') {
        const element = document.createElement(tag);
        if (className) element.className = className;
        if (id) element.id = id;
        return element;
    },

    // Adicionar classes
    addClass(element, className) {
        element.classList.add(className);
    },

    // Remover classes
    removeClass(element, className) {
        element.classList.remove(className);
    },

    // Toggle classe
    toggleClass(element, className) {
        element.classList.toggle(className);
    },

    // Verificar se tem classe
    hasClass(element, className) {
        return element.classList.contains(className);
    },

    // Mostrar elemento
    show(element) {
        element.style.display = 'block';
    },

    // Esconder elemento
    hide(element) {
        element.style.display = 'none';
    }
};

// Utilitários de requisição HTTP alternativo
const HTTP = {
    async get(url) {
        const response = await fetch(url);
        return response.json();
    },

    async post(url, data) {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return response.json();
    },

    async put(url, data) {
        const response = await fetch(url, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return response.json();
    },

    async delete(url) {
        const response = await fetch(url, { method: 'DELETE' });
        return response.json();
    }
};

// Exportar para uso global
window.PatrimonioAPI = PatrimonioAPI;
window.Formatter = Formatter;
window.Validator = Validator;
window.Storage = Storage;
window.Notify = Notify;
window.DOM = DOM;
window.HTTP = HTTP;

console.log('✅ Script.js carregado com sucesso');
