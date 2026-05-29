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
        "h-11 w-full rounded-xl border border-white/10 bg-white/[0.04] px-3.5 text-sm text-slate-100 placeholder:text-slate-500 transition-colors focus:border-indigo-400/60 focus:outline-none focus:ring-2 focus:ring-indigo-500/25 [color-scheme:dark]",
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
        "flex items-start gap-3 rounded-xl border p-4 text-left transition-all duration-150",
        selected
          ? "border-indigo-400/60 bg-gradient-to-br from-sky-500/10 via-indigo-500/10 to-fuchsia-500/10 ring-2 ring-indigo-500/30"
          : "border-white/10 bg-white/[0.03] hover:border-white/20 hover:bg-white/[0.06]",
        className
      )}
    >
      {icon && (
        <span
          className={cn(
            "flex h-10 w-10 shrink-0 items-center justify-center rounded-lg text-xl",
            selected ? "bg-white/10" : "bg-white/5"
          )}
        >
          {icon}
        </span>
      )}
      <span className="space-y-0.5">
        <span className="block text-sm font-semibold text-slate-100">
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
