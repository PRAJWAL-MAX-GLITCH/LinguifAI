import { Separator } from "@/components/ui/separator";
import Sidebar from "./Sidebar";
import Navbar from "./Navbar";

export default function DashboardLayout({ children }) {
  return (
    <div className="flex h-screen w-full bg-background overflow-hidden">
      {/* Desktop Sidebar */}
      <div className="hidden lg:block lg:w-64 lg:flex-shrink-0 h-screen">
        <Sidebar />
      </div>

      {/* Main Content Area */}
      <div className="flex flex-1 flex-col overflow-hidden">
        <Navbar />
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
          <div className="mx-auto max-w-6xl pb-16">
            {children}
          </div>
        </main>

        {/* Footer */}
        <footer className="border-t py-3 px-6 flex items-center justify-between text-xs text-muted-foreground/60 bg-muted/10">
          <span>© {new Date().getFullYear()} LinguifAI. All rights reserved.</span>
          <span>Powered by GPT-4o · Gemini · DeepSeek</span>
        </footer>
      </div>
    </div>
  );
}
