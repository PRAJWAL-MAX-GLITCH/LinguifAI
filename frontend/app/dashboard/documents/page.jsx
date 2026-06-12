"use client";

import { useRef, useState } from "react";
import { useDocuments, useUploadDocument, useDeleteDocument, downloadDocument } from "@/hooks/useDocuments";
import {
  UploadCloud, FileText, Loader2, Trash2,
  Download, RefreshCw, CheckCircle2, XCircle,
  Clock, Zap
} from "lucide-react";

const STATUS_CONFIG = {
  pending:    { label: "Pending",    icon: Clock,         className: "text-yellow-600 bg-yellow-500/10 border-yellow-500/20" },
  processing: { label: "Processing", icon: RefreshCw,     className: "text-blue-600 bg-blue-500/10 border-blue-500/20" },
  completed:  { label: "Completed",  icon: CheckCircle2,  className: "text-green-600 bg-green-500/10 border-green-500/20" },
  failed:     { label: "Failed",     icon: XCircle,       className: "text-destructive bg-destructive/10 border-destructive/20" },
};

const FILE_ICONS = { pdf: "📄", docx: "📝", txt: "📃" };

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function DocumentRow({ doc, onDelete }) {
  const [downloading, setDownloading] = useState(false);
  const config = STATUS_CONFIG[doc.status] || STATUS_CONFIG.pending;
  const StatusIcon = config.icon;

  const handleDownload = async () => {
    setDownloading(true);
    try {
      await downloadDocument(doc.id, doc.original_filename);
    } catch {
      alert("Download failed. The file may not be ready yet.");
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="flex items-center gap-4 px-6 py-4 hover:bg-muted/20 transition group">
      <div className="text-2xl flex-shrink-0 w-8 text-center">
        {FILE_ICONS[doc.file_type] || "📁"}
      </div>

      <div className="flex-1 min-w-0">
        <p className="font-medium text-sm truncate">{doc.original_filename}</p>
        <div className="flex items-center gap-2 text-xs text-muted-foreground mt-0.5 flex-wrap">
          <span>{formatBytes(doc.file_size_bytes)}</span>
          <span>·</span>
          <span className="uppercase">{doc.source_language || "auto"} → {doc.target_language}</span>
          <span>·</span>
          <span>{doc.ai_model}</span>
        </div>
      </div>

      {/* Status Badge */}
      <span className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium flex-shrink-0 ${config.className}`}>
        <StatusIcon className={`h-3.5 w-3.5 flex-shrink-0 ${doc.status === "processing" ? "animate-spin" : ""}`} />
        {config.label}
      </span>

      {/* Actions */}
      <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0">
        {doc.status === "completed" && (
          <button
            onClick={handleDownload}
            disabled={downloading}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs bg-primary/10 text-primary border border-primary/20 rounded-md hover:bg-primary/20 transition disabled:opacity-60"
          >
            {downloading
              ? <Loader2 className="h-3.5 w-3.5 animate-spin" />
              : <Download className="h-3.5 w-3.5" />}
            Download
          </button>
        )}
        <button
          onClick={() => onDelete(doc.id)}
          className="p-1.5 rounded-md text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition"
          title="Delete document"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}

export default function DocumentsPage() {
  const fileInputRef = useRef(null);
  const [dragging, setDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [targetLang, setTargetLang] = useState("en");
  const [sourceLang, setSourceLang] = useState("auto");
  const [tone, setTone] = useState("formal");
  const [model, setModel] = useState("gpt-4o");
  const [fileError, setFileError] = useState("");

  const { data: documents = [], isLoading, refetch } = useDocuments();
  const uploadMutation = useUploadDocument();
  const deleteMutation = useDeleteDocument();

  const validateFile = (file) => {
    if (!file) return;
    const ext = file.name.split(".").pop().toLowerCase();
    if (!["pdf", "docx", "txt"].includes(ext)) {
      setFileError("Only PDF, DOCX, and TXT files are supported.");
      return false;
    }
    if (file.size > 10 * 1024 * 1024) {
      setFileError("File size must be under 10 MB.");
      return false;
    }
    setFileError("");
    return true;
  };

  const handleFileSelect = (file) => {
    if (validateFile(file)) {
      setSelectedFile(file);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    handleFileSelect(e.dataTransfer.files[0]);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    try {
      await uploadMutation.mutateAsync({
        file: selectedFile,
        targetLanguage: targetLang,
        sourceLanguage: sourceLang,
        tone,
        model,
      });
      setSelectedFile(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
    } catch (err) {
      setFileError(err?.response?.data?.detail || "Upload failed.");
    }
  };

  const handleDelete = async (docId) => {
    if (!confirm("Delete this document and its translation?")) return;
    deleteMutation.mutate(docId);
  };

  const pendingOrProcessing = documents.filter(
    (d) => d.status === "pending" || d.status === "processing"
  );

  return (
    <div className="flex flex-col gap-8">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Document Translation</h1>
          <p className="text-muted-foreground">
            Upload PDF, DOCX, or TXT files. AI translates them in the background.
          </p>
        </div>
        {pendingOrProcessing.length > 0 && (
          <button
            onClick={() => refetch()}
            className="flex items-center gap-2 px-3 py-2 border rounded-md text-sm hover:bg-muted transition"
          >
            <RefreshCw className="h-4 w-4" />
            Refresh
          </button>
        )}
      </div>

      {/* Upload Card */}
      <div className="rounded-xl border bg-card shadow-sm">
        <div className="border-b px-6 py-4 flex items-center gap-2">
          <UploadCloud className="h-5 w-5 text-primary" />
          <h3 className="font-semibold">Upload Document</h3>
        </div>
        <div className="p-6 space-y-5">
          {/* Drop Zone */}
          <div
            onClick={() => fileInputRef.current?.click()}
            onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={handleDrop}
            className={`flex flex-col items-center justify-center cursor-pointer rounded-xl border-2 border-dashed py-14 transition-all ${
              dragging
                ? "border-primary bg-primary/5 scale-[1.01]"
                : selectedFile
                ? "border-green-500/60 bg-green-500/5"
                : "border-border hover:border-primary/40 hover:bg-muted/20"
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.docx,.txt"
              onChange={(e) => handleFileSelect(e.target.files[0])}
              className="hidden"
            />
            {selectedFile ? (
              <div className="text-center">
                <div className="text-4xl mb-3">
                  {FILE_ICONS[selectedFile.name.split(".").pop().toLowerCase()] || "📁"}
                </div>
                <p className="font-semibold text-sm">{selectedFile.name}</p>
                <p className="text-xs text-muted-foreground mt-1">
                  {formatBytes(selectedFile.size)} · Click to change file
                </p>
              </div>
            ) : (
              <div className="text-center">
                <UploadCloud className="h-12 w-12 text-muted-foreground/30 mx-auto mb-4" />
                <p className="font-medium text-sm text-muted-foreground">
                  Drag & drop a file, or{" "}
                  <span className="text-primary font-semibold">click to browse</span>
                </p>
                <p className="text-xs text-muted-foreground/70 mt-1">
                  PDF, DOCX, TXT &mdash; Max 10 MB
                </p>
              </div>
            )}
          </div>

          {fileError && (
            <div className="rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
              {fileError}
            </div>
          )}

          {/* Translation Options */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Source Language
              </label>
              <input
                value={sourceLang}
                onChange={(e) => setSourceLang(e.target.value)}
                placeholder="auto"
                className="h-9 w-full rounded-lg border border-input bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Target Language
              </label>
              <input
                value={targetLang}
                onChange={(e) => setTargetLang(e.target.value)}
                placeholder="e.g. es, fr, de"
                className="h-9 w-full rounded-lg border border-input bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Tone
              </label>
              <select
                value={tone}
                onChange={(e) => setTone(e.target.value)}
                className="h-9 w-full rounded-lg border border-input bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
              >
                <option value="formal">Formal</option>
                <option value="casual">Casual</option>
                <option value="technical">Technical</option>
                <option value="literary">Literary</option>
              </select>
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                AI Model
              </label>
              <select
                value={model}
                onChange={(e) => setModel(e.target.value)}
                className="h-9 w-full rounded-lg border border-input bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
              >
                <option value="gpt-4o">GPT-4o</option>
                <option value="gpt-4o-mini">GPT-4o Mini</option>
                <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
                <option value="deepseek-chat">DeepSeek Chat</option>
              </select>
            </div>
          </div>

          <button
            onClick={handleUpload}
            disabled={!selectedFile || uploadMutation.isPending}
            className="flex items-center gap-2 bg-primary text-primary-foreground px-6 py-2.5 rounded-lg text-sm font-semibold hover:bg-primary/90 transition disabled:opacity-60"
          >
            {uploadMutation.isPending ? (
              <><Loader2 className="h-4 w-4 animate-spin" /> Uploading...</>
            ) : (
              <><Zap className="h-4 w-4" /> Upload & Translate</>
            )}
          </button>
        </div>
      </div>

      {/* Documents List */}
      <div className="rounded-xl border bg-card shadow-sm overflow-hidden">
        <div className="border-b px-6 py-4 flex items-center justify-between">
          <h3 className="font-semibold">Your Documents</h3>
          {documents.length > 0 && (
            <span className="text-xs text-muted-foreground">{documents.length} document{documents.length !== 1 ? "s" : ""}</span>
          )}
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="h-7 w-7 animate-spin text-primary opacity-40" />
          </div>
        ) : documents.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-center px-4">
            <FileText className="h-12 w-12 text-muted-foreground/20 mb-4" />
            <h3 className="font-medium text-sm mb-1">No documents yet</h3>
            <p className="text-muted-foreground text-xs max-w-xs">
              Upload a PDF, DOCX, or TXT file above and we will translate it for you in the background.
            </p>
          </div>
        ) : (
          <div className="divide-y">
            {documents.map((doc) => (
              <DocumentRow key={doc.id} doc={doc} onDelete={handleDelete} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
