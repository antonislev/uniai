// frontend/src/main.tsx
import './index.css';
import { createRoot } from 'react-dom/client';
import { App } from './App';

const container = document.getElementById("root");
if (!container) throw new Error("Missing <div id='root'> in index.html");

createRoot(container).render(<App />);
