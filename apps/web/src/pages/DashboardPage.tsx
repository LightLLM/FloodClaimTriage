import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { useAuthStore } from '@/store/auth'
import Button from '@/components/Button'
import Card, { CardContent, CardHeader, CardTitle } from '@/components/Card'
import { formatProbability, getPriorityColor, getPriorityBg, formatCurrency } from '@/lib/utils'
import type { Event, TriageItem } from '@/types'
import { LogOut, Download, AlertCircle } from 'lucide-react'

export default function DashboardPage() {
  const { user, logout } = useAuthStore()
  const [selectedEventId, setSelectedEventId] = useState<string | null>(null)
  const [selectedPriority, setSelectedPriority] = useState<string | null>(null)

  const { data: events } = useQuery({
    queryKey: ['events'],
    queryFn: () => api.getEvents(),
  })

  const { data: triageQueue } = useQuery({
    queryKey: ['triage', selectedEventId, selectedPriority],
    queryFn: () =>
      selectedEventId
        ? api.getTriageQueue(selectedEventId, {
            priority: selectedPriority || undefined,
            limit: 50,
          })
        : Promise.resolve([]),
    enabled: !!selectedEventId,
  })

  const selectedEvent = events?.find((e) => e.id === selectedEventId)

  const handleExport = async () => {
    if (!selectedEventId) return
    try {
      const blob = await api.exportTriage(selectedEventId)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `triage-export-${selectedEvent?.name || 'event'}.csv`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      console.error('Export failed:', error)
    }
  }

  const priorityCounts = triageQueue?.reduce(
    (acc, item) => {
      acc[item.inspection_priority] = (acc[item.inspection_priority] || 0) + 1
      return acc
    },
    {} as Record<string, number>
  )

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-card border-b border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div>
              <h1 className="text-xl font-bold text-primary">Flood Claim Triage</h1>
              <p className="text-sm text-text-muted">MVP v0.1 - Rule-based Model</p>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm text-text">{user?.full_name}</p>
                <p className="text-xs text-text-muted">{user?.role}</p>
              </div>
              <Button variant="secondary" size="sm" onClick={logout}>
                <LogOut className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Event Selector */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-text mb-2">Select Event</label>
          <select
            value={selectedEventId || ''}
            onChange={(e) => setSelectedEventId(e.target.value || null)}
            className="w-full max-w-md px-3 py-2 bg-card border border-border rounded-md text-text focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="">-- Select an event --</option>
            {events?.map((event) => (
              <option key={event.id} value={event.id}>
                {event.name} - {event.event_date} ({event.scored_count || 0} scored)
              </option>
            ))}
          </select>
        </div>

        {selectedEventId && selectedEvent && (
          <>
            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <Card>
                <CardContent>
                  <div className="text-text-muted text-sm mb-1">Total Properties</div>
                  <div className="text-2xl font-bold text-text">
                    {selectedEvent.property_count || 0}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent>
                  <div className="text-text-muted text-sm mb-1">P1 - Critical</div>
                  <div className="text-2xl font-bold text-p1">{priorityCounts?.P1 || 0}</div>
                </CardContent>
              </Card>

              <Card>
                <CardContent>
                  <div className="text-text-muted text-sm mb-1">P2 - Review</div>
                  <div className="text-2xl font-bold text-p2">{priorityCounts?.P2 || 0}</div>
                </CardContent>
              </Card>

              <Card>
                <CardContent>
                  <div className="text-text-muted text-sm mb-1">P3 - Low</div>
                  <div className="text-2xl font-bold text-p3">{priorityCounts?.P3 || 0}</div>
                </CardContent>
              </Card>
            </div>

            {/* Filters and Actions */}
            <div className="flex justify-between items-center mb-4">
              <div className="flex gap-2">
                <Button
                  variant={selectedPriority === null ? 'primary' : 'secondary'}
                  size="sm"
                  onClick={() => setSelectedPriority(null)}
                >
                  All
                </Button>
                <Button
                  variant={selectedPriority === 'P1' ? 'primary' : 'secondary'}
                  size="sm"
                  onClick={() => setSelectedPriority('P1')}
                >
                  P1
                </Button>
                <Button
                  variant={selectedPriority === 'P2' ? 'primary' : 'secondary'}
                  size="sm"
                  onClick={() => setSelectedPriority('P2')}
                >
                  P2
                </Button>
                <Button
                  variant={selectedPriority === 'P3' ? 'primary' : 'secondary'}
                  size="sm"
                  onClick={() => setSelectedPriority('P3')}
                >
                  P3
                </Button>
              </div>

              <Button variant="secondary" size="sm" onClick={handleExport}>
                <Download className="w-4 h-4 mr-2" />
                Export CSV
              </Button>
            </div>

            {/* Triage Queue */}
            <Card>
              <CardHeader>
                <CardTitle>Triage Queue</CardTitle>
              </CardHeader>
              <CardContent>
                {triageQueue && triageQueue.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b border-border">
                          <th className="text-left py-3 px-4 text-sm font-medium text-text-muted">
                            Property ID
                          </th>
                          <th className="text-left py-3 px-4 text-sm font-medium text-text-muted">
                            Priority
                          </th>
                          <th className="text-right py-3 px-4 text-sm font-medium text-text-muted">
                            Damage Prob.
                          </th>
                          <th className="text-right py-3 px-4 text-sm font-medium text-text-muted">
                            Exposure
                          </th>
                          <th className="text-left py-3 px-4 text-sm font-medium text-text-muted">
                            Action
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {triageQueue.map((item) => (
                          <tr
                            key={item.property_id}
                            className="border-b border-border hover:bg-background/50 cursor-pointer"
                          >
                            <td className="py-3 px-4 text-sm text-text font-mono">
                              {item.external_property_id}
                            </td>
                            <td className="py-3 px-4">
                              <span
                                className={`inline-flex px-2 py-1 rounded text-xs font-semibold border ${getPriorityBg(
                                  item.inspection_priority
                                )} ${getPriorityColor(item.inspection_priority)}`}
                              >
                                {item.inspection_priority}
                              </span>
                            </td>
                            <td className="py-3 px-4 text-right text-sm font-semibold text-text">
                              {formatProbability(item.damage_probability)}
                            </td>
                            <td className="py-3 px-4 text-right text-sm text-text">
                              {formatCurrency(item.exposure_value)}
                            </td>
                            <td className="py-3 px-4 text-sm text-text-muted">
                              {item.recommended_action}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <AlertCircle className="w-12 h-12 text-text-muted mx-auto mb-4" />
                    <p className="text-text-muted">
                      No properties in triage queue. Run scoring on this event first.
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          </>
        )}

        {!selectedEventId && (
          <Card>
            <CardContent>
              <div className="text-center py-12">
                <AlertCircle className="w-12 h-12 text-text-muted mx-auto mb-4" />
                <p className="text-text-muted">Select an event to view the triage queue</p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
