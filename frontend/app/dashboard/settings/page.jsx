"use client";

import { useState, useEffect } from "react";
import { useSession } from "next-auth/react";
import { useTranslationStore } from "@/store/translation.store";
import { apiClient } from "@/lib/api-client";
import { Loader2, Save, ShieldCheck } from "lucide-react";

export default function SettingsPage() {
  const { data: session, update } = useSession();
  const user = session?.user;
  
  const { model: storeModel, tone: storeTone, setModel, setTone } = useTranslationStore();

  const [prefModel, setPrefModel] = useState("gpt-4o");
  const [prefTone, setPrefTone] = useState("formal");
  const [prefSrcLang, setPrefSrcLang] = useState("auto");
  const [prefTgtLang, setPrefTgtLang] = useState("en");

  // Sync state once user is loaded
  useEffect(() => {
    if (user) {
      setPrefModel(user.preferred_model || storeModel || "gpt-4o");
      setPrefTone(user.preferred_tone || storeTone || "formal");
      setPrefSrcLang(user.default_source_lang || "auto");
      setPrefTgtLang(user.default_target_lang || "en");
    }
  }, [user, storeModel, storeTone]);
  const [prefSaving, setPrefSaving] = useState(false);
  const [prefSuccess, setPrefSuccess] = useState("");
  const [prefError, setPrefError] = useState("");

  const [curPass, setCurPass] = useState("");
  const [newPass, setNewPass] = useState("");
  const [passSaving, setPassSaving] = useState(false);
  const [passSuccess, setPassSuccess] = useState("");
  const [passError, setPassError] = useState("");

  const handleSavePrefs = async (e) => {
    e.preventDefault();
    setPrefSaving(true);
    setPrefError("");
    setPrefSuccess("");
    try {
      await apiClient.patch("/auth/me", {
        preferred_model: prefModel,
        preferred_tone: prefTone,
        default_source_lang: prefSrcLang,
        default_target_lang: prefTgtLang,
      });
      setModel(prefModel);
      setTone(prefTone);
      await update();
      setPrefSuccess("Preferences saved successfully.");
    } catch (err) {
      setPrefError(err?.response?.data?.detail || "Failed to save preferences.");
    } finally {
      setPrefSaving(false);
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    if (newPass.length < 8) {
      setPassError("New password must be at least 8 characters.");
      return;
    }
    setPassSaving(true);
    setPassError("");
    setPassSuccess("");
    try {
      await apiClient.post("/auth/change-password", {
        current_password: curPass,
        new_password: newPass,
      });
      setPassSuccess("Password changed successfully.");
      setCurPass("");
      setNewPass("");
    } catch (err) {
      setPassError(err?.response?.data?.detail || "Failed to change password.");
    } finally {
      setPassSaving(false);
    }
  };

  return (
    <div className="flex flex-col gap-8 max-w-3xl">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground">Manage your account and AI preferences.</p>
      </div>

      {/* Profile Card */}
      <div className="rounded-xl border bg-card shadow-sm">
        <div className="border-b px-6 py-4">
          <h3 className="font-semibold">Profile</h3>
          <p className="text-sm text-muted-foreground">Your account information.</p>
        </div>
        <div className="px-6 py-5 grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-xs text-muted-foreground font-medium uppercase tracking-wider mb-1">Username</p>
            <p className="font-medium">{user?.username || "—"}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground font-medium uppercase tracking-wider mb-1">Email</p>
            <p className="font-medium">{user?.email || "—"}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground font-medium uppercase tracking-wider mb-1">Role</p>
            <span className="inline-flex items-center rounded-full bg-primary/10 border border-primary/20 text-primary px-2.5 py-0.5 text-xs font-medium capitalize">
              {user?.role || "user"}
            </span>
          </div>
        </div>
      </div>

      {/* AI Preferences */}
      <div className="rounded-xl border bg-card shadow-sm">
        <div className="border-b px-6 py-4">
          <h3 className="font-semibold">AI Preferences</h3>
          <p className="text-sm text-muted-foreground">Set your default translation behaviour.</p>
        </div>
        <form onSubmit={handleSavePrefs} className="px-6 py-5 grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Default Model</label>
            <select
              value={prefModel}
              onChange={(e) => setPrefModel(e.target.value)}
              className="flex h-10 w-full rounded-lg border border-input bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
            >
              <option value="gpt-4o">GPT-4o (Most Capable)</option>
              <option value="gpt-4o-mini">GPT-4o Mini (Fast)</option>
              <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
              <option value="deepseek-chat">DeepSeek Chat</option>
            </select>
          </div>
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Default Tone</label>
            <select
              value={prefTone}
              onChange={(e) => setPrefTone(e.target.value)}
              className="flex h-10 w-full rounded-lg border border-input bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
            >
              <option value="formal">Formal</option>
              <option value="casual">Casual</option>
              <option value="technical">Technical</option>
              <option value="literary">Literary</option>
            </select>
          </div>
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Default Source Language</label>
            <input
              value={prefSrcLang}
              onChange={(e) => setPrefSrcLang(e.target.value)}
              placeholder="auto"
              className="flex h-10 w-full rounded-lg border border-input bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
            />
          </div>
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Default Target Language</label>
            <input
              value={prefTgtLang}
              onChange={(e) => setPrefTgtLang(e.target.value)}
              placeholder="en"
              className="flex h-10 w-full rounded-lg border border-input bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
            />
          </div>

          {prefSuccess && <p className="col-span-full text-sm text-green-600">{prefSuccess}</p>}
          {prefError && <p className="col-span-full text-sm text-destructive">{prefError}</p>}

          <div className="col-span-full">
            <button
              type="submit"
              disabled={prefSaving}
              className="flex items-center gap-2 bg-primary text-primary-foreground px-5 py-2.5 rounded-lg text-sm font-medium hover:bg-primary/90 transition disabled:opacity-60"
            >
              {prefSaving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
              Save Preferences
            </button>
          </div>
        </form>
      </div>

      {/* Change Password */}
      <div className="rounded-xl border bg-card shadow-sm">
        <div className="border-b px-6 py-4">
          <h3 className="font-semibold">Security</h3>
          <p className="text-sm text-muted-foreground">Update your account password.</p>
        </div>
        <form onSubmit={handleChangePassword} className="px-6 py-5 space-y-4">
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Current Password</label>
            <input
              type="password"
              value={curPass}
              onChange={(e) => setCurPass(e.target.value)}
              required
              placeholder="••••••••"
              className="flex h-10 w-full rounded-lg border border-input bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
            />
          </div>
          <div className="space-y-1.5">
            <label className="text-sm font-medium">New Password</label>
            <input
              type="password"
              value={newPass}
              onChange={(e) => setNewPass(e.target.value)}
              required
              placeholder="Min 8 chars, 1 uppercase, 1 number"
              className="flex h-10 w-full rounded-lg border border-input bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
            />
          </div>

          {passSuccess && <p className="text-sm text-green-600">{passSuccess}</p>}
          {passError && <p className="text-sm text-destructive">{passError}</p>}

          <button
            type="submit"
            disabled={passSaving}
            className="flex items-center gap-2 bg-primary text-primary-foreground px-5 py-2.5 rounded-lg text-sm font-medium hover:bg-primary/90 transition disabled:opacity-60"
          >
            {passSaving ? <Loader2 className="h-4 w-4 animate-spin" /> : <ShieldCheck className="h-4 w-4" />}
            Update Password
          </button>
        </form>
      </div>
    </div>
  );
}
