import { cn } from "@/lib/utils";
import { Check } from "lucide-react";

interface StepperProps {
  steps: string[];
  current: number;
  onStepClick?: (index: number) => void;
  maxReached: number;
}

export function Stepper({ steps, current, onStepClick, maxReached }: StepperProps) {
  return (
    <div className="flex items-center justify-between w-full">
      {steps.map((label, i) => {
        const done = i < current;
        const active = i === current;
        const clickable = i <= maxReached;
        return (
          <div key={label} className="flex items-center flex-1 last:flex-none">
            <button
              type="button"
              disabled={!clickable}
              onClick={() => clickable && onStepClick?.(i)}
              className={cn(
                "flex items-center gap-2.5 group",
                clickable ? "cursor-pointer" : "cursor-not-allowed"
              )}
            >
              <span
                className={cn(
                  "flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-sm font-semibold transition-all duration-200",
                  done && "bg-gradient-to-br from-sky-500 to-fuchsia-500 text-white",
                  active &&
                    "bg-gradient-to-br from-sky-500 to-fuchsia-500 text-white ring-4 ring-indigo-500/25",
                  !done && !active && "bg-white/[0.06] text-slate-500 border border-white/10"
                )}
              >
                {done ? <Check className="h-4 w-4" /> : i + 1}
              </span>
              <span
                className={cn(
                  "hidden text-sm font-medium sm:block transition-colors",
                  active ? "text-white" : "text-slate-500",
                  done && "text-slate-300"
                )}
              >
                {label}
              </span>
            </button>
            {i < steps.length - 1 && (
              <div className="mx-2 h-px flex-1 bg-white/10 sm:mx-4">
                <div
                  className={cn(
                    "h-full bg-gradient-to-r from-sky-500 to-fuchsia-500 transition-all duration-300",
                    done ? "w-full" : "w-0"
                  )}
                />
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
