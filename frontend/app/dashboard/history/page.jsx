"use client";

import { useState, useEffect } from 'react';
import { useHistory, useToggleStar, useDeleteTranslation } from '@/hooks/useHistory';
import { useLanguages } from '@/hooks/useLanguages';
import { useDebounce } from '@/hooks/useDebounce';
import { Star, Trash2, Search, Filter, Loader2, ChevronLeft, ChevronRight } from 'lucide-react';
import { format } from 'date-fns';

export default function HistoryPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebounce(search, 500);
  const [starredOnly, setStarredOnly] = useState(false);
  
  // Reset page when search term changes
  useEffect(() => {
    setPage(1);
  }, [debouncedSearch]);

  const handleSearchChange = (e) => {
    setSearch(e.target.value);
  };

  const filters = {
    ...(debouncedSearch && { q: debouncedSearch }),
    ...(starredOnly && { starred: true }),
  };

  const { data, isLoading, isError } = useHistory(page, 10, filters);
  const toggleStarMutation = useToggleStar();
  const deleteMutation = useDeleteTranslation();

  const { data: langsData } = useLanguages();

  const getLanguageName = (code) => {
    if (!langsData) return code.toUpperCase();
    const lang = langsData.find(l => l.code === code);
    return lang ? lang.name : code.toUpperCase();
  };

  const handleToggleStar = (id) => {
    toggleStarMutation.mutate(id);
  };

  const handleDelete = (id) => {
    if (confirm("Are you sure you want to delete this translation?")) {
      deleteMutation.mutate(id);
    }
  };

  return (
    <div className="flex flex-col h-full gap-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Translation History</h1>
          <p className="text-muted-foreground">View and manage your past AI translations.</p>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="flex flex-col sm:flex-row items-center gap-4 p-4 rounded-xl border bg-card text-card-foreground shadow-sm">
        <div className="relative flex-1 w-full">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input 
            type="text" 
            placeholder="Search original or translated text..." 
            value={search}
            onChange={handleSearchChange}
            className="w-full pl-9 pr-4 py-2 bg-background border rounded-md text-sm outline-none focus:ring-1 focus:ring-primary"
          />
        </div>
        <div className="flex items-center gap-4 w-full sm:w-auto">
          <button 
            onClick={() => { setStarredOnly(!starredOnly); setPage(1); }}
            className={`flex items-center gap-2 px-3 py-2 border rounded-md text-sm font-medium transition ${
              starredOnly ? "bg-primary/10 border-primary/20 text-primary" : "bg-background hover:bg-muted"
            }`}
          >
            <Star className={`h-4 w-4 ${starredOnly ? "fill-primary" : ""}`} />
            Starred
          </button>
        </div>
      </div>

      {/* History List */}
      <div className="rounded-xl border bg-card text-card-foreground shadow-sm overflow-hidden flex-1 flex flex-col">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center flex-1 py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary opacity-50 mb-4" />
            <p className="text-muted-foreground">Loading history...</p>
          </div>
        ) : isError ? (
          <div className="flex flex-col items-center justify-center flex-1 py-12">
            <p className="text-destructive font-medium">Failed to load history.</p>
          </div>
        ) : data?.items?.length === 0 ? (
          <div className="flex flex-col items-center justify-center flex-1 py-16 text-center px-4">
            <Filter className="h-12 w-12 text-muted-foreground opacity-20 mb-4" />
            <h3 className="text-lg font-medium mb-1">No translations found</h3>
            <p className="text-muted-foreground text-sm max-w-sm">
              {debouncedSearch || starredOnly 
                ? "Try adjusting your filters or search terms." 
                : "You haven't translated anything yet. Head to the Translate page to get started!"}
            </p>
          </div>
        ) : (
          <>
            <div className="flex-1 overflow-y-auto divide-y">
              {data.items.map((item) => (
                <div key={item.id} className="p-4 sm:p-6 hover:bg-muted/30 transition flex flex-col sm:flex-row gap-4 sm:gap-6 group">
                  <div className="flex-1 space-y-4">
                    {/* Header: Languages and Meta */}
                    <div className="flex items-center gap-3 text-xs font-medium text-muted-foreground">
                      <div className="bg-secondary px-2 py-1 rounded-md text-foreground">
                        {getLanguageName(item.source_language)} → {getLanguageName(item.target_language)}
                      </div>
                      <span>{format(new Date(item.created_at), "MMM d, yyyy 'at' h:mm a")}</span>
                      <span className="capitalize border px-2 py-0.5 rounded-full text-[10px]">{item.tone}</span>
                      <span className="border px-2 py-0.5 rounded-full text-[10px] bg-primary/5 text-primary border-primary/10">
                        {item.ai_model}
                      </span>
                    </div>

                    {/* Content */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div className="space-y-1">
                        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Source</p>
                        <p className="text-sm">{item.source_text}</p>
                      </div>
                      <div className="space-y-1">
                        <p className="text-xs font-semibold text-primary uppercase tracking-wider">Translation</p>
                        <p className="text-sm font-medium">{item.translated_text}</p>
                      </div>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex sm:flex-col justify-end sm:justify-start gap-2 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity">
                    <button 
                      onClick={() => handleToggleStar(item.id)}
                      className="p-2 rounded-md hover:bg-accent text-muted-foreground hover:text-foreground transition"
                      title={item.is_starred ? "Unstar" : "Star"}
                    >
                      <Star className={`h-4 w-4 ${item.is_starred ? "fill-yellow-400 text-yellow-400" : ""}`} />
                    </button>
                    <button 
                      onClick={() => handleDelete(item.id)}
                      className="p-2 rounded-md hover:bg-destructive/10 text-muted-foreground hover:text-destructive transition"
                      title="Delete"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination Footer */}
            {data.total > data.limit && (
              <div className="border-t p-4 flex items-center justify-between bg-muted/10">
                <p className="text-sm text-muted-foreground">
                  Showing <span className="font-medium">{((page - 1) * 10) + 1}</span> to <span className="font-medium">{Math.min(page * 10, data.total)}</span> of <span className="font-medium">{data.total}</span> results
                </p>
                <div className="flex gap-2">
                  <button 
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="p-2 border rounded-md hover:bg-muted disabled:opacity-50 transition"
                  >
                    <ChevronLeft className="h-4 w-4" />
                  </button>
                  <button 
                    onClick={() => setPage(p => p + 1)}
                    disabled={page >= Math.ceil(data.total / 10)}
                    className="p-2 border rounded-md hover:bg-muted disabled:opacity-50 transition"
                  >
                    <ChevronRight className="h-4 w-4" />
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
