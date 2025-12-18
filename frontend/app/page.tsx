import { ChatInterface } from "@/components/chat/chat-interface";

export default function Home() {
  return (
    <main className="container mx-auto h-screen">
      <div className="h-full flex flex-col">
        <header className="border-b p-4">
          <h1 className="text-2xl font-bold">Site RAG Chatbot</h1>
          <p className="text-sm text-muted-foreground">
            Ask questions about the website content
          </p>
        </header>
        <ChatInterface />
      </div>
    </main>
  );
}
