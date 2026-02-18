export function nextReviewDate(mastery: number, lapseCount: number) {
  const intervals = [1, 2, 4, 7, 14, 30];
  const safeMastery = Math.max(0, Math.min(5, mastery));
  const days = intervals[safeMastery] ?? 30;
  const penalty = lapseCount > 0 ? Math.min(lapseCount, 3) : 0;
  const next = new Date();
  next.setDate(next.getDate() + Math.max(1, days - penalty));
  return next;
}

export function dateKey(date: Date) {
  return date.toISOString().slice(0, 10);
}
