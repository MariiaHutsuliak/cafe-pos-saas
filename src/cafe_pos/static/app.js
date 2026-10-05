const TOKEN_KEY = 'cafe_pos_token';

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

function isLoggedIn() {
  return !!getToken();
}

function getRole() {
  const token = getToken();
  if (!token) return null;
  try {
    const base64 = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
    const payload = JSON.parse(atob(base64));
    return payload.role || null;
  } catch (e) {
    return null;
  }
}

function isAdmin() {
  return getRole() === 'admin';
}

function authHeaders() {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function errorFrom(response) {
  try {
    const data = await response.json();
    return data.detail || `Помилка ${response.status}`;
  } catch (e) {
    return `Помилка ${response.status}`;
  }
}

async function apiGet(path) {
  const res = await fetch(path, { headers: { ...authHeaders() } });
  if (!res.ok) throw new Error(await errorFrom(res));
  return res.json();
}

async function apiPost(path, body) {
  const res = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await errorFrom(res));
  return res.json();
}

async function apiPut(path, body) {
  const res = await fetch(path, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await errorFrom(res));
  return res.json();
}

async function apiDelete(path) {
  const res = await fetch(path, {
    method: 'DELETE',
    headers: { ...authHeaders() },
  });
  if (!res.ok) throw new Error(await errorFrom(res));
  if (res.status === 204) return null;
  return res.json().catch(() => null);
}

async function login(email, password) {
  const form = new URLSearchParams();
  form.append('username', email);
  form.append('password', password);
  const res = await fetch('/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: form,
  });
  if (!res.ok) throw new Error(await errorFrom(res));
  const data = await res.json();
  setToken(data.access_token);
  return data;
}

function logout() {
  clearToken();
  window.location.href = 'index.html';
}

function showError(message) {
  const el = document.getElementById('error-msg');
  if (!el) return;
  el.textContent = message;
  el.style.display = 'block';
}

function hideError() {
  const el = document.getElementById('error-msg');
  if (!el) return;
  el.style.display = 'none';
  el.textContent = '';
}

function renderNav(activePage) {
  const nav = document.createElement('nav');
  nav.className = 'topnav';

  const links = [];
  if (isAdmin()) {
    links.push({ href: 'dashboard.html', label: 'Дашборд', page: 'dashboard' });
    links.push({ href: 'sales.html', label: 'Продажі', page: 'sales' });
  }
  links.push({ href: 'products.html', label: 'Товари', page: 'products' });
  links.push({ href: 'cafes.html', label: "Кав'ярні", page: 'cafes' });

  const linksHtml = links
    .map(l => `<a href="${l.href}" class="${l.page === activePage ? 'active' : ''}">${l.label}</a>`)
    .join('');

  const authHtml = isLoggedIn()
    ? `<span class="badge">${isAdmin() ? 'Адмін' : 'Користувач'}</span><button class="secondary" onclick="logout()">Вийти</button>`
    : `<a href="index.html">Увійти</a>`;

  nav.innerHTML = `<div class="nav-links">${linksHtml}</div><div class="nav-auth">${authHtml}</div>`;
  document.body.prepend(nav);
}