'use client';

import React, { useState } from 'react';
import {
  useReactTable,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  ColumnDef,
  flexRender,
  SortingState,
  ColumnFiltersState,
} from '@tanstack/react-table';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet';
import { Search, AlertCircle, Download, Mail, Plus } from 'lucide-react';
import { mockStudents, mockAttempts } from '@/data/mock-data';
import { Student } from '@/types';
import { formatDistanceToNow } from 'date-fns';
import { ProgressChart } from '@/components/dashboard/charts';

export default function StudentsPage() {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [selectedStudent, setSelectedStudent] = useState<Student | null>(null);

  const columns: ColumnDef<Student>[] = [
    {
      accessorKey: 'name',
      header: 'Student',
      cell: ({ row }) => (
        <div className="flex items-center gap-3">
          <Avatar className="h-8 w-8">
            <AvatarFallback>
              {row.original.name.split(' ').map((n) => n[0]).join('')}
            </AvatarFallback>
          </Avatar>
          <div>
            <div className="font-medium">{row.getValue('name')}</div>
            <div className="text-xs text-neutral-500">{row.original.className}</div>
          </div>
        </div>
      ),
    },
    {
      accessorKey: 'className',
      header: 'Class',
      cell: ({ row }) => <Badge variant="outline">{row.getValue('className')}</Badge>,
    },
    {
      accessorKey: 'lastLogin',
      header: 'Last Login',
      cell: ({ row }) => {
        const date = row.getValue('lastLogin') as Date | undefined;
        return date ? (
          <span className="text-sm">{formatDistanceToNow(date, { addSuffix: true })}</span>
        ) : (
          '—'
        );
      },
    },
    {
      accessorKey: 'totalAttempts',
      header: 'Attempts',
      cell: ({ row }) => <div className="text-center">{row.getValue('totalAttempts')}</div>,
    },
    {
      accessorKey: 'averageScore',
      header: 'Avg Score',
      cell: ({ row }) => {
        const score = row.getValue('averageScore') as number;
        return (
          <Badge
            variant={score >= 80 ? 'default' : score >= 60 ? 'secondary' : 'destructive'}
          >
            {score}%
          </Badge>
        );
      },
    },
    {
      accessorKey: 'needsHelp',
      header: 'Status',
      cell: ({ row }) => {
        const needsHelp = row.getValue('needsHelp') as boolean;
        return needsHelp ? (
          <div className="flex items-center gap-2 text-amber-600">
            <AlertCircle className="h-4 w-4" />
            <span className="text-sm">Needs Help</span>
          </div>
        ) : (
          <span className="text-sm text-green-600">On Track</span>
        );
      },
    },
    {
      id: 'actions',
      cell: ({ row }) => (
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setSelectedStudent(row.original)}
        >
          View Profile
        </Button>
      ),
    },
  ];

  const table = useReactTable({
    data: mockStudents,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    state: {
      sorting,
      columnFilters,
    },
    initialState: {
      pagination: {
        pageSize: 15,
      },
    },
  });

  // Get student's attempts for the profile drawer
  const studentAttempts = selectedStudent
    ? mockAttempts
        .filter((a) => a.studentId === selectedStudent.id)
        .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
    : [];

  const progressData = studentAttempts.slice(0, 10).reverse().map((a, idx) => ({
    date: `Day ${idx + 1}`,
    score: a.score,
  }));

  return (
    <div className="space-y-6 p-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Students</h1>
          <p className="mt-2 text-neutral-600 dark:text-neutral-400">
            Monitor student progress and identify those who need support
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" className="gap-2">
            <Download className="h-4 w-4" />
            Export CSV
          </Button>
          <Button className="gap-2">
            <Plus className="h-4 w-4" />
            Add Student
          </Button>
        </div>
      </div>

      {/* Filters and Bulk Actions */}
      <Card>
        <CardHeader>
          <CardTitle>All Students</CardTitle>
          <CardDescription>
            {mockStudents.length} students across {mockStudents.filter((s) => s.needsHelp).length} need help
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="mb-4 flex items-center gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-neutral-500" />
              <Input
                placeholder="Search students..."
                value={(table.getColumn('name')?.getFilterValue() as string) ?? ''}
                onChange={(event) =>
                  table.getColumn('name')?.setFilterValue(event.target.value)
                }
                className="pl-9"
              />
            </div>
            <Button variant="outline" className="gap-2">
              <Mail className="h-4 w-4" />
              Send Message
            </Button>
          </div>

          {/* Table */}
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                {table.getHeaderGroups().map((headerGroup) => (
                  <TableRow key={headerGroup.id}>
                    {headerGroup.headers.map((header) => (
                      <TableHead key={header.id}>
                        {header.isPlaceholder
                          ? null
                          : flexRender(
                              header.column.columnDef.header,
                              header.getContext()
                            )}
                      </TableHead>
                    ))}
                  </TableRow>
                ))}
              </TableHeader>
              <TableBody>
                {table.getRowModel().rows?.length ? (
                  table.getRowModel().rows.map((row) => (
                    <TableRow key={row.id}>
                      {row.getVisibleCells().map((cell) => (
                        <TableCell key={cell.id}>
                          {flexRender(
                            cell.column.columnDef.cell,
                            cell.getContext()
                          )}
                        </TableCell>
                      ))}
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={columns.length} className="h-24 text-center">
                      No results.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>

          {/* Pagination */}
          <div className="mt-4 flex items-center justify-between">
            <div className="text-sm text-neutral-600">
              Showing {table.getRowModel().rows.length} of {mockStudents.length} students
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => table.previousPage()}
                disabled={!table.getCanPreviousPage()}
              >
                Previous
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => table.nextPage()}
                disabled={!table.getCanNextPage()}
              >
                Next
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Student Profile Drawer */}
      <Sheet open={!!selectedStudent} onOpenChange={() => setSelectedStudent(null)}>
        <SheetContent className="sm:max-w-2xl overflow-y-auto">
          {selectedStudent && (
            <>
              <SheetHeader>
                <div className="flex items-center gap-3">
                  <Avatar className="h-12 w-12">
                    <AvatarFallback>
                      {selectedStudent.name.split(' ').map((n) => n[0]).join('')}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <SheetTitle>{selectedStudent.name}</SheetTitle>
                    <SheetDescription>
                      {selectedStudent.className} • Grade {selectedStudent.grade}
                    </SheetDescription>
                  </div>
                </div>
              </SheetHeader>

              <div className="mt-6 space-y-6">
                {/* Quick Stats */}
                <div className="grid grid-cols-3 gap-4">
                  <Card>
                    <CardContent className="pt-6">
                      <p className="text-2xl font-bold">{selectedStudent.totalAttempts}</p>
                      <p className="text-xs text-neutral-500">Total Attempts</p>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="pt-6">
                      <p className="text-2xl font-bold">{selectedStudent.averageScore}%</p>
                      <p className="text-xs text-neutral-500">Avg Score</p>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="pt-6">
                      <p className="text-2xl font-bold">{studentAttempts.length}</p>
                      <p className="text-xs text-neutral-500">This Week</p>
                    </CardContent>
                  </Card>
                </div>

                {/* Progress Chart */}
                {progressData.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-base">Progress Over Time</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ProgressChart data={progressData} />
                    </CardContent>
                  </Card>
                )}

                {/* Strengths & Weaknesses */}
                <div className="grid grid-cols-2 gap-4">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-base">Strengths</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="flex flex-wrap gap-2">
                        {selectedStudent.strengths.length > 0 ? (
                          selectedStudent.strengths.map((s) => (
                            <Badge key={s} variant="default">
                              {s}
                            </Badge>
                          ))
                        ) : (
                          <p className="text-sm text-neutral-500">No data yet</p>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-base">Needs Practice</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="flex flex-wrap gap-2">
                        {selectedStudent.weaknesses.length > 0 ? (
                          selectedStudent.weaknesses.map((w) => (
                            <Badge key={w} variant="destructive">
                              {w}
                            </Badge>
                          ))
                        ) : (
                          <p className="text-sm text-neutral-500">All good!</p>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Recent Activity */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Recent Activity</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {studentAttempts.slice(0, 5).map((attempt) => (
                        <div
                          key={attempt.id}
                          className="flex items-center justify-between rounded-lg border p-3"
                        >
                          <div>
                            <p className="text-sm font-medium">{attempt.strand}</p>
                            <p className="text-xs text-neutral-500">
                              {formatDistanceToNow(attempt.timestamp, { addSuffix: true })}
                            </p>
                          </div>
                          <Badge
                            variant={
                              attempt.score >= 80
                                ? 'default'
                                : attempt.score >= 60
                                ? 'secondary'
                                : 'destructive'
                            }
                          >
                            {attempt.score}%
                          </Badge>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </>
          )}
        </SheetContent>
      </Sheet>
    </div>
  );
}
