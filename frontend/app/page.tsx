import { ChatInterface } from "@/components/chat/chat-interface";

export default function Home() {
  return (
    <main className="h-full flex flex-col">
      <div className="container mx-auto flex-1 flex flex-col min-h-0">
        <div className="border-b p-4 flex-shrink-0">
          <h1 className="text-2xl font-bold">Site RAG Chatbot</h1>
          <p className="text-sm text-muted-foreground">
            Ask questions about the website content
          </p>
        </div>
        <div className="flex-1 min-h-0">
          <ChatInterface />
        </div>
      </div>
    </main>
  );
}
