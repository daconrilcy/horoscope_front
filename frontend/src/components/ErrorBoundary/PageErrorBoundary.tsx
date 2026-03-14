import React from "react";
import { ErrorBoundary } from "./ErrorBoundary";
import { RefreshCw, AlertCircle } from "lucide-react";
import "./ErrorBoundary.css";

interface Props {
  children: React.ReactNode;
}

const PageErrorFallback: React.FC = () => {
  const handleReload = () => {
    window.location.reload();
  };

  return (
    <div className="page-error-boundary">
      <div className="page-error-boundary__container">
        <AlertCircle size={48} className="page-error-boundary__icon" />
        <h1 className="page-error-boundary__title">Une erreur est survenue</h1>
        <p className="page-error-boundary__message">
          L'application a rencontré une erreur inattendue. 
          Si le problème persiste, n'hésitez pas à contacter le support.
        </p>
        <button 
          onClick={handleReload}
          className="page-error-boundary__button"
        >
          <RefreshCw size={20} />
          Recharger la page
        </button>
      </div>
    </div>
  );
};

export function PageErrorBoundary({ children }: Props) {
  return (
    <ErrorBoundary fallback={<PageErrorFallback />}>
      {children}
    </ErrorBoundary>
  );
}
