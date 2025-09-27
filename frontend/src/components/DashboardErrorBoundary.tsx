import React from 'react'

interface DashboardErrorBoundaryProps {
  children: React.ReactNode
}

interface DashboardErrorBoundaryState {
  hasError: boolean
  errorMessage: string | null
}

export default class DashboardErrorBoundary extends React.Component<
  DashboardErrorBoundaryProps,
  DashboardErrorBoundaryState
> {
  constructor(props: DashboardErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false, errorMessage: null }
  }

  static getDerivedStateFromError(error: Error): DashboardErrorBoundaryState {
    return { hasError: true, errorMessage: error.message }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    // eslint-disable-next-line no-console
    console.error('Dashboard render error', error, errorInfo)
  }

  private handleReset = () => {
    this.setState({ hasError: false, errorMessage: null })
  }

  render(): React.ReactNode {
    if (this.state.hasError) {
      return (
        <div className="p-6 max-w-xl mx-auto">
          <div className="rounded-lg border border-red-200 bg-red-50 p-6 space-y-4" role="alert">
            <h2 className="text-lg font-semibold text-red-800">Something went wrong in the dashboard</h2>
            <p className="text-sm text-red-700">
              Try refreshing the page. If the issue persists, capture the console logs and notify the engineering team.
            </p>
            {this.state.errorMessage && (
              <p className="text-xs text-red-600">Details: {this.state.errorMessage}</p>
            )}
            <div className="flex gap-3">
              <button
                type="button"
                onClick={this.handleReset}
                className="rounded bg-red-600 px-3 py-2 text-sm font-medium text-white transition hover:bg-red-700"
              >
                Try again
              </button>
              <button
                type="button"
                onClick={() => window.location.reload()}
                className="rounded border border-red-600 px-3 py-2 text-sm font-medium text-red-700 transition hover:bg-red-100"
              >
                Reload
              </button>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
