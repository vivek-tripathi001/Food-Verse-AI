import { useState } from "react"; import Food from "./modules/Food.jsx"; import Freshness from "./modules/Freshness.jsx"; import Hygiene from "./modules/Hygiene.jsx"; import Planner from "./modules/Planner.jsx"; import Cook from "./modules/Cook.jsx";
const NAV = [["food", "Food & nutrition", Food], ["fresh", "Freshness", Freshness], ["hygiene", "Kitchen hygiene", Hygiene], ["plan", "Meal planner", Planner], ["cook", "Cooking assistant", Cook]];
export default function App() {
  const [id, setId] = useState("food"), [open, setOpen] = useState(false), View = NAV.find(n => n[0] === id)[2];
  return (<div className="min-h-screen lg:flex">
    <button onClick={() => setOpen(!open)} className="fixed left-3 top-3 z-30 rounded-lg bg-plum-900 px-3 py-2 text-sm text-white lg:hidden" aria-label="Toggle menu">Menu</button>
    <aside className={`fixed inset-y-0 left-0 z-20 w-64 bg-plum-900 p-5 text-white transition-transform lg:sticky lg:top-0 lg:h-screen lg:translate-x-0 ${open ? "" : "-translate-x-full"}`}>
      <div className="mb-8 mt-10 font-display text-2xl font-bold lg:mt-0">Food Verse <span className="text-saffron">AI</span></div>
      <nav className="space-y-1">{NAV.map(([k, t]) => <button key={k} onClick={() => { setId(k); setOpen(false); }} aria-current={id === k} className={`block w-full rounded-lg px-3 py-2.5 text-left text-sm transition-colors ${id === k ? "bg-saffron font-bold text-plum-900" : "text-white/75 hover:bg-plum-700"}`}>{t}</button>)}</nav></aside>
    <main className="min-w-0 flex-1 p-5 pt-16 lg:p-10"><div key={id} className="rise mx-auto max-w-6xl"><View /></div></main></div>);
}
