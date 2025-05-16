// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";
import { getStorage } from "firebase/storage";
import { getAnalytics } from "firebase/analytics";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyDGJb_rG0A1zC187ls3iULHV0ktveMiiek",
  authDomain: "test-45111.firebaseapp.com",
  projectId: "test-45111",
  storageBucket: "test-45111.firebasestorage.app",
  messagingSenderId: "409666489615",
  appId: "1:409666489615:web:9c475700a6d847d0bd027a",
  measurementId: "G-VFWEJBZG34"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);

// Initialize Firebase services
const auth = getAuth(app);
const db = getFirestore(app);
const storage = getStorage(app);

export { auth, db, storage, analytics }; 