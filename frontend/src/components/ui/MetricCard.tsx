import React from "react";
import { cn } from "@/lib/utils";
import { Card } from "./Card";

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ElementType;
  trend?: string;
  trendPositive?: boolean;
  className?: string;
}

export function MetricCard({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  trendPositive,
  className,
}: MetricCardProps) {
  return (
    <Card className={cn("relative overflow-hidden", className)}>
      <div className="flex items-start justify-between">
        <div>
          <span className="text-[11px] font-mono text-gray-400 uppercase tracking-wider block mb-1">
            {title}
          </span>
          <div className="text-2xl font-bold tracking-tight text-white">{value}</div>
          {subtitle && <p className="text-xs text-gray-400 mt-1">{subtitle}</p>}
        </div>
        {Icon && (
          <div className="w-8 h-8 rounded-md bg-surface-50 border border-border flex items-center justify-center text-gray-400">
            <Icon className="w-4 h-4 text-brand-400" />
          </div>
        )}
      </div>

      {trend && (
        <div className="mt-3 pt-2.5 border-t border-border/60 flex items-center gap-1.5 text-xs">
          <span
            className={cn(
              "font-mono font-medium",
              trendPositive ? "text-emerald-400" : "text-amber-400"
            )}
          >
            {trend}
          </span>
        </div>
      )}
    </Card>
  );
}
