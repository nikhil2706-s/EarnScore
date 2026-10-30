const ACCOUNTS_KEY = 'earnscore_accounts_v1';
const SESSION_KEY = 'earnscore_session_v1';

function readAccounts() {
  try {
    return JSON.parse(localStorage.getItem(ACCOUNTS_KEY) || '{}');
  } catch {
    return {};
  }
}

async function hashPassword(password, salt) {
  const data = new TextEncoder().encode(`${salt}:${password}`);
  const hash = await crypto.subtle.digest('SHA-256', data);

  return Array.from(new Uint8Array(hash))
    .map(byte => byte.toString(16).padStart(2, '0'))
    .join('');
}

export async function signup({ name, email, password }) {
  const accounts = readAccounts();
  const normalizedEmail = email.trim().toLowerCase();

  if (accounts[normalizedEmail]) {
    throw new Error('An account with this email already exists.');
  }

  if (password.length < 8) {
    throw new Error('Password must contain at least 8 characters.');
  }

  const salt = crypto.randomUUID();
  const passwordHash = await hashPassword(password, salt);

  accounts[normalizedEmail] = {
    name: name.trim(),
    email: normalizedEmail,
    salt,
    passwordHash,
  };

  localStorage.setItem(ACCOUNTS_KEY, JSON.stringify(accounts));

  return { name: name.trim(), email: normalizedEmail };
}

export async function login({ email, password }) {
  const accounts = readAccounts();
  const normalizedEmail = email.trim().toLowerCase();
  const account = accounts[normalizedEmail];

  if (!account) {
    throw new Error('Invalid email or password.');
  }

  const passwordHash = await hashPassword(password, account.salt);

  if (passwordHash !== account.passwordHash) {
    throw new Error('Invalid email or password.');
  }

  const user = { name: account.name, email: account.email };
  sessionStorage.setItem(SESSION_KEY, JSON.stringify(user));

  return user;
}

export function getCurrentUser() {
  try {
    return JSON.parse(sessionStorage.getItem(SESSION_KEY) || 'null');
  } catch {
    return null;
  }
}

export function logout() {
  sessionStorage.removeItem(SESSION_KEY);
}
