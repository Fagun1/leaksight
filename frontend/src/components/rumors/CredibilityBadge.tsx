"use client";

const GRADE_COLORS: Record<string, string> = {
  A: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300",
  B: "bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300",
  C: "bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300",
  D: "bg-orange-100 text-orange-800 dark:bg-orange-900/40 dark:text-orange-300",
  F: "bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300",
};

export default function CredibilityBadge({
  grade,
  score,
}: {
  grade?: string;
  score?: number;
}) {
  const g = (grade || (score != null && score >= 85 ? "A" : score >= 70 ? "B" : score >= 55 ? "C" : score >= 40 ? "D" : "F")).toUpperCase().slice(0, 1);
  const style = GRADE_COLORS[g] || GRADE_COLORS.C;
  return (
    <span className={`px-2 py-0.5 rounded text-xs font-medium ${style}`}>
      {grade ? `${grade}${score != null ? ` ${Math.round(score)}%` : ""}` : `${Math.round(score ?? 0)}%`}
    </span>
  );
}
