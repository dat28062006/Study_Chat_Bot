"use client";

import { useState, useEffect, useCallback } from "react";
import FileUpload from "@/components/FileUpload";
import DocumentList from "@/components/DocumentList";
import ChatInterface from "@/components/ChatInterface";
import { listDocuments, deleteDocument, Document } from "@/lib/api";

export default function Home() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selected, setSelected] = useState<string[]>([]);

  const refresh = useCallback(async () => {
    try {
      const docs = await listDocuments();
      setDocuments(docs);
    } catch {
      // backend may not be ready yet
    }
  }, []);

  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, 5000);
    return () => clearInterval(interval);
  }, [refresh]);

  const toggleDoc = (id: string) => {
    setSelected((prev) =>
      prev.includes(id) ? prev.filter((d) => d !== id) : [...prev, id]
    );
  };

  const handleDelete = async (id: string) => {
    await deleteDocument(id);
    setSelected((prev) => prev.filter((d) => d !== id));
    refresh();
  };

  return (
    <main className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto p-6">
        <h1 className="text-3xl font-bold mb-6">RAG Document Chat</h1>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-120px)]">
          <div className="space-y-4">
            <FileUpload onUploaded={refresh} />
            <div>
              <h2 className="font-semibold mb-2">
                Tai lieu ({documents.length})
              </h2>
              <DocumentList
                documents={documents}
                selected={selected}
                onToggle={toggleDoc}
                onDelete={handleDelete}
              />
            </div>
          </div>

          <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border flex flex-col">
            <div className="border-b px-4 py-3">
              <h2 className="font-semibold">Chat</h2>
              {selected.length > 0 && (
                <p className="text-xs text-gray-500">
                  Dang tim trong {selected.length} tai lieu
                </p>
              )}
            </div>
            <ChatInterface selectedDocIds={selected} />
          </div>
        </div>
      </div>
    </main>
  );
}
