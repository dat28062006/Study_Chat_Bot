"use client";

import { Document } from "@/lib/api";

interface Props {
  documents: Document[];
  selected: string[];
  onToggle: (id: string) => void;
  onDelete: (id: string) => void;
}

const statusColor: Record<string, string> = {
  indexed: "bg-green-100 text-green-700",
  processing: "bg-yellow-100 text-yellow-700",
  uploading: "bg-blue-100 text-blue-700",
  failed: "bg-red-100 text-red-700",
};

export default function DocumentList({
  documents,
  selected,
  onToggle,
  onDelete,
}: Props) {
  if (documents.length === 0) {
    return <p className="text-gray-500 text-sm">Chua co tai lieu nao</p>;
  }

  return (
    <div className="space-y-2">
      {documents.map((doc) => (
        <div
          key={doc.id}
          className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer
            ${selected.includes(doc.id) ? "border-blue-500 bg-blue-50" : "border-gray-200"}`}
          onClick={() => doc.status === "indexed" && onToggle(doc.id)}
        >
          <input
            type="checkbox"
            checked={selected.includes(doc.id)}
            disabled={doc.status !== "indexed"}
            onChange={() => onToggle(doc.id)}
            onClick={(e) => e.stopPropagation()}
          />
          <div className="flex-1 min-w-0">
            <p className="font-medium truncate">{doc.filename}</p>
            <p className="text-xs text-gray-500">
              {doc.chunk_count > 0 && `${doc.chunk_count} chunks · `}
              {new Date(doc.created_at).toLocaleString("vi-VN")}
            </p>
          </div>
          <span
            className={`text-xs px-2 py-1 rounded-full ${statusColor[doc.status] || ""}`}
          >
            {doc.status}
          </span>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDelete(doc.id);
            }}
            className="text-red-500 hover:text-red-700 text-sm"
          >
            x
          </button>
        </div>
      ))}
    </div>
  );
}
