import { cn } from "@/lib/utils";

export function Field({
  label,
  hint,
  children,
  required,
}: {
  label: string;
  hint?: string;
  required?: boolean;
  children: React.ReactNode;
}) {
  return (
    <div className="space-y-2">
      <label className="flex items-center gap-1.5 text-sm font-medium text-slate-200">
        {label}
        {required && <span className="text-fuchsia-400">*</span>}
        {hint && <span className="font-normal text-slate-500">· {hint}</span>}
      </label>
      {children}
    </div>
  );
}

export function TextInput({
  className,
  ...props
}: React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={cn(
        "h-12 w-full rounded-2xl border border-white/10 bg-white/[0.02] px-4 text-sm text-slate-100 placeholder:text-slate-500 transition-all duration-300 ease-[cubic-bezier(0.32,0.72,0,1)] focus:border-white/30 focus:bg-white/[0.04] focus:outline-none focus:ring-4 focus:ring-white/5 [color-scheme:dark] shadow-[inset_0_1px_1px_rgba(255,255,255,0.02)]",
        className
      )}
      {...props}
    />
  );
}

export function TextArea({
  className,
  ...props
}: React.TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return (
    <textarea
      className={cn(
        "w-full rounded-xl border border-white/10 bg-white/[0.04] px-3.5 py-3 text-sm text-slate-100 placeholder:text-slate-500 transition-colors focus:border-indigo-400/60 focus:outline-none focus:ring-2 focus:ring-indigo-500/25 resize-none",
        className
      )}
      {...props}
    />
  );
}

interface OptionCardProps {
  selected: boolean;
  onClick: () => void;
  title: string;
  description?: string;
  icon?: React.ReactNode;
  className?: string;
}

export function OptionCard({
  selected,
  onClick,
  title,
  description,
  icon,
  className,
}: OptionCardProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "group flex items-start gap-4 rounded-[1.5rem] border p-4 text-left transition-all duration-500 ease-[cubic-bezier(0.32,0.72,0,1)]",
        selected
          ? "border-white/20 bg-white/[0.08] shadow-[inset_0_1px_1px_rgba(255,255,255,0.1)]"
          : "border-white/5 bg-white/[0.02] hover:border-white/15 hover:bg-white/[0.04]",
        className
      )}
    >
      {icon && (
        <span
          className={cn(
            "flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl text-xl transition-transform duration-500 ease-[cubic-bezier(0.32,0.72,0,1)] group-hover:scale-105",
            selected ? "bg-white/10 shadow-[inset_0_1px_1px_rgba(255,255,255,0.2)]" : "bg-white/5"
          )}
        >
          {icon}
        </span>
      )}
      <span className="space-y-1 mt-0.5">
        <span className="block text-sm font-semibold text-slate-100 transition-colors group-hover:text-white">
          {title}
        </span>
        {description && (
          <span className="block text-xs text-slate-400">{description}</span>
        )}
      </span>
    </button>
  );
}

export function Toggle({
  checked,
  onChange,
  label,
  description,
}: {
  checked: boolean;
  onChange: (v: boolean) => void;
  label: string;
  description?: string;
}) {
  return (
    <button
      type="button"
      onClick={() => onChange(!checked)}
      className="flex w-full items-center justify-between gap-4 rounded-xl border border-white/10 bg-white/[0.03] p-4 text-left transition-colors hover:bg-white/[0.06]"
    >
      <span className="space-y-0.5">
        <span className="block text-sm font-medium text-slate-200">{label}</span>
        {description && (
          <span className="block text-xs text-slate-400">{description}</span>
        )}
      </span>
      <span
        className={cn(
          "relative h-6 w-11 shrink-0 rounded-full transition-colors",
          checked
            ? "bg-gradient-to-r from-sky-500 to-fuchsia-500"
            : "bg-white/15"
        )}
      >
        <span
          className={cn(
            "absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform",
            checked ? "translate-x-[22px]" : "translate-x-0.5"
          )}
        />
      </span>
    </button>
  );
}
