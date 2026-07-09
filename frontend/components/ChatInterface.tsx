"use client";

import { useState, useRef, useEffect } from "react";
import { streamChat, loginUser, getChatHistory } from "@/lib/api";

import ReactMarkdown from "react-markdown";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface Props {
  selectedDocIds: string[];
}

export default function ChatInterface({ selectedDocIds }: Props) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [agentType, setAgentType] = useState<"mentor" | "grader">("mentor");
  const bottomRef = useRef<HTMLDivElement>(null);

  // Authentication states
  const [loggedInEmail, setLoggedInEmail] = useState<string | null>(null);
  const [emailInput, setEmailInput] = useState("");
  const [isLoggingIn, setIsLoggingIn] = useState(false);

  useEffect(() => {
    const savedEmail = localStorage.getItem("user_email");
    if (savedEmail) {
      setLoggedInEmail(savedEmail);
      loadHistory(savedEmail);
    }
  }, []);

  const loadHistory = async (email: string) => {
    try {
      const history = await getChatHistory(email);
      setMessages(history);
    } catch (error) {
      console.error("Failed to load history:", error);
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!emailInput.trim()) return;
    
    setIsLoggingIn(true);
    try {
      const res = await loginUser(emailInput.trim());
      localStorage.setItem("user_email", res.email);
      setLoggedInEmail(res.email);
      await loadHistory(res.email);
    } catch (error) {
      alert("Đăng nhập thất bại: " + error);
    } finally {
      setIsLoggingIn(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("user_email");
    setLoggedInEmail(null);
    setMessages([]);
  };

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || streaming) return;

    const question = input.trim();
    setInput("");
    
    const newMessages: Message[] = [...messages, { role: "user", content: question }];
    setMessages(newMessages);
    setStreaming(true);

    let answer = "";
    setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

    await streamChat(
      newMessages,
      selectedDocIds,
      agentType,
      loggedInEmail,
      (token) => {
        answer += token;
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            role: "assistant",
            content: answer,
          };
          return updated;
        });
      },
      () => setStreaming(false),
      (err) => {
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            role: "assistant",
            content: `Loi: ${err}`,
          };
          return updated;
        });
        setStreaming(false);
      }
    );
  };

  if (!loggedInEmail) {
    return (
      <div className="flex flex-col items-center justify-center h-full bg-gray-50 p-6">
        <div className="bg-white p-8 rounded-2xl shadow-sm border max-w-md w-full text-center">
          <div className="text-4xl mb-4">🎓</div>
          <h2 className="text-2xl font-bold mb-2">Đăng nhập để vào học</h2>
          <p className="text-gray-500 mb-6">Bạn hãy nhập email để AI ghi nhớ lịch sử trò chuyện và dễ dàng gửi kết quả nhé.</p>
          <form onSubmit={handleLogin} className="space-y-4">
            <input
              type="email"
              value={emailInput}
              onChange={(e) => setEmailInput(e.target.value)}
              placeholder="Nhập email của bạn..."
              className="w-full border rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
            <button
              type="submit"
              disabled={isLoggingIn}
              className="w-full bg-blue-600 text-white font-semibold py-3 rounded-xl hover:bg-blue-700 transition disabled:opacity-50"
            >
              {isLoggingIn ? "Đang đăng nhập..." : "Bắt đầu học"}
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full relative">
      <div className="absolute top-4 right-4 z-10 flex items-center gap-2">
        <span className="text-sm text-gray-500">{loggedInEmail}</span>
        <button onClick={handleLogout} className="text-sm text-red-500 hover:underline">
          Đăng xuất
        </button>
      </div>

      <div className="p-4 border-b flex justify-center gap-4 bg-gray-50">
        <button
          onClick={() => setAgentType("mentor")}
          className={`px-4 py-2 rounded-xl font-medium transition-colors ${
            agentType === "mentor"
              ? "bg-blue-600 text-white"
              : "bg-white text-gray-600 hover:bg-gray-100 border border-gray-200"
          }`}
        >
          🎓 Cố vấn học tập
        </button>
        <button
          onClick={() => setAgentType("grader")}
          className={`px-4 py-2 rounded-xl font-medium transition-colors ${
            agentType === "grader"
              ? "bg-green-600 text-white"
              : "bg-white text-gray-600 hover:bg-gray-100 border border-gray-200"
          }`}
        >
          📝 Chấm bài tập
        </button>
      </div>

      <div className="flex-1 overflow-y-auto space-y-4 p-4">
        {messages.length === 0 && (
          <p className="text-gray-400 text-center mt-8">
            Hoi bat ky cau hoi nao ve tai lieu da upload
          </p>
        )}
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-2 whitespace-pre-wrap
                ${
                  msg.role === "user"
                    ? "bg-blue-600 text-white"
                    : "bg-gray-100 text-gray-900"
                }`}
            >
              {msg.role === "user" ? (
                <div className="whitespace-pre-wrap">{msg.content}</div>
              ) : (
                <div className="prose prose-sm max-w-none break-words">
                  <ReactMarkdown>
                    {msg.content}
                  </ReactMarkdown>
                </div>
              )}
              {streaming &&
                i === messages.length - 1 &&
                msg.role === "assistant" && (
                  <span className="inline-block w-2 h-4 bg-gray-400 animate-pulse ml-1" />
                )}
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      <div className="border-t p-4 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
          placeholder="Nhap cau hoi..."
          disabled={streaming}
          className="flex-1 border rounded-xl px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          onClick={handleSend}
          disabled={streaming || !input.trim()}
          className="bg-blue-600 text-white px-6 py-2 rounded-xl hover:bg-blue-700 disabled:opacity-50"
        >
          Gui
        </button>
      </div>
    </div>
  );
}
