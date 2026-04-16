import { useCallback, useRef } from "react";
import { useUpload } from "@/hooks/use-upload";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Upload } from "lucide-react";

interface UploadWidgetProps {
  botId: string;
}

export function UploadWidget({ botId }: UploadWidgetProps) {
  const { isUploading, progress, error, lastResult, upload } = useUpload(botId);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      const file = e.dataTransfer.files[0];
      if (file) upload(file);
    },
    [upload]
  );

  const handleFileSelect = useCallback(() => {
    const file = inputRef.current?.files?.[0];
    if (file) upload(file);
  }, [upload]);

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-sm">Upload Documents</CardTitle>
      </CardHeader>
      <CardContent>
        <div
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleDrop}
          className="flex flex-col items-center gap-2 rounded-lg border-2 border-dashed border-neutral-200 p-6 text-center hover:border-neutral-400"
        >
          <Upload className="h-8 w-8 text-neutral-400" />
          <p className="text-xs text-neutral-500">
            Drag a file here or click to browse
          </p>
          <input
            ref={inputRef}
            type="file"
            accept=".txt,.pdf,.docx,.json"
            onChange={handleFileSelect}
            className="hidden"
          />
          <Button
            variant="outline"
            size="sm"
            onClick={() => inputRef.current?.click()}
            disabled={isUploading}
          >
            {isUploading ? progress : "Choose File"}
          </Button>
        </div>
        {error && <p className="mt-2 text-xs text-red-500">{error}</p>}
        {lastResult && (
          <p className="mt-2 text-xs text-green-600">
            Ingested {lastResult.chunks_created} chunks
          </p>
        )}
      </CardContent>
    </Card>
  );
}
