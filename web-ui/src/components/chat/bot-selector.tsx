import { useEffect, useState } from "react";
import { fetchModels } from "@/lib/api";

interface BotSelectorProps {
  value: string;
  onChange: (botId: string) => void;
}

interface ModelInfo {
  name: string;
  source: string;
  status: string;
}

export function BotSelector({ value, onChange }: BotSelectorProps) {
  const [models, setModels] = useState<ModelInfo[]>([]);

  useEffect(() => {
    fetchModels()
      .then((data) => setModels(data.models || []))
      .catch(() => setModels([]));
  }, []);

  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="rounded-md border border-neutral-200 bg-white px-3 py-1.5 text-sm"
    >
      <option value="default">default</option>
      {models.map((m) => (
        <option key={m.name} value={m.name}>
          {m.name} ({m.source})
        </option>
      ))}
    </select>
  );
}
