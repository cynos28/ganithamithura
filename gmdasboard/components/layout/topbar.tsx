'use client';

import React, { useState } from 'react';
import { Search, Bell, Calendar, ChevronDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet';
import { mockNotifications } from '@/data/mock-data';
import { formatDistanceToNow } from 'date-fns';
import { cn } from '@/lib/utils';

interface TopBarProps {
  className?: string;
}

export function TopBar({ className }: TopBarProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [dateRange, setDateRange] = useState('Last 7 days');
  const unreadCount = mockNotifications.filter((n) => !n.read).length;

  const currentUser = {
    name: 'Ms. Perera',
    email: 'perera@school.lk',
    avatar: undefined,
    initials: 'MP',
  };

  return (
    <header
      className={cn(
        'sticky top-0 z-30 flex h-16 items-center gap-4 border-b bg-white px-4 dark:bg-neutral-950 lg:px-6',
        className
      )}
    >
      {/* Logo for mobile when sidebar is closed */}
      <div className="flex items-center gap-2 lg:hidden">
        <span className="ml-12 text-sm font-bold">Ganitha Mithura</span>
      </div>

      {/* Search */}
      <div className="flex-1 lg:max-w-md">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-neutral-500" aria-hidden="true" />
          <Input
            type="search"
            placeholder="Search students, classes, assignments..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
            aria-label="Search"
          />
        </div>
      </div>

      {/* Date Range Picker */}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" className="hidden gap-2 md:flex" aria-label="Select date range">
            <Calendar className="h-4 w-4" aria-hidden="true" />
            <span>{dateRange}</span>
            <ChevronDown className="h-4 w-4" aria-hidden="true" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-48">
          <DropdownMenuLabel>Date Range</DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={() => setDateRange('Today')}>
            Today
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => setDateRange('Last 7 days')}>
            Last 7 days
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => setDateRange('Last 30 days')}>
            Last 30 days
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => setDateRange('This month')}>
            This month
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => setDateRange('Custom range')}>
            Custom range...
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Notifications */}
      <Sheet>
        <SheetTrigger asChild>
          <Button variant="ghost" size="icon" className="relative" aria-label={`Notifications (${unreadCount} unread)`}>
            <Bell className="h-5 w-5" aria-hidden="true" />
            {unreadCount > 0 && (
              <span className="absolute right-1 top-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-xs text-white">
                {unreadCount}
              </span>
            )}
          </Button>
        </SheetTrigger>
        <SheetContent>
          <SheetHeader>
            <SheetTitle>Notifications</SheetTitle>
            <SheetDescription>
              You have {unreadCount} unread notification{unreadCount !== 1 ? 's' : ''}
            </SheetDescription>
          </SheetHeader>
          <div className="mt-6 space-y-4">
            {mockNotifications.map((notification) => (
              <div
                key={notification.id}
                className={cn(
                  'rounded-lg border p-3 transition-colors hover:bg-neutral-50 dark:hover:bg-neutral-900',
                  !notification.read && 'border-blue-200 bg-blue-50 dark:border-blue-900 dark:bg-blue-950'
                )}
              >
                <div className="flex items-start gap-2">
                  <Badge
                    variant={
                      notification.type === 'error'
                        ? 'destructive'
                        : notification.type === 'warning'
                        ? 'secondary'
                        : 'default'
                    }
                    className="shrink-0"
                  >
                    {notification.type}
                  </Badge>
                  {!notification.read && (
                    <div className="mt-1 h-2 w-2 shrink-0 rounded-full bg-blue-500" aria-label="Unread" />
                  )}
                </div>
                <h4 className="mt-2 font-medium">{notification.title}</h4>
                <p className="mt-1 text-sm text-neutral-600 dark:text-neutral-400">
                  {notification.message}
                </p>
                <p className="mt-2 text-xs text-neutral-500">
                  {formatDistanceToNow(notification.timestamp, { addSuffix: true })}
                </p>
              </div>
            ))}
          </div>
        </SheetContent>
      </Sheet>

      {/* User Menu */}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" className="gap-2 pl-2" aria-label="User menu">
            <Avatar className="h-8 w-8">
              <AvatarImage src={currentUser.avatar} alt={currentUser.name} />
              <AvatarFallback>{currentUser.initials}</AvatarFallback>
            </Avatar>
            <span className="hidden font-medium lg:inline">{currentUser.name}</span>
            <ChevronDown className="hidden h-4 w-4 lg:inline" aria-hidden="true" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-56">
          <DropdownMenuLabel>
            <div className="flex flex-col">
              <span>{currentUser.name}</span>
              <span className="text-xs font-normal text-neutral-500">{currentUser.email}</span>
            </div>
          </DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuItem>Profile</DropdownMenuItem>
          <DropdownMenuItem>My Classes</DropdownMenuItem>
          <DropdownMenuItem>Preferences</DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem>Documentation</DropdownMenuItem>
          <DropdownMenuItem>Keyboard shortcuts</DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem className="text-red-600">Sign out</DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </header>
  );
}
