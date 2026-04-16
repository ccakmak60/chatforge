import * as React from "react";
import { cn } from "@/lib/utils";

export interface AvatarProps extends React.HTMLAttributes<HTMLDivElement> {}

export function Avatar({ className, ...props }: AvatarProps) {
  return <div className={cn("relative flex shrink-0 overflow-hidden rounded-full", className)} {...props} />;
}

export interface AvatarFallbackProps extends React.HTMLAttributes<HTMLDivElement> {}

export function AvatarFallback({ className, ...props }: AvatarFallbackProps) {
  return <div className={cn("flex h-full w-full items-center justify-center rounded-full", className)} {...props} />;
}
