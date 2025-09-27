import DashboardView from '@/components/Dashboard'
import DashboardErrorBoundary from '@/components/DashboardErrorBoundary'

export default function DashboardPage() {
  return (
    <DashboardErrorBoundary>
      <DashboardView />
    </DashboardErrorBoundary>
  )
}
