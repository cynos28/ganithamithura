'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Switch } from '@/components/ui/switch';
import { Slider } from '@/components/ui/slider';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Save, RotateCcw } from 'lucide-react';
import { ChartCard, MasteryBarChart } from '@/components/dashboard/charts';
import { mockMasteryData } from '@/data/mock-data';

interface UnitConfig {
  label: string;
  enabled: boolean;
}

interface StrandConfig {
  name: string;
  units: UnitConfig[];
  tolerance: number;
  hintsVisible: boolean;
  difficulty: 'easy' | 'medium' | 'hard';
}

interface DomainConfigProps {
  title: string;
  description: string;
  strands: StrandConfig[];
  accentColor: string;
}

export function DomainConfig({ title, description, strands, accentColor }: DomainConfigProps) {
  const [config, setConfig] = useState<StrandConfig[]>(strands);
  const [activeTab, setActiveTab] = useState(strands[0]?.name || '');
  const [profileName, setProfileName] = useState('');

  const updateStrand = (strandName: string, updates: Partial<StrandConfig>) => {
    setConfig((prev) =>
      prev.map((s) => (s.name === strandName ? { ...s, ...updates } : s))
    );
  };

  const toggleUnit = (strandName: string, unitLabel: string) => {
    setConfig((prev) =>
      prev.map((s) =>
        s.name === strandName
          ? {
              ...s,
              units: s.units.map((u) =>
                u.label === unitLabel ? { ...u, enabled: !u.enabled } : u
              ),
            }
          : s
      )
    );
  };

  const currentStrand = config.find((s) => s.name === activeTab);

  // Filter mastery data for this domain
  const domainMastery = mockMasteryData
    .filter((m) => strands.some((s) => s.name === m.strand))
    .map((m) => ({
      strand: m.strand,
      masteryPercentage: m.masteryPercentage,
      domain: m.domain,
    }));

  return (
    <div className="space-y-8 pb-8">
      {/* Page Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold text-neutral-900">{title}</h1>
        <p className="text-neutral-600 text-base">{description}</p>
      </div>

      <div className="grid gap-8 lg:grid-cols-3">
        {/* Configuration Panel */}
        <div className="lg:col-span-2 space-y-8">
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full h-auto p-1 gap-1" style={{ gridTemplateColumns: `repeat(${Math.min(strands.length, 4)}, 1fr)` }}>
              {strands.map((strand) => (
                <TabsTrigger key={strand.name} value={strand.name} className="py-3 capitalize">
                  {strand.name.replace(/-/g, ' ')}
                </TabsTrigger>
              ))}
            </TabsList>

            {config.map((strand) => (
              <TabsContent key={strand.name} value={strand.name} className="space-y-8 mt-8">
                {/* Unit Toggles */}
                <Card>
                  <CardHeader>
                    <CardTitle>Unit Selection</CardTitle>
                    <CardDescription>
                      Choose which units students can practice
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid gap-4 sm:grid-cols-2">
                      {strand.units.map((unit) => (
                        <div
                          key={unit.label}
                          className="flex items-center justify-between rounded-lg border p-4"
                        >
                          <Label htmlFor={`unit-${unit.label}`} className="cursor-pointer">
                            {unit.label}
                          </Label>
                          <Switch
                            id={`unit-${unit.label}`}
                            checked={unit.enabled}
                            onCheckedChange={() => toggleUnit(strand.name, unit.label)}
                          />
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Difficulty & Settings */}
                <Card>
                  <CardHeader>
                    <CardTitle>Difficulty Settings</CardTitle>
                    <CardDescription>
                      Adjust challenge level and support options
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-8 pt-2">
                    {/* Difficulty Presets */}
                    <div className="space-y-3">
                      <Label className="text-sm font-medium">Difficulty Level</Label>
                      <div className="flex gap-3">
                        {(['easy', 'medium', 'hard'] as const).map((level) => (
                          <Button
                            key={level}
                            variant={strand.difficulty === level ? 'default' : 'outline'}
                            size="default"
                            onClick={() => updateStrand(strand.name, { difficulty: level })}
                            className="flex-1"
                          >
                            {level.charAt(0).toUpperCase() + level.slice(1)}
                          </Button>
                        ))}
                      </div>
                    </div>

                    {/* Tolerance Slider */}
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <Label className="text-sm font-medium">Tolerance</Label>
                        <Badge variant="outline" className="px-3 py-1">{strand.tolerance}%</Badge>
                      </div>
                      <Slider
                        value={[strand.tolerance]}
                        onValueChange={([value]) =>
                          updateStrand(strand.name, { tolerance: value })
                        }
                        max={20}
                        step={1}
                        className="mt-2"
                      />
                      <p className="text-sm text-neutral-500">
                        Acceptable margin of error for measurements
                      </p>
                    </div>

                    {/* Hints Visibility */}
                    <div className="flex items-center justify-between p-4 rounded-lg border border-neutral-200 hover:bg-neutral-50 transition-colors">
                      <div className="flex-1">
                        <Label htmlFor={`hints-${strand.name}`} className="font-medium cursor-pointer">Show Hints</Label>
                        <p className="text-sm text-neutral-500 mt-1">
                          Allow students to request help
                        </p>
                      </div>
                      <Switch
                        id={`hints-${strand.name}`}
                        checked={strand.hintsVisible}
                        onCheckedChange={(checked) =>
                          updateStrand(strand.name, { hintsVisible: checked })
                        }
                      />
                    </div>
                  </CardContent>
                </Card>

                {/* Save as Lesson Profile */}
                <Card className="shadow-sm">
                  <CardHeader className="pb-4">
                    <CardTitle className="text-xl">Save Configuration</CardTitle>
                    <CardDescription className="text-base mt-1">
                      Save these settings as a reusable lesson profile
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="pt-2">
                    <div className="flex gap-3">
                      <Input
                        placeholder="Profile name (e.g., Week 1 - Length Basics)"
                        value={profileName}
                        onChange={(e) => setProfileName(e.target.value)}
                        className="flex-1"
                      />
                      <Button className="gap-2 px-6">
                        <Save className="h-4 w-4" />
                        Save
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            ))}
          </Tabs>
        </div>

        {/* Live Stats Sidebar */}
        <div className="space-y-6 lg:space-y-8">
          <Card className="shadow-sm">
            <CardHeader className="pb-4">
              <CardTitle className="text-xl">Current Performance</CardTitle>
              <CardDescription className="text-base mt-1 capitalize">
                {currentStrand?.name.replace(/-/g, ' ') || 'Select a strand'}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4 pt-2">
              <div className="rounded-lg border-l-4 border p-5 bg-neutral-50" style={{ borderLeftColor: accentColor }}>
                <p className="text-4xl font-bold text-neutral-900">
                  {mockMasteryData.find((m) => m.strand === currentStrand?.name)?.averageAccuracy || 0}%
                </p>
                <p className="text-sm text-neutral-600 mt-2">Current Class Accuracy</p>
              </div>

              <div className="rounded-lg border-l-4 border p-5 bg-neutral-50" style={{ borderLeftColor: accentColor }}>
                <p className="text-4xl font-bold text-neutral-900">
                  {mockMasteryData.find((m) => m.strand === currentStrand?.name)?.averageTimeOnTask || 0}s
                </p>
                <p className="text-sm text-neutral-600 mt-2">Avg Time on Task</p>
              </div>
            </CardContent>
          </Card>

          {domainMastery.length > 0 && (
            <ChartCard title="Mastery Overview" description="Performance across strands">
              <MasteryBarChart data={domainMastery} />
            </ChartCard>
          )}

          <div className="flex gap-3">
            <Button variant="outline" className="flex-1 gap-2 h-11">
              <RotateCcw className="h-4 w-4" />
              Reset
            </Button>
            <Button className="flex-1 gap-2 h-11" style={{ backgroundColor: accentColor }}>
              <Save className="h-4 w-4" />
              Apply
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
