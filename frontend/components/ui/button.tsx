import { cn } from "@/lib/utils";
import { ButtonHTMLAttributes, forwardRef } from "react";

type Variant = "primary" | "secondary" | "ghost" | "outline";
type Size = "sm" | "md" | "lg";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
}

const variants: Record<Variant, string> = {
  primary:
    "bg-gradient-to-r from-sky-500 via-indigo-500 to-fuchsia-500 text-white hover:brightness-110 shadow-lg shadow-indigo-600/30 disabled:from-slate-600 disabled:via-slate-600 disabled:to-slate-600 disabled:shadow-none disabled:opacity-50",
  secondary:
    "bg-white/10 text-white border border-white/15 hover:bg-white/15 disabled:opacity-40",
  ghost: "text-slate-300 hover:bg-white/10 hover:text-white disabled:opacity-40",
  outline:
    "border border-white/15 bg-white/[0.03] text-slate-200 hover:bg-white/[0.08] hover:border-white/25",
};

const sizes: Record<Size, string> = {
  sm: "h-9 px-3 text-sm",
  md: "h-11 px-5 text-sm",
  lg: "h-12 px-6 text-base",
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", size = "md", ...props }, ref) => (
    <button
      ref={ref}
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-xl font-medium transition-all duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400/50 focus-visible:ring-offset-2 focus-visible:ring-offset-ink-950 disabled:cursor-not-allowed active:scale-[0.98]",
        variants[variant],
        sizes[size],
        className
      )}
      {...props}
    />
  )
);
Button.displayName = "Button";
