import { cn } from "@/lib/utils";

export function Card({
  className,
  children,
  outerClassName,
}: {
  className?: string;
  outerClassName?: string;
  children: React.ReactNode;
}) {
  return (
    <div
      className={cn(
        "rounded-[2rem] border border-white/5 bg-black/40 p-2 backdrop-blur-2xl shadow-2xl shadow-black/50",
        outerClassName
      )}
    >
      <div
        className={cn(
          "h-full w-full rounded-[calc(2rem-0.5rem)] border border-white/10 bg-[#0a0a0a]/80 shadow-[inset_0_1px_1px_rgba(255,255,255,0.08)]",
          className
        )}
      >
        {children}
      </div>
    </div>
  );
}
