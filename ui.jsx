import { useRef, useState } from "react";
export const post = async (url, body) => { const r = await fetch(url, { method: "POST", ...(body instanceof FormData ? { body } : { headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }) }); if (!r.ok) throw new Error("Request failed"); return r.json(); };
export const Card = ({ title, children, className = "" }) => (<section className={`rounded-xl bg-white p-5 shadow-sm ring-1 ring-plum-900/5 ${className}`}>{title && <h3 className="mb-3 font-display text-lg font-bold">{title}</h3>}{children}</section>);
export const Bar = ({ label, value, max, unit = "g" }) => (<div className="mb-2"><div className="flex justify-between text-sm"><span>{label}</span><span className="font-medium">{value}{unit}</span></div><div className="h-2 rounded bg-plum-900/10"><div className="grow h-2 rounded bg-saffron" style={{ width: `${Math.min(100, (value / max) * 100)}%` }} /></div></div>);
export const Header = ({ title, sub }) => (<header className="mb-6"><h1 className="font-display text-3xl font-bold">{title}</h1><p className="mt-1 max-w-xl text-plum-700/80">{sub}</p></header>);

/* Upload / drag-drop / camera capture, then POST to `endpoint`; `render(result)` draws output. */
export function Analyzer({ endpoint, render, extra, accept = "image/*", label = "Analyze" }) {
  const [file, setFile] = useState(null), [busy, setBusy] = useState(false), [res, setRes] = useState(null), [err, setErr] = useState("");
  const [cam, setCam] = useState(false), vid = useRef(), input = useRef();
  const pick = f => { if (f) { setFile(f); setRes(null); setErr(""); } };
  const startCam = async () => { try { const s = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } }); setCam(true); setTimeout(() => { vid.current.srcObject = s; }, 50); } catch { setErr("Camera unavailable. Check browser permissions or upload a file."); } };
  const snap = () => { const v = vid.current, c = document.createElement("canvas"); c.width = v.videoWidth; c.height = v.videoHeight; c.getContext("2d").drawImage(v, 0, 0); v.srcObject.getTracks().forEach(t => t.stop()); setCam(false); c.toBlob(b => pick(new File([b], "capture.jpg", { type: "image/jpeg" })), "image/jpeg"); };
  const run = async () => { setBusy(true); setErr(""); const fd = new FormData(); fd.append("file", file); Object.entries(extra || {}).forEach(([k, v]) => fd.append(k, v)); try { const [r] = await Promise.all([post(endpoint, fd), new Promise(r => setTimeout(r, 1600))]); setRes(r); } catch { setErr("Analysis failed. Is the backend running on port 8000?"); } setBusy(false); };
  const url = file && URL.createObjectURL(file), isVid = file?.type.startsWith("video");
  const btn = "rounded-lg bg-white px-4 py-2 text-sm font-medium ring-1 ring-plum-900/15";
  return (<div className="grid gap-5 lg:grid-cols-[minmax(0,420px)_1fr]"><div>
    <div onDragOver={e => e.preventDefault()} onDrop={e => { e.preventDefault(); pick(e.dataTransfer.files[0]); }} className="relative flex aspect-[4/3] items-center justify-center overflow-hidden rounded-xl border-2 border-dashed border-plum-900/25 bg-white">
      {cam ? <video ref={vid} autoPlay playsInline className="h-full w-full object-cover" /> : url ? (isVid ? <video src={url} controls className="h-full w-full object-cover" /> : <img src={url} alt="Selected upload" className="h-full w-full object-cover" />) :
        <button onClick={() => input.current.click()} className="p-6 text-center text-plum-700/70">Drop a file here or <span className="font-bold underline">browse</span></button>}
      {busy && <div className="scanline" />}</div>
    <input ref={input} type="file" accept={accept} hidden onChange={e => pick(e.target.files[0])} />
    <div className="mt-3 flex flex-wrap gap-2">
      <button onClick={() => input.current.click()} className={btn}>Choose file</button>
      {cam ? <button onClick={snap} className="rounded-lg bg-plum-900 px-4 py-2 text-sm font-medium text-white">Take photo</button> : <button onClick={startCam} className={btn}>Use camera</button>}
      <button disabled={!file || busy} onClick={run} className="rounded-lg bg-saffron px-5 py-2 text-sm font-bold disabled:opacity-40">{busy ? "Scanning…" : label}</button></div>
    {err && <p role="alert" className="mt-3 text-sm text-red-700">{err}</p>}</div>
    <div>{res ? <div className="rise">{render(res)}</div> : <Card className="text-plum-700/70">{busy ? "Analyzing image…" : "Results appear here after you analyze an image."}</Card>}</div></div>);
}
