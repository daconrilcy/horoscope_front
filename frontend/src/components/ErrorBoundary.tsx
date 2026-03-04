import { Component } from "react";
import type { ErrorInfo, ReactNode } from "react";
import { AlertCircle, RefreshCw } from "lucide-react";

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
        <div style={{
          padding: "1.5rem",
          backgroundColor: "rgba(254, 242, 242, 1)",
          border: "1px solid rgba(252, 165, 165, 1)",
          borderRadius: "0.75rem",
          textAlign: "center",
          margin: "1rem 0"
        }}>
          <div style={{
            display: "inline-flex",
            alignItems: "center",
            justifyContent: "center",
            width: "3rem",
            height: "3rem",
            borderRadius: "9999px",
            backgroundColor: "rgba(254, 226, 226, 1)",
            marginBottom: "1rem"
          }}>
            <AlertCircle style={{ width: "1.5rem", height: "1.5rem", color: "rgba(220, 38, 38, 1)" }} />
          </div>
          <h3 style={{
            fontSize: "1.125rem",
            fontWeight: "bold",
            color: "rgba(127, 29, 29, 1)",
            marginBottom: "0.5rem",
            marginTop: "0"
          }}>
            Une erreur est survenue
          </h3>
          <p style={{
            fontSize: "0.875rem",
            color: "rgba(185, 28, 28, 1)",
            marginBottom: "1rem"
          }}>
            L'affichage de cette section a échoué.
          </p>
          <button
            onClick={this.handleReset}
            style={{
              display: "inline-flex",
              alignItems: "center",
              padding: "0.5rem 1rem",
              borderRadius: "0.375rem",
              backgroundColor: "rgba(220, 38, 38, 1)",
              color: "white",
              border: "none",
              cursor: "pointer",
              fontSize: "0.875rem",
              fontWeight: "500"
            }}
          >
            <RefreshCw style={{ width: "1rem", height: "1rem", marginRight: "0.5rem" }} />
            Réessayer
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
