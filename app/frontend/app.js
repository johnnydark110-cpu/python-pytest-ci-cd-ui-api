const API_BASE = "";
const TOKEN_KEY = "order_app_token";

let authMode = "login";
let currentPage = 1;
let editingId = null;

function $(id) {
  return document.getElementById(id);
}

function escapeHtml(value) {
  const map = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  };
  return String(value).replace(/[&<>"']/g, (char) => map[char]);
}

function authHeaders() {
  return {
    "Content-Type": "application/json",
    Authorization: "Bearer " + localStorage.getItem(TOKEN_KEY),
  };
}

function switchAuthMode() {
  authMode = authMode === "login" ? "register" : "login";
  $("auth-title").textContent = authMode === "login" ? "登录" : "注册";
  $("auth-submit").textContent = authMode === "login" ? "登录" : "注册";
  $("auth-switch").textContent =
    authMode === "login" ? "没有账号？去注册" : "已有账号？去登录";
  $("auth-message").textContent = "";
}

async function submitAuth(event) {
  event.preventDefault();
  const username = $("username").value.trim();
  const password = $("password").value;
  const path = authMode === "login" ? "/api/auth/login" : "/api/auth/register";
  const response = await fetch(API_BASE + path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  let data = {};
  try {
    data = await response.json();
  } catch (_) {
    data = {};
  }
  if (!response.ok) {
    $("auth-message").textContent =
      typeof data.detail === "string" ? data.detail : "请求失败";
    return;
  }
  localStorage.setItem(TOKEN_KEY, data.token);
  $("user-greeting").textContent = `你好，${data.username}（${data.role}）`;
  $("auth-form").reset();
  refreshUI();
}

async function loadOrders() {
  const q = $("search-input").value.trim();
  const params = new URLSearchParams({ page: currentPage, page_size: 5 });
  if (q) params.set("q", q);
  const response = await fetch(API_BASE + "/api/orders?" + params.toString(), {
    headers: authHeaders(),
  });
  if (response.status === 401) {
    logout();
    return;
  }
  const data = await response.json();
  const tbody = $("order-list");
  tbody.innerHTML = "";
  for (const item of data.items) {
    const tr = document.createElement("tr");
    tr.dataset.testid = "order-item";
    tr.innerHTML = `
      <td>${item.id}</td>
      <td>${escapeHtml(item.title)}</td>
      <td>${item.amount}</td>
      <td>${escapeHtml(item.status)}</td>
      <td>${escapeHtml(item.created_at)}</td>
      <td>
        <button data-action="edit" data-id="${item.id}" data-testid="order-edit-button">编辑</button>
        <button data-action="delete" data-id="${item.id}" data-testid="order-delete-button">删除</button>
      </td>`;
    tbody.appendChild(tr);
  }
  const totalPages = Math.max(1, Math.ceil(data.total / data.page_size));
  $("page-info").textContent = `第 ${data.page} / ${totalPages} 页，共 ${data.total} 条`;
}

function resetOrderForm() {
  editingId = null;
  $("order-form").reset();
  $("order-create-submit").textContent = "新增订单";
}

async function submitOrder(event) {
  event.preventDefault();
  const payload = {
    title: $("order-title").value.trim(),
    amount: Number($("order-amount").value),
    status: $("order-status").value,
  };
  const url = editingId
    ? API_BASE + "/api/orders/" + editingId
    : API_BASE + "/api/orders";
  const method = editingId ? "PUT" : "POST";
  const response = await fetch(url, {
    method,
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    alert(typeof data.detail === "string" ? data.detail : "请求失败");
    return;
  }
  resetOrderForm();
  loadOrders();
}

async function deleteOrder(id) {
  if (!confirm(`确定删除订单 #${id} 吗？`)) return;
  const response = await fetch(API_BASE + "/api/orders/" + id, {
    method: "DELETE",
    headers: authHeaders(),
  });
  if (response.status === 401) {
    logout();
    return;
  }
  if (!response.ok) alert("删除失败");
  loadOrders();
}

async function editOrder(id) {
  const response = await fetch(API_BASE + "/api/orders/" + id, {
    headers: authHeaders(),
  });
  if (!response.ok) return;
  const order = await response.json();
  editingId = order.id;
  $("order-title").value = order.title;
  $("order-amount").value = order.amount;
  $("order-status").value = order.status;
  $("order-create-submit").textContent = "保存修改";
  $("order-title").focus();
}

function logout() {
  localStorage.removeItem(TOKEN_KEY);
  refreshUI();
}

function refreshUI() {
  const loggedIn = Boolean(localStorage.getItem(TOKEN_KEY));
  $("auth-panel").hidden = loggedIn;
  $("orders-panel").hidden = !loggedIn;
  $("user-bar").hidden = !loggedIn;
  if (loggedIn) loadOrders();
}

document.addEventListener("DOMContentLoaded", () => {
  $("auth-form").addEventListener("submit", submitAuth);
  $("auth-switch").addEventListener("click", (event) => {
    event.preventDefault();
    switchAuthMode();
  });
  $("order-form").addEventListener("submit", submitOrder);
  $("search-button").addEventListener("click", () => {
    currentPage = 1;
    loadOrders();
  });
  $("logout-button").addEventListener("click", logout);
  $("prev-page").addEventListener("click", () => {
    if (currentPage > 1) {
      currentPage -= 1;
      loadOrders();
    }
  });
  $("next-page").addEventListener("click", () => {
    currentPage += 1;
    loadOrders();
  });
  $("order-list").addEventListener("click", async (event) => {
    const button = event.target.closest("button[data-action]");
    if (!button) return;
    if (button.dataset.action === "delete") await deleteOrder(button.dataset.id);
    if (button.dataset.action === "edit") await editOrder(button.dataset.id);
  });
  refreshUI();
});
