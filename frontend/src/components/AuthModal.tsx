import React, { useState } from 'react';
import { UserProfile, DEMO_USER, auth, googleProvider, signInWithEmailAndPassword, createUserWithEmailAndPassword, signInWithPopup } from '../config/firebase';
import { Lock, Mail, ShieldCheck, X, Sparkles, AlertCircle } from 'lucide-react';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onLoginSuccess: (user: UserProfile) => void;
}

export const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose, onLoginSuccess }) => {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) return;
    setLoading(true);
    setError(null);

    try {
      if (!auth) {
        onLoginSuccess({
          ...DEMO_USER,
          email: email || DEMO_USER.email,
          displayName: displayName || email.split('@')[0] || DEMO_USER.displayName
        });
        onClose();
        setLoading(false);
        return;
      }
      let fbUser;
      if (mode === 'login') {
        const userCredential = await signInWithEmailAndPassword(auth, email, password);
        fbUser = userCredential.user;
      } else {
        const userCredential = await createUserWithEmailAndPassword(auth, email, password);
        fbUser = userCredential.user;
      }

      const token = await fbUser.getIdToken();
      const userProfile: UserProfile = {
        uid: fbUser.uid,
        email: fbUser.email || email,
        displayName: fbUser.displayName || displayName || email.split('@')[0],
        tenantId: 'tenant_lawpedia_demo',
        token: token
      };

      onLoginSuccess(userProfile);
      onClose();
    } catch (err: any) {
      console.error("Firebase Authentication Error:", err);
      setError(err.message || 'Firebase authentication failed. Please check credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSignIn = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await signInWithPopup(auth, googleProvider);
      const fbUser = result.user;
      const token = await fbUser.getIdToken();
      const userProfile: UserProfile = {
        uid: fbUser.uid,
        email: fbUser.email || "google.user@lawpedia.io",
        displayName: fbUser.displayName || "Google Verified Counsel",
        tenantId: 'tenant_lawpedia_demo',
        photoURL: fbUser.photoURL || undefined,
        token: token
      };
      onLoginSuccess(userProfile);
      onClose();
    } catch (err: any) {
      console.error("Firebase Google Auth Error:", err);
      setError(err.message || 'Google sign-in failed.');
    } finally {
      setLoading(false);
    }
  };


  const handleInstantDemo = () => {
    onLoginSuccess(DEMO_USER);
    onClose();
  };

  let submitButtonText = 'Log In to Firebase Workspace';
  if (loading) {
    submitButtonText = 'Authenticating with Firebase SDK...';
  } else if (mode === 'register') {
    submitButtonText = 'Register Account';
  }

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl border border-slate-200 shadow-2xl w-full max-w-md p-6 space-y-5 animate-in fade-in zoom-in-95 duration-150">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-blue-600" />
            <h3 className="text-base font-bold text-slate-900">
              {mode === 'login' ? 'Firebase Authentication' : 'Register New Account'}
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-xl border border-slate-200 text-xs">
          <button
            onClick={() => { setMode('login'); setError(null); }}
            className={`flex-1 py-1.5 rounded-lg font-bold transition-all ${
              mode === 'login' ? 'bg-white text-blue-700 shadow-sm' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Log In
          </button>
          <button
            onClick={() => { setMode('register'); setError(null); }}
            className={`flex-1 py-1.5 rounded-lg font-bold transition-all ${
              mode === 'register' ? 'bg-white text-blue-700 shadow-sm' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Register
          </button>
        </div>

        {error && (
          <div className="bg-red-50 text-red-800 p-3 rounded-xl border border-red-200 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-red-600 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          {mode === 'register' && (
            <div>
              <label htmlFor="auth-display-name" className="font-semibold text-slate-700 block mb-1">Full Name / Counsel Title</label>
              <input
                id="auth-display-name"
                type="text"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                placeholder="e.g. Counsel Jane Doe"
                className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-slate-900 font-medium"
                required
              />
            </div>
          )}

          <div>
            <label htmlFor="auth-email" className="font-semibold text-slate-700 block mb-1">Email Address</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              <input
                id="auth-email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="counsel@enterprise.law"
                className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 pl-9 text-slate-900 font-medium"
                required
              />
            </div>
          </div>

          <div>
            <label htmlFor="auth-password" className="font-semibold text-slate-700 block mb-1">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              <input
                id="auth-password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 pl-9 text-slate-900 font-medium"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2.5 rounded-xl font-bold transition-all shadow-md shadow-blue-600/20 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {submitButtonText}
          </button>
        </form>

        <div className="space-y-2 pt-2 border-t border-slate-100">
          <button
            onClick={handleGoogleSignIn}
            disabled={loading}
            className="w-full bg-slate-50 hover:bg-slate-100 text-slate-800 border border-slate-200 py-2 rounded-xl font-bold text-xs transition-colors flex items-center justify-center gap-2"
          >
            <svg className="w-4 h-4" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
            </svg>
            Sign in with Google
          </button>

          <button
            onClick={handleInstantDemo}
            className="w-full bg-emerald-50 hover:bg-emerald-100 text-emerald-800 border border-emerald-200 py-2 rounded-xl font-bold text-xs transition-colors flex items-center justify-center gap-2"
          >
            <Sparkles className="w-4 h-4 text-emerald-600" /> Instant Demo Access (Pre-Configured)
          </button>
        </div>
      </div>
    </div>
  );
};
