import { IngestionStatus } from "@/components/admin/ingestion-status";
import { UploadForm } from "@/components/admin/upload-form";
import { DocumentList } from "@/components/admin/document-list";

export default function AdminPage() {
  return (
    <main className="container mx-auto p-8">
      <div className="space-y-8">
        <header>
          <h1 className="text-3xl font-bold">Admin - Content Management</h1>
          <p className="text-muted-foreground mt-2">
            Manage knowledge base content and trigger ingestion
          </p>
        </header>

        <section>
          <h2 className="text-2xl font-semibold mb-4">Ingest Content</h2>
          <IngestionStatus />
        </section>

        <section>
          <h2 className="text-2xl font-semibold mb-4">Upload Documents</h2>
          <UploadForm />
        </section>

        <section>
          <h2 className="text-2xl font-semibold mb-4">Manage Documents</h2>
          <DocumentList />
        </section>
      </div>
    </main>
  );
}
