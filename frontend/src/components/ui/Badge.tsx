import React from "react";
import { cn } from "@/lib/utils";

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?:
    | "default"
    | "success"
    | "warning"
    | "danger"
    | "info"
    | "purple"
    | "outline"
    | "synthetic";
}

export function Badge({ className, variant = "default", children, ...props }: BadgeProps) {
  const variantStyles = {
    default: "bg-surface-50 text-gray-300 border-border",
    success: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
    warning: "bg-amber-500/15 text-amber-400 border-amber-500/30",
    danger: "bg-rose-500/15 text-rose-400 border-rose-500/30",
    info: "bg-cyan-500/15 text-cyan-400 border-cyan-500/30",
    purple: "bg-brand-500/15 text-brand-400 border-brand-500/30",
    outline: "bg-transparent text-gray-400 border-border",
    synthetic: "bg-purple-900/30 text-purple-300 border-purple-500/40 font-mono text-[10px]",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium border uppercase tracking-wider",
        variantStyles[variant],
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
}

export function StatusBadge({ status }: { status: string }) {
  const norm = status?.toUpperCase() || "";
  if (norm === "ACCEPTED" || norm === "APPROVED" || norm === "QUALIFIED" || norm === "SUCCESS" || norm === "COMPLETED") {
    return <Badge variant="success">{status}</Badge>;
  }
  if (norm === "REVIEW_REQUIRED" || norm === "PROFILED" || norm === "DRAFT_PENDING_APPROVAL" || norm === "WARNING") {
    return <Badge variant="warning">{status}</Badge>;
  }
  if (norm === "REJECTED" || norm === "FAILED" || norm === "DISQUALIFIED") {
    return <Badge variant="danger">{status}</Badge>;
  }
  if (norm.includes("RUNNING")) {
    return <Badge variant="info">{status}</Badge>;
  }
  return <Badge variant="default">{status}</Badge>;
}

export function EvidenceBadge({ classification }: { classification: string }) {
  const norm = classification?.toUpperCase() || "";
  if (norm === "VERIFIED") return <Badge variant="success">VERIFIED</Badge>;
  if (norm === "INFERRED") return <Badge variant="warning">INFERRED</Badge>;
  return <Badge variant="outline">UNKNOWN</Badge>;
}
