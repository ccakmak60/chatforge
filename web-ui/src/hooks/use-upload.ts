import { useState, useCallback } from "react";
import { uploadFile } from "@/lib/api";

export interface UploadState {
  isUploading: boolean;
  progress: string;
  error: string | null;
  lastResult: { chunks_created: number } | null;
}

export function useUpload(botId: string) {
  const [state, setState] = useState<UploadState>({
    isUploading: false,
    progress: "",
    error: null,
    lastResult: null,
  });

  const upload = useCallback(
    async (file: File) => {
      setState({
        isUploading: true,
        progress: "Uploading...",
        error: null,
        lastResult: null,
      });
      try {
        const result = await uploadFile(file, botId);
        setState({
          isUploading: false,
          progress: "",
          error: null,
          lastResult: { chunks_created: result.chunks_created },
        });
        return result;
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : "Upload failed";
        setState({
          isUploading: false,
          progress: "",
          error: message,
          lastResult: null,
        });
        throw err;
      }
    },
    [botId]
  );

  return { ...state, upload };
}
