"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Radio,
  Building2,
  DollarSign,
  Cpu,
  Mail,
  Network,
  History,
  Settings,
  ShieldAlert,
  ChevronRight,
  Terminal,
  Compass,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface NavItem {
  name: string;
  href: string;
  icon: React.ElementType;
  badge?: string;
}

const navSections: Array<{ title: string; items: NavItem[] }> = [
  {
    title: "WORKSPACE",
    items: [
      { name: "Overview", href: "/", icon: LayoutDashboard },
      { name: "Signal Monitor", href: "/signals", icon: Radio },
      { name: "Companies", href: "/companies", icon: Building2 },
    ],
  },
  {
    title: "INTELLIGENCE",
    items: [
      { name: "Crustdata Explorer", href: "/explorer", icon: Compass, badge: "AI" },
      { name: "Financial Analysis", href: "/financials", icon: DollarSign },
      { name: "Migration Architect", href: "/architect", icon: Cpu },
      { name: "Outreach Studio", href: "/outreach", icon: Mail },
    ],
  },
  {
    title: "SYSTEM",
    items: [
      { name: "Agent Monitor", href: "/agents", icon: Network },
      { name: "Execution History", href: "/history", icon: History },
      { name: "Settings", href: "/settings", icon: Settings },
    ],
  },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 border-r border-border bg-surface-200/90 flex flex-col shrink-0 h-screen sticky top-0 select-none z-30">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-5 border-b border-border/80 gap-3">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-brand-600 to-accent-cyan flex items-center justify-center shadow-lg shadow-brand-500/20">
          <ShieldAlert className="w-5 h-5 text-white" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="font-bold text-sm tracking-wide text-white uppercase">Churn Poacher</span>
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-brand-500/20 text-brand-400 border border-brand-500/30">
              v1.0
            </span>
          </div>
          <span className="text-[11px] text-gray-400 block tracking-tight">Deposition Intelligence</span>
        </div>
      </div>

      {/* Navigation Sections */}
      <div className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
        {navSections.map((section) => (
          <div key={section.title} className="space-y-1">
            <div className="px-3 text-[10px] font-semibold text-gray-400 tracking-wider uppercase font-mono mb-2">
              {section.title}
            </div>
            {section.items.map((item) => {
              const Icon = item.icon;
              const isActive =
                item.href === "/"
                  ? pathname === "/"
                  : pathname === item.href || pathname.startsWith(`${item.href}/`);

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex items-center justify-between px-3 py-2 rounded-md text-xs font-medium transition-all group",
                    isActive
                      ? "bg-brand-500/15 text-white font-semibold border-l-2 border-brand-400 pl-2.5"
                      : "text-gray-400 hover:text-gray-200 hover:bg-surface-100"
                  )}
                >
                  <div className="flex items-center gap-2.5">
                    <Icon
                      className={cn(
                        "w-4 h-4 transition-colors",
                        isActive ? "text-brand-400" : "text-gray-400 group-hover:text-gray-300"
                      )}
                    />
                    <span>{item.name}</span>
                  </div>
                  {isActive && <ChevronRight className="w-3.5 h-3.5 text-brand-400/80" />}
                </Link>
              );
            })}
          </div>
        ))}
      </div>

      {/* Target Competitive Footprint Banner */}
      <div className="p-3 m-3 rounded-lg bg-surface-100/70 border border-border/80">
        <div className="flex items-center justify-between mb-1.5">
          <span className="text-[10px] font-mono text-gray-400 uppercase">Target Takeout</span>
          <span className="flex h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
        </div>
        <div className="text-xs font-semibold text-gray-200">Datadog &rarr; SigNoz / Grafana</div>
        <p className="text-[11px] text-gray-400 mt-1">Autonomous customer deposition pipeline active.</p>
      </div>
    </aside>
  );
}
