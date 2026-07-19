
const API_BASE_URL = '/api';

const ApiClient = {
  get token() { return localStorage.getItem('av_token'); },
  set token(value) {
    if (value) localStorage.setItem('av_token', value);
    else localStorage.removeItem('av_token');
  },
  get curator() {
    try { return JSON.parse(localStorage.getItem('av_curator') || 'null'); }
    catch (e) { return null; }
  },
  set curator(value) {
    if (value) localStorage.setItem('av_curator', JSON.stringify(value));
    else localStorage.removeItem('av_curator');
  },
  get isLoggedIn() { return !!this.token; },

  async _request(path, { method = 'GET', body = null, auth = false, isForm = false } = {}) {
    const headers = {};
    if (!isForm) headers['Content-Type'] = 'application/json';
    if (auth && this.token) headers['Authorization'] = 'Token ' + this.token;

    const res = await fetch(API_BASE_URL + path, {
      method,
      headers,
      body: body ? (isForm ? body : JSON.stringify(body)) : null,
    });

    let data = null;
    const contentType = res.headers.get('content-type') || '';
    if (contentType.includes('application/json')) {
      data = await res.json();
    } else {
      data = await res.text();
    }

    if (!res.ok) {
      const message = (data && data.detail) ? data.detail : 'Request failed (' + res.status + ')';
      const err = new Error(message);
      err.status = res.status;
      err.data = data;
      throw err;
    }
    return data;
  },

  // ---------- Curators / Auth ----------
  register(payload) { return this._request('/curators/register/', { method: 'POST', body: payload }); },
  async login(email, password) {
    const data = await this._request('/curators/login/', { method: 'POST', body: { email, password } });
    this.token = data.token;
    this.curator = data.curator;
    return data;
  },
  async logout() {
    try { await this._request('/curators/logout/', { method: 'POST', auth: true }); }
    finally { this.token = null; this.curator = null; }
  },
  me() { return this._request('/curators/me/', { auth: true }); },
  listCurators() { return this._request('/curators/', { auth: true }); },

  // ---------- Artifacts ----------
  getArtifacts(params = {}) {
    const qs = new URLSearchParams(Object.entries(params).filter(([, v]) => v));
    return this._request('/artifacts/?' + qs.toString());
  },
  getArtifact(id) { return this._request('/artifacts/' + encodeURIComponent(id) + '/'); },
  getArtifactStats() { return this._request('/artifacts/stats/'); },
  createArtifact(payload) { return this._request('/artifacts/', { method: 'POST', body: payload, auth: true }); },
  updateArtifact(id, payload) { return this._request('/artifacts/' + id + '/', { method: 'PATCH', body: payload, auth: true }); },
  deleteArtifact(id) { return this._request('/artifacts/' + id + '/', { method: 'DELETE', auth: true }); },
  exportArtifactsCsvUrl() { return API_BASE_URL + '/artifacts/export/'; },
  async importArtifactsCsv(file) {
    const formData = new FormData();
    formData.append('file', file);
    return this._request('/artifacts/import/', { method: 'POST', body: formData, auth: true, isForm: true });
  },
  getImportStatus(jobId) { return this._request('/artifacts/import/status/' + jobId + '/', { auth: true }); },

  // ---------- Loans ----------
  getLoans(params = {}) {
    const qs = new URLSearchParams(Object.entries(params).filter(([, v]) => v));
    return this._request('/loans/?' + qs.toString(), { auth: true });
  },
  getLoan(id) { return this._request('/loans/' + id + '/', { auth: true }); },
  createLoan(payload) { return this._request('/loans/', { method: 'POST', body: payload, auth: true }); },
  returnLoan(id) { return this._request('/loans/' + id + '/return/', { method: 'PATCH', auth: true }); },
  getLoanSummary() { return this._request('/loans/summary/', { auth: true }); },
  exportLoansCsvUrl() { return API_BASE_URL + '/loans/export/'; },

  // ---------- Health check ----------
  async isBackendOnline() {
    try {
      await this._request('/artifacts/stats/');
      return true;
    } catch (e) {
      return false;
    }
  },
};
