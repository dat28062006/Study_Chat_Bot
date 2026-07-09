"use client";

import { useState, useRef } from "react";
import { uploadDocument } from "@/lib/api";

interface Props {
  onUploaded: () => void;
}

export default function FileUpload({ onUploaded }: Props) {
  const [uploading, setUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = async (file: File) => {
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      alert("Chi chap nhan file PDF");
      return;
    }
    setUploading(true);
    try {
      await uploadDocument(file);
      onUploaded();
    } catch (e) {
      alert(`Upload that bai: ${e}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div
      className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors
        ${dragOver ? "border-blue-500 bg-blue-50" : "border-gray-300 hover:border-gray-400"}`}
      onDragOver={(e) => {
        e.preventDefault();
        setDragOver(true);
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragOver(false);
        const file = e.dataTransfer.files[0];
        if (file) handleFile(file);
      }}
      onClick={() => inputRef.current?.click()}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf"
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) handleFile(file);
        }}
      />
      {uploading ? (
        <p className="text-blue-600">Dang upload va xu ly...</p>
      ) : (
        <>
          <p className="text-lg font-medium">Keo tha PDF vao day</p>
          <p className="text-gray-500 text-sm mt-1">hoac click de chon file</p>
        </>
      )}
    </div>
  );
}
