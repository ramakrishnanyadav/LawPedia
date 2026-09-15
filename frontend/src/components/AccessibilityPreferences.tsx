import React from 'react';
import { Sliders, X, Type, Sparkles } from 'lucide-react';

export interface AccessibilitySettings {
  textScale: number; // 100 to 200
  highContrast: boolean;
  reduceMotion: boolean;
  dyslexiaFont: boolean;
  readingLevel: 'simple' | 'standard';
  disable3DGraph: boolean;
}

interface AccessibilityPreferencesProps {
  isOpen: boolean;
  onClose: () => void;
  settings: AccessibilitySettings;
  onUpdateSettings: (newSettings: AccessibilitySettings) => void;
}

export const AccessibilityPreferences: React.FC<AccessibilityPreferencesProps> = ({
  isOpen,
  onClose,
  settings,
  onUpdateSettings
}) => {
  if (!isOpen) return null;

  const handleChange = (key: keyof AccessibilitySettings, value: any) => {
    const updated = { ...settings, [key]: value };
    onUpdateSettings(updated);
    localStorage.setItem('lawpedia_a11y_settings', JSON.stringify(updated));
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl border border-slate-200 shadow-2xl w-full max-w-lg p-6 space-y-6 animate-in fade-in zoom-in-95 duration-150">
        <div className="flex items-center justify-between border-b border-slate-100 pb-4">
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Sliders className="w-5 h-5 text-blue-600" /> Accessibility & Reading Preferences
          </h3>
          <button
            onClick={onClose}
            className="p-1 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100"
            aria-label="Close preferences modal"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="space-y-5 text-xs text-slate-700">
          {/* Text Size Scale */}
          <div className="space-y-2">
            <label className="font-bold text-slate-900 flex items-center gap-2">
              <Type className="w-4 h-4 text-blue-600" /> Text Display Scale ({settings.textScale}%)
            </label>
            <div className="flex items-center gap-2">
              {[100, 125, 150, 175, 200].map((scale) => (
                <button
                  key={scale}
                  onClick={() => handleChange('textScale', scale)}
                  className={`px-3 py-1.5 rounded-lg border font-semibold transition-all ${
                    settings.textScale === scale
                      ? 'bg-blue-600 text-white border-blue-600 shadow-sm'
                      : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
                  }`}
                >
                  {scale}%
                </button>
              ))}
            </div>
          </div>

          {/* Reading Level */}
          <div className="space-y-2">
            <label className="font-bold text-slate-900 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-amber-500" /> AI Explanation Target Reading Level
            </label>
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => handleChange('readingLevel', 'simple')}
                className={`p-3 rounded-xl border text-left transition-all ${
                  settings.readingLevel === 'simple'
                    ? 'bg-blue-50 border-blue-500 text-blue-900 font-bold'
                    : 'bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100'
                }`}
              >
                <span className="block text-xs font-bold">Simple (Grade 8)</span>
                <span className="text-[11px] text-slate-500">Max plain-language & aggressive jargon substitution</span>
              </button>

              <button
                onClick={() => handleChange('readingLevel', 'standard')}
                className={`p-3 rounded-xl border text-left transition-all ${
                  settings.readingLevel === 'standard'
                    ? 'bg-blue-50 border-blue-500 text-blue-900 font-bold'
                    : 'bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100'
                }`}
              >
                <span className="block text-xs font-bold">Standard</span>
                <span className="text-[11px] text-slate-500">Balanced explanation with original citations</span>
              </button>
            </div>
          </div>

          {/* High Contrast Mode */}
          <div className="flex items-center justify-between p-3 bg-slate-50 rounded-xl border border-slate-200">
            <div>
              <span className="font-bold text-slate-900 block">High Contrast Mode (AAA)</span>
              <span className="text-[11px] text-slate-500">Maximizes text and component border contrast ratio</span>
            </div>
            <input
              type="checkbox"
              checked={settings.highContrast}
              onChange={(e) => handleChange('highContrast', e.target.checked)}
              className="w-4 h-4 text-blue-600 rounded border-slate-300 focus:ring-blue-500"
            />
          </div>

          {/* Dyslexia-Friendly Font */}
          <div className="flex items-center justify-between p-3 bg-slate-50 rounded-xl border border-slate-200">
            <div>
              <span className="font-bold text-slate-900 block">Dyslexia-Friendly Font</span>
              <span className="text-[11px] text-slate-500">Applies heavy-bottomed typeface spacing for clause reading</span>
            </div>
            <input
              type="checkbox"
              checked={settings.dyslexiaFont}
              onChange={(e) => handleChange('dyslexiaFont', e.target.checked)}
              className="w-4 h-4 text-blue-600 rounded border-slate-300 focus:ring-blue-500"
            />
          </div>

          {/* Disable 3D Graph -> Table View Default */}
          <div className="flex items-center justify-between p-3 bg-slate-50 rounded-xl border border-slate-200">
            <div>
              <span className="font-bold text-slate-900 block">Disable 3D Canvas Graph</span>
              <span className="text-[11px] text-slate-500">Defaults Evidence Graph to WCAG accessible table view</span>
            </div>
            <input
              type="checkbox"
              checked={settings.disable3DGraph}
              onChange={(e) => handleChange('disable3DGraph', e.target.checked)}
              className="w-4 h-4 text-blue-600 rounded border-slate-300 focus:ring-blue-500"
            />
          </div>

          {/* Reduce Motion */}
          <div className="flex items-center justify-between p-3 bg-slate-50 rounded-xl border border-slate-200">
            <div>
              <span className="font-bold text-slate-900 block">Reduce Motion</span>
              <span className="text-[11px] text-slate-500">Disables animations and transitions</span>
            </div>
            <input
              type="checkbox"
              checked={settings.reduceMotion}
              onChange={(e) => handleChange('reduceMotion', e.target.checked)}
              className="w-4 h-4 text-blue-600 rounded border-slate-300 focus:ring-blue-500"
            />
          </div>
        </div>

        <div className="pt-2 border-t border-slate-100 flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold text-xs shadow-sm"
          >
            Save Preferences
          </button>
        </div>
      </div>
    </div>
  );
};
