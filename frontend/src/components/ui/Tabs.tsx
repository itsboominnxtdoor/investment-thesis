"use client";

import { useState } from "react";

interface Tab {
  id: string;
  label: string;
  content: React.ReactNode;
}

interface TabsProps {
  tabs: Tab[];
  defaultTab?: string;
}

export function Tabs({ tabs, defaultTab }: TabsProps) {
  const [active, setActive] = useState(defaultTab ?? tabs[0]?.id);
  const currentTab = tabs.find((t) => t.id === active);

  return (
    <div>
      {/* Tab navigation */}
      <div className="relative mb-6 overflow-x-auto">
        <div className="flex gap-1 rounded-xl bg-[var(--color-border-light)] p-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActive(tab.id)}
              className={`relative rounded-lg px-4 py-2.5 text-sm font-medium transition-all duration-200 ${
                active === tab.id
                  ? "text-[var(--color-text-primary)]"
                  : "text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
              }`}
            >
              {active === tab.id && (
                <div className="absolute inset-0 rounded-lg bg-[var(--color-surface)] shadow-sm"></div>
              )}
              <span className="relative z-10">{tab.label}</span>
            </button>
          ))}
        </div>
      </div>
      
      {/* Tab content with animation */}
      <div className="animate-fade-in">{currentTab?.content}</div>
    </div>
  );
}
