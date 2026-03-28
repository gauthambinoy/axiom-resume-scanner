import { Component, type ReactNode } from 'react';

interface Props { children: ReactNode; }
interface State { error: Error | null; }

export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error) { return { error }; }

  render() {
    if (this.state.error) {
      return (
        <div className="flex flex-col items-center justify-center p-12 text-center">
          <h2 className="text-xl font-semibold text-danger mb-2">Something went wrong</h2>
          <p className="text-muted mb-4">{this.state.error.message}</p>
          <button
            onClick={() => this.setState({ error: null })}
            className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-light transition"
          >
            Try Again
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
