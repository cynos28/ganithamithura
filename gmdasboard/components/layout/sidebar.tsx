'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Home,
  Users,
  GraduationCap,
  Ruler,
  Hash,
  Shapes,
  Calculator,
  FileText,
  ClipboardList,
  BookOpen,
  Video,
  BarChart3,
  Settings,
  HelpCircle,
  ChevronDown,
  ChevronRight,
  Menu,
  X,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';

export interface NavItem {
  title: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: number;
  children?: NavItem[];
}

const navigationItems: NavItem[] = [
  {
    title: 'Overview',
    href: '/',
    icon: Home,
  },
  {
    title: 'Classes',
    href: '/classes',
    icon: GraduationCap,
  },
  {
    title: 'Students',
    href: '/students',
    icon: Users,
  },
  {
    title: 'Math Domains',
    href: '/domains',
    icon: Calculator,
    children: [
      { title: 'Numbers', href: '/domains/numbers', icon: Hash },
      { title: 'Measurement', href: '/domains/measurement', icon: Ruler },
      { title: 'Shapes', href: '/domains/shapes', icon: Shapes },
      { title: 'Operations', href: '/domains/operations', icon: Calculator },
    ],
  },
  {
    title: 'Assignments',
    href: '/assignments',
    icon: ClipboardList,
  },
  {
    title: 'Assessments',
    href: '/assessments',
    icon: FileText,
  },
  {
    title: 'Content Library',
    href: '/content',
    icon: BookOpen,
  },
  {
    title: 'Live Session',
    href: '/live',
    icon: Video,
  },
  {
    title: 'Analytics & Reports',
    href: '/analytics',
    icon: BarChart3,
    children: [
      { title: 'By Class', href: '/analytics/class', icon: GraduationCap },
      { title: 'By Student', href: '/analytics/student', icon: Users },
      { title: 'By Skill', href: '/analytics/skill', icon: BarChart3 },
      { title: 'Retention', href: '/analytics/retention', icon: BarChart3 },
    ],
  },
  {
    title: 'Settings',
    href: '/settings',
    icon: Settings,
  },
  {
    title: 'Help',
    href: '/help',
    icon: HelpCircle,
  },
];

interface SidebarProps {
  className?: string;
}

export function Sidebar({ className }: SidebarProps) {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);
  const [expandedItems, setExpandedItems] = useState<string[]>([]);
  const [mobileOpen, setMobileOpen] = useState(false);

  const toggleExpanded = (title: string) => {
    setExpandedItems((prev) =>
      prev.includes(title)
        ? prev.filter((item) => item !== title)
        : [...prev, title]
    );
  };

  const renderNavItem = (item: NavItem, level = 0) => {
    const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
    const isExpanded = expandedItems.includes(item.title);
    const hasChildren = item.children && item.children.length > 0;

    return (
      <div key={item.href} className="w-full">
        <div
          className={cn(
            'group relative flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
            level > 0 && 'ml-4',
            isActive
              ? 'bg-neutral-100 text-neutral-900 dark:bg-neutral-800 dark:text-neutral-50'
              : 'text-neutral-600 hover:bg-neutral-50 hover:text-neutral-900 dark:text-neutral-400 dark:hover:bg-neutral-800 dark:hover:text-neutral-50'
          )}
          role="menuitem"
          aria-haspopup={hasChildren ? 'menu' : undefined}
          aria-expanded={hasChildren ? isExpanded : undefined}
        >
          {hasChildren ? (
            <button
              onClick={() => toggleExpanded(item.title)}
              className="flex flex-1 items-center gap-3"
              aria-label={`${item.title} menu`}
            >
              <item.icon className="h-5 w-5 shrink-0" aria-hidden="true" />
              {!collapsed && (
                <>
                  <span className="flex-1 text-left">{item.title}</span>
                  {isExpanded ? (
                    <ChevronDown className="h-4 w-4" aria-hidden="true" />
                  ) : (
                    <ChevronRight className="h-4 w-4" aria-hidden="true" />
                  )}
                </>
              )}
            </button>
          ) : (
            <Link href={item.href} className="flex flex-1 items-center gap-3">
              <item.icon className="h-5 w-5 shrink-0" aria-hidden="true" />
              {!collapsed && <span className="flex-1">{item.title}</span>}
              {!collapsed && item.badge && (
                <span className="flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-xs text-white">
                  {item.badge}
                </span>
              )}
            </Link>
          )}
        </div>

        {hasChildren && isExpanded && !collapsed && (
          <div role="menu" aria-label={`${item.title} submenu`} className="mt-1 space-y-1">
            {item.children!.map((child) => renderNavItem(child, level + 1))}
          </div>
        )}
      </div>
    );
  };

  const sidebarContent = (
    <>
      <div className="flex h-16 items-center justify-between border-b px-4">
        {!collapsed && (
          <Link href="/" className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-linear-to-br from-blue-500 to-purple-600">
              <Calculator className="h-5 w-5 text-white" />
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-bold">Ganitha Mithura</span>
              <span className="text-xs text-neutral-500">Teacher Dashboard</span>
            </div>
          </Link>
        )}
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setCollapsed(!collapsed)}
          className="hidden lg:flex"
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? <ChevronRight className="h-5 w-5" /> : <X className="h-5 w-5" />}
        </Button>
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setMobileOpen(false)}
          className="lg:hidden"
          aria-label="Close menu"
        >
          <X className="h-5 w-5" />
        </Button>
      </div>

      <ScrollArea className="flex-1 px-3 py-4">
        <nav role="menubar" aria-label="Main navigation" className="space-y-1">
          {navigationItems.map((item) => renderNavItem(item))}
        </nav>
      </ScrollArea>

      <Separator />

      <div className="p-4">
        {!collapsed && (
          <div className="rounded-lg bg-linear-to-br from-blue-50 to-purple-50 p-4 dark:from-blue-950 dark:to-purple-950">
            <p className="text-sm font-medium">Need Help?</p>
            <p className="mt-1 text-xs text-neutral-600 dark:text-neutral-400">
              Check our documentation or contact support
            </p>
            <Button variant="outline" size="sm" className="mt-3 w-full">
              Get Support
            </Button>
          </div>
        )}
      </div>
    </>
  );

  return (
    <>
      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setMobileOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Mobile menu button */}
      <Button
        variant="ghost"
        size="icon"
        className="fixed left-4 top-4 z-50 lg:hidden"
        onClick={() => setMobileOpen(true)}
        aria-label="Open menu"
      >
        <Menu className="h-6 w-6" />
      </Button>

      {/* Sidebar for desktop */}
      <aside
        className={cn(
          'hidden lg:flex lg:flex-col border-r bg-white dark:bg-neutral-950 transition-all duration-300',
          collapsed ? 'lg:w-20' : 'lg:w-64',
          className
        )}
      >
        {sidebarContent}
      </aside>

      {/* Sidebar for mobile */}
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r bg-white dark:bg-neutral-950 transition-transform duration-300 lg:hidden',
          mobileOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {sidebarContent}
      </aside>
    </>
  );
}
