export default function NewPhrasePage() {
  return (
    <form action="/api/admin/phrases" method="post" className="space-y-2 rounded border border-slate-800 p-4">
      <h2 className="text-xl font-semibold">Create phrase equivalent</h2>
      <input name="phraseEn" placeholder="English phrase" className="w-full rounded bg-slate-800 p-2" required />
      <input name="phraseEs" placeholder="Spanish phrase" className="w-full rounded bg-slate-800 p-2" required />
      <input name="literalTranslation" placeholder="Literal translation (optional)" className="w-full rounded bg-slate-800 p-2" />
      <textarea name="explanation" placeholder="Functional equivalent explanation" className="h-24 w-full rounded bg-slate-800 p-2" required />
      <input name="tags" placeholder="comma,separated,tags" className="w-full rounded bg-slate-800 p-2" required />
      <button className="rounded bg-indigo-600 px-3 py-2">Create</button>
    </form>
  );
}
