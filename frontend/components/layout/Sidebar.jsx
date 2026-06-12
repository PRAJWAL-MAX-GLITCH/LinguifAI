"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, History, FileText, Settings, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';

const navigation = [
  { name: 'Translate', href: '/dashboard', icon: Sparkles },
  { name: 'History', href: '/dashboard/history', icon: History },
  { name: 'Documents', href: '/dashboard/documents', icon: FileText },
  { name: 'Settings', href: '/dashboard/settings', icon: Settings },
];

export default function Sidebar({ className }) {
  const pathname = usePathname();

  return (
    <div className={cn("flex h-full flex-col bg-muted/30 border-r", className)}>
      <div className="flex h-16 items-center border-b px-6">
        <Link href="/dashboard" className="flex items-center gap-2 font-bold text-xl tracking-tight">
          <Sparkles className="h-6 w-6 text-primary" />
          <span>LinguifAI</span>
        </Link>
      </div>
      <nav className="flex-1 space-y-1 p-4">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "group flex items-center rounded-md px-3 py-2.5 text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary text-primary-foreground shadow-sm"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              )}
            >
              <item.icon
                className={cn(
                  "mr-3 h-5 w-5 flex-shrink-0 transition-colors",
                  isActive ? "text-primary-foreground" : "text-muted-foreground group-hover:text-accent-foreground"
                )}
                aria-hidden="true"
              />
              {item.name}
            </Link>
          );
        })}
      </nav>
      <div className="border-t p-4">
        <div className="rounded-lg bg-primary/10 p-4">
          <h4 className="font-medium text-sm text-primary mb-1">AI Pro Plan</h4>
          <p className="text-xs text-muted-foreground mb-3">10k / 50k tokens used</p>
          <div className="h-2 w-full rounded-full bg-primary/20">
            <div className="h-2 rounded-full bg-primary" style={{ width: '20%' }} />
          </div>
        </div>
      </div>
    </div>
  );
}
