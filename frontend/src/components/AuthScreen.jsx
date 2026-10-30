import { useState } from 'react';

export function AuthScreen({ onLogin, onSignup }) {
  const [mode, setMode] = useState('login');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');

  const isSignup = mode === 'signup';

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');

    if (isSignup && name.trim().length < 2) {
      setError('Please enter your full name.');
      return;
    }

    if (password.length < 8) {
      setError('Password must contain at least 8 characters.');
      return;
    }

    if (isSignup && password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    try {
      if (isSignup) {
        await onSignup({ name: name.trim(), email: email.trim(), password });
      } else {
        await onLogin({ email: email.trim(), password });
      }
    } catch (err) {
      setError(err.message || 'Authentication failed. Please try again.');
    }
  };

  return (
    <main className="auth-page">
      <div className="auth-panel">
        <div className="auth-brand">
          <span className="auth-logo">ES</span>
          <span>EarnScore</span>
        </div>

        <div className="auth-content">
          <span className="auth-eyebrow">LENDER PORTAL</span>

          <h1>{isSignup ? 'Create your account' : 'Welcome back'}</h1>

          <p className="auth-description">
            {isSignup
              ? 'Create an account to access the EarnScore lending workspace.'
              : 'Sign in to access your underwriting workspace.'}
          </p>

          <form className="auth-form" onSubmit={handleSubmit}>
            {isSignup && (
              <label>
                Full name
                <input
                  type="text"
                  autoComplete="name"
                  value={name}
                  onChange={e => setName(e.target.value)}
                  placeholder="Enter your full name"
                  required
                />
              </label>
            )}

            <label>
              Email address
              <input
                type="email"
                autoComplete="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="Enter your email"
                required
              />
            </label>

            <label>
              Password
              <input
                type="password"
                autoComplete={isSignup ? 'new-password' : 'current-password'}
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="Enter your password"
                required
              />
            </label>

            {isSignup && (
              <label>
                Confirm password
                <input
                  type="password"
                  autoComplete="new-password"
                  value={confirmPassword}
                  onChange={e => setConfirmPassword(e.target.value)}
                  placeholder="Confirm your password"
                  required
                />
              </label>
            )}

            {error && <p className="auth-error" role="alert">{error}</p>}

            <button type="submit" className="auth-submit">
              {isSignup ? 'Create Account' : 'Sign In'}
            </button>
          </form>

          <p className="auth-switch">
            {isSignup ? 'Already have an account?' : "Don't have an account?"}
            {' '}
            <button
              type="button"
              onClick={() => {
                setMode(isSignup ? 'login' : 'signup');
                setError('');
              }}
            >
              {isSignup ? 'Sign In' : 'Create an account'}
            </button>
          </p>
        </div>

        <p className="auth-footer">
          © EarnScore · Explainable financial assessment
        </p>
      </div>

      <div className="auth-visual">
        <div className="auth-visual-content">
          <span className="auth-visual-label">FINANCIAL INTELLIGENCE</span>
          <h2>Better insights.
            <br />
            More informed decisions.</h2>
          <p>
            Understand gig-worker earnings, financial consistency
            and cash-flow evidence in one transparent workspace.
          </p>

          <div className="auth-feature-list">
            <span>✓ Transparent scoring factors</span>
            <span>✓ Earnings and cash-flow insights</span>
            <span>✓ Human-centered underwriting</span>
          </div>
        </div>
      </div>
    </main>
  );
}
