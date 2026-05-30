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
    <div className="flex w-full items-start justify-between relative px-2">
      {/* Background Line */}
      <div className="absolute top-[18px] left-[10%] right-[10%] h-px bg-white/[0.05] -z-10" />

      {steps.map((label, i) => {
        const done = i < current;
        const active = i === current;
        const clickable = i <= maxReached;

        return (
          <div key={label} className="flex flex-col items-center flex-1">
            <button
              type="button"
              disabled={!clickable}
              onClick={() => clickable && onStepClick?.(i)}
              className={cn(
                "group relative flex flex-col items-center outline-none",
                clickable ? "cursor-pointer" : "cursor-not-allowed"
              )}
            >
              {/* Active Glow */}
              {active && (
                <div className="absolute top-0 h-9 w-9 rounded-full bg-white/20 blur-md" />
              )}

              {/* Number/Check Circle */}
              <span
                className={cn(
                  "relative flex h-9 w-9 items-center justify-center rounded-full text-sm font-semibold transition-all duration-500 ease-[cubic-bezier(0.32,0.72,0,1)] ring-4 ring-[#050505]",
                  done && "bg-white text-black",
                  active && "bg-white text-black shadow-[0_0_15px_rgba(255,255,255,0.3)]",
                  !done && !active && "bg-[#0a0a0a] text-slate-500 border border-white/10 group-hover:border-white/30"
                )}
              >
                {done ? <Check className="h-4 w-4" /> : i + 1}
              </span>

              {/* Label */}
              <span
                className={cn(
                  "mt-3 text-[13px] font-medium transition-colors duration-300 whitespace-nowrap",
                  active ? "text-white" : "text-slate-500",
                  done && "text-slate-300"
                )}
              >
                {label}
              </span>
            </button>
          </div>
        );
      })}
    </div>
  );
}
