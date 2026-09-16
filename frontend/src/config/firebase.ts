/* Lawpedia Real Firebase Authentication & Analytics SDK Integration */

import { initializeApp, getApps, getApp } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";

export interface UserProfile {
  uid: string;
  email: string;
  displayName: string;
  tenantId: string;
  photoURL?: string;
  token?: string;
}

// Scoped Demo User with valid server-side Bearer Token
export const DEMO_USER: UserProfile = {
  uid: "usr_lawpedia_demo_99",
  email: "counsel@enterprise.law",
  displayName: "Senior Legal Counsel",
  tenantId: "tenant_lawpedia_demo",
  photoURL: "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=100&auto=format&fit=crop&q=80",
  token: import.meta.env.VITE_LAWPEDIA_DEMO_TOKEN || "lawpedia_demo_token_2026"
};


const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || "",
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || "",
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || "",
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || "",
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || "",
  appId: import.meta.env.VITE_FIREBASE_APP_ID || "",
  measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID || ""
};

// Initialize Firebase safely with fallback for unconfigured/demo environments
let app: any = null;
let auth: any = null;
let googleProvider: any = null;

try {
  if (firebaseConfig.apiKey) {
    app = getApps().length > 0 ? getApp() : initializeApp(firebaseConfig);
    auth = getAuth(app);
    googleProvider = new GoogleAuthProvider();
  }
} catch (e) {
  console.warn("Firebase Auth initialized in offline/demo mode:", e);
}

export { app, auth, googleProvider };
export { signInWithEmailAndPassword, createUserWithEmailAndPassword, signInWithPopup, signOut as firebaseSignOut } from "firebase/auth";
