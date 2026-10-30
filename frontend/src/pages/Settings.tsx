import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api, setAuthToken } from '../services/api';
import { AppSettings } from '../types';
import { Settings as SettingsIcon, Lock, KeyRound, Check, AlertCircle, Save } from 'lucide-react';

export const Settings: React.FC = () => {
  const queryClient = useQueryClient();
  const [password, setPassword] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(
    Boolean(localStorage.getItem('numpe_admin_token'))
  );
  const [loginError, setLoginError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Form state
  const [formData, setFormData] = useState<AppSettings>({
    rsi_threshold: 42.0,
    pe_threshold: 20.0,
    pb_lower: 2.7,
    pb_upper: 3.2,
    price_interpretation: 'below',
    price_band_pct: 2.0,
    sma_period: 200,
  });

  const { data: currentSettings } = useQuery({
    queryKey: ['settings'],
    queryFn: async () => {
      const data = await api.getSettings();
      setFormData(data);
      return data;
    },
  });

  const loginMutation = useMutation({
    mutationFn: (pwd: string) => api.login(pwd),
    onSuccess: () => {
      setIsAuthenticated(true);
      setLoginError(null);
    },
    onError: () => {
      setLoginError('Incorrect administrative password.');
    },
  });

  const updateMutation = useMutation({
    mutationFn: (newSettings: AppSettings) => api.updateSettings(newSettings),
    onSuccess: (data) => {
      setSuccessMsg('Signal thresholds updated successfully.');
      queryClient.invalidateQueries({ queryKey: ['currentSignal'] });
      queryClient.invalidateQueries({ queryKey: ['marketOverview'] });
      setTimeout(() => setSuccessMsg(null), 4000);
    },
    onError: () => {
      setLoginError('Failed to save settings. Please re-authenticate.');
    },
  });

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    loginMutation.mutate(password);
  };

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    updateMutation.mutate(formData);
  };

  const handleLogout = () => {
    setAuthToken(null);
    setIsAuthenticated(false);
  };

  return (
    <div className="space-y-6 max-w-3xl">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-black text-white flex items-center space-x-2">
          <SettingsIcon className="h-6 w-6 text-blue-400" />
          <span>System & Strategy Threshold Configuration</span>
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Adjust the quantitative investment parameters for Nifty 100 Equal Weight conditions. Protected by administrator authentication.
        </p>
      </div>

      {!isAuthenticated ? (
        /* Login Card */
        <div className="glass-panel rounded-xl p-6 border border-[#2a2f45] shadow-lg max-w-md">
          <div className="flex items-center space-x-2 text-white font-bold mb-4">
            <Lock className="h-5 w-5 text-blue-400" />
            <span>Administrator Access Required</span>
          </div>
          <p className="text-xs text-slate-400 mb-4">
            The general dashboard is open for read-only monitoring. Enter the administrative password to modify systematic condition rules.
          </p>

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="text-xs text-slate-300 font-semibold block mb-1">
                Admin Password:
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter password..."
                className="w-full bg-slate-900 border border-[#2a2f45] rounded-lg p-2.5 text-white text-sm"
              />
            </div>

            {loginError && (
              <div className="text-xs text-rose-400 flex items-center space-x-1.5">
                <AlertCircle className="h-4 w-4" />
                <span>{loginError}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={loginMutation.isPending}
              className="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs py-2.5 rounded-lg shadow-md transition"
            >
              {loginMutation.isPending ? 'Verifying...' : 'Unlock Settings Panel'}
            </button>
          </form>
        </div>
      ) : (
        /* Settings Form */
        <form onSubmit={handleSave} className="glass-panel rounded-xl p-6 border border-[#2a2f45] shadow-lg space-y-6">
          <div className="flex items-center justify-between pb-3 border-b border-[#2a2f45]">
            <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center space-x-1.5">
              <Check className="h-4 w-4" />
              <span>Admin Mode Active</span>
            </span>
            <button
              type="button"
              onClick={handleLogout}
              className="text-xs text-slate-400 hover:text-white underline"
            >
              Lock & Log Out
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 text-xs">
            {/* RSI Threshold */}
            <div>
              <label className="text-slate-300 font-semibold block mb-1">
                RSI (14) Momentum Entry Threshold:
              </label>
              <input
                type="number"
                step="0.5"
                value={formData.rsi_threshold}
                onChange={(e) =>
                  setFormData({ ...formData, rsi_threshold: parseFloat(e.target.value) })
                }
                className="w-full bg-slate-900 border border-[#2a2f45] rounded-lg p-2 text-white font-mono"
              />
              <span className="text-[10px] text-slate-400 mt-1 block">Default: 42.0</span>
            </div>

            {/* P/E Threshold */}
            <div>
              <label className="text-slate-300 font-semibold block mb-1">
                Consolidated P/E Ceiling Threshold:
              </label>
              <input
                type="number"
                step="0.5"
                value={formData.pe_threshold}
                onChange={(e) =>
                  setFormData({ ...formData, pe_threshold: parseFloat(e.target.value) })
                }
                className="w-full bg-slate-900 border border-[#2a2f45] rounded-lg p-2 text-white font-mono"
              />
              <span className="text-[10px] text-slate-400 mt-1 block">Default: 20.0</span>
            </div>

            {/* P/B Lower */}
            <div>
              <label className="text-slate-300 font-semibold block mb-1">
                P/B Ratio Lower Bound:
              </label>
              <input
                type="number"
                step="0.1"
                value={formData.pb_lower}
                onChange={(e) =>
                  setFormData({ ...formData, pb_lower: parseFloat(e.target.value) })
                }
                className="w-full bg-slate-900 border border-[#2a2f45] rounded-lg p-2 text-white font-mono"
              />
              <span className="text-[10px] text-slate-400 mt-1 block">Default: 2.7</span>
            </div>

            {/* P/B Upper */}
            <div>
              <label className="text-slate-300 font-semibold block mb-1">
                P/B Ratio Upper Bound:
              </label>
              <input
                type="number"
                step="0.1"
                value={formData.pb_upper}
                onChange={(e) =>
                  setFormData({ ...formData, pb_upper: parseFloat(e.target.value) })
                }
                className="w-full bg-slate-900 border border-[#2a2f45] rounded-lg p-2 text-white font-mono"
              />
              <span className="text-[10px] text-slate-400 mt-1 block">Default: 3.2</span>
            </div>

            {/* Price Interpretation */}
            <div>
              <label className="text-slate-300 font-semibold block mb-1">
                Condition 1 Price Formula Interpretation:
              </label>
              <select
                value={formData.price_interpretation}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    price_interpretation: e.target.value as 'below' | 'band',
                  })
                }
                className="w-full bg-slate-900 border border-[#2a2f45] rounded-lg p-2 text-white font-medium"
              >
                <option value="below">Mode A: Current Price ≤ Threshold T</option>
                <option value="band">Mode B: Within ± Band % around T</option>
              </select>
            </div>

            {/* Price Band % */}
            <div>
              <label className="text-slate-300 font-semibold block mb-1">
                Price Accumulation Band (± %):
              </label>
              <input
                type="number"
                step="0.5"
                value={formData.price_band_pct}
                onChange={(e) =>
                  setFormData({ ...formData, price_band_pct: parseFloat(e.target.value) })
                }
                disabled={formData.price_interpretation !== 'band'}
                className="w-full bg-slate-900 border border-[#2a2f45] rounded-lg p-2 text-white font-mono disabled:opacity-40"
              />
              <span className="text-[10px] text-slate-400 mt-1 block">Applies in Mode B (Default: 2.0%)</span>
            </div>
          </div>

          {successMsg && (
            <div className="p-3 rounded-lg bg-emerald-950/40 border border-emerald-500/30 text-xs text-emerald-400 flex items-center space-x-2">
              <Check className="h-4 w-4 shrink-0" />
              <span>{successMsg}</span>
            </div>
          )}

          <button
            type="submit"
            disabled={updateMutation.isPending}
            className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs px-6 py-2.5 rounded-lg shadow-lg transition"
          >
            <Save className="h-4 w-4" />
            <span>{updateMutation.isPending ? 'Saving...' : 'Save Configuration Changes'}</span>
          </button>
        </form>
      )}
    </div>
  );
};

