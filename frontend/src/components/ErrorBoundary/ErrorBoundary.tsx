import { Component } from "react";
import type { ErrorInfo, ReactNode } from "react";
import { AlertCircle, RefreshCw } from "lucide-react";
import "./ErrorBoundary.css";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onReset?: () => void;
}

interface State {
  hasError: boolean;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false
  };

  public static getDerivedStateFromError(_: Error): State {
    return { hasError: true };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught error:", error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ hasError: false });
    this.props.onReset?.();
  };

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="error-boundary">
          <div className="error-boundary__icon-wrapper">
            <AlertCircle className="error-boundary__icon" />
          </div>
          <h3 className="error-boundary__title">
            Une erreur est survenue
          </h3>
          <p className="error-boundary__text">
            L'affichage de cette section a échoué.
          </p>
          <button
            onClick={this.handleReset}
            className="error-boundary__button"
          >
            <RefreshCw className="error-boundary__button-icon" />
            Réessayer
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
