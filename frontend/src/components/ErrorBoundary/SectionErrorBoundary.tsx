import React from "react";
import { ErrorBoundary } from "./ErrorBoundary";
import { EmptyState } from "../ui/EmptyState";
import { AlertCircle, RefreshCw } from "lucide-react";

interface Props {
  children: React.ReactNode;
  onRetry?: () => void;
}

export function SectionErrorBoundary({ children, onRetry }: Props) {
  return (
    <ErrorBoundary 
      onReset={onRetry}
      fallback={
        <EmptyState
          icon={<AlertCircle className="text-error" />}
          title="Une erreur est survenue"
          description="L'affichage de cette section a échoué. Veuillez réessayer."
          action={
            <button 
              onClick={() => onRetry?.()} 
              className="button-ghost button-sm"
            >
              <RefreshCw size={16} className="mr-2" />
              Réessayer
            </button>
          }
        />
      }
    >
      {children}
    </ErrorBoundary>
  );
}
