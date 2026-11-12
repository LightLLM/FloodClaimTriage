import Button from '@/components/Button'
import { formatCurrency, formatProbability, getPriorityBg, getPriorityColor } from '@/lib/utils'
import type { TriageItem } from '@/types'
import { X } from 'lucide-react'

interface EvidenceDrawerProps {
  item: TriageItem
  onClose: () => void
  onAccept: () => void
  onOverride: (priority: 'P1' | 'P2' | 'P3') => void
  reviewMessage?: string | null
}

const DEMO_EVIDENCE = {
  flood_extent_signal: 1.0,
  proximity_signal: 0.95,
  rainfall_signal: 0.88,
  river_stage_signal: 1.0,
  optical_change_signal: 0.72,
  elevation_signal: 0.6,
  data_sources: {
    sensor: 'Sentinel-2',
    stac_item: 'sentinel2_20230815_tile32UQD',
    weather: 'NOAA NCEP Precipitation',
    elevation: 'USGS 3DEP 30m',
  },
  confidence_factors: {
    cloud_cover: 'Clear imagery (quality: 0.95)',
    data_completeness: '6/6 data sources available',
  },
}

export default function EvidenceDrawer({
  item,
  onClose,
  onAccept,
  onOverride,
  reviewMessage,
}: EvidenceDrawerProps) {
  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/50">
      <div className="w-full max-w-lg h-full bg-card border-l border-border overflow-y-auto scrollbar-thin">
        <div className="sticky top-0 bg-card border-b border-border px-6 py-4 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-text">Property Evidence</h2>
            <p className="text-sm text-text-muted font-mono">{item.external_property_id}</p>
          </div>
          <Button variant="secondary" size="sm" onClick={onClose} aria-label="Close evidence">
            <X className="w-4 h-4" />
          </Button>
        </div>

        <div className="p-6 space-y-6">
          <section>
            <h3 className="text-sm font-medium text-text-muted mb-3">Recommendation</h3>
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-background border border-border rounded-md p-3">
                <div className="text-xs text-text-muted mb-1">Priority</div>
                <span
                  className={`inline-flex px-2 py-1 rounded text-xs font-semibold border ${getPriorityBg(
                    item.inspection_priority
                  )} ${getPriorityColor(item.inspection_priority)}`}
                >
                  {item.inspection_priority}
                </span>
              </div>
              <div className="bg-background border border-border rounded-md p-3">
                <div className="text-xs text-text-muted mb-1">Damage Probability</div>
                <div className="text-lg font-semibold text-text">
                  {formatProbability(item.damage_probability)}
                </div>
              </div>
              <div className="bg-background border border-border rounded-md p-3">
                <div className="text-xs text-text-muted mb-1">Exposure</div>
                <div className="text-text">{formatCurrency(item.exposure_value)}</div>
              </div>
              <div className="bg-background border border-border rounded-md p-3">
                <div className="text-xs text-text-muted mb-1">Action</div>
                <div className="text-text text-sm">{item.recommended_action}</div>
              </div>
            </div>
          </section>

          <section>
            <h3 className="text-sm font-medium text-text-muted mb-3">Model Signals</h3>
            <div className="space-y-2">
              {Object.entries(DEMO_EVIDENCE)
                .filter(([key]) => key.endsWith('_signal'))
                .map(([key, value]) => (
                  <div key={key} className="flex items-center justify-between text-sm">
                    <span className="text-text-muted">{key.replace(/_/g, ' ')}</span>
                    <span className="text-text font-mono">{Number(value).toFixed(2)}</span>
                  </div>
                ))}
            </div>
          </section>

          <section>
            <h3 className="text-sm font-medium text-text-muted mb-3">Data Sources</h3>
            <div className="space-y-2 text-sm">
              {Object.entries(DEMO_EVIDENCE.data_sources).map(([key, value]) => (
                <div key={key} className="flex justify-between gap-4">
                  <span className="text-text-muted capitalize">{key}</span>
                  <span className="text-text text-right">{value}</span>
                </div>
              ))}
            </div>
          </section>

          <section>
            <h3 className="text-sm font-medium text-text-muted mb-3">Confidence</h3>
            <div className="space-y-2 text-sm">
              {Object.entries(DEMO_EVIDENCE.confidence_factors).map(([key, value]) => (
                <div key={key} className="bg-background border border-border rounded-md p-3">
                  <div className="text-text-muted capitalize mb-1">{key.replace(/_/g, ' ')}</div>
                  <div className="text-text">{value}</div>
                </div>
              ))}
              <p className="text-xs text-text-muted pt-1">Model version: v0.1-rule-based</p>
            </div>
          </section>

          <section>
            <h3 className="text-sm font-medium text-text-muted mb-3">Human Review</h3>
            <div className="space-y-3">
              <Button className="w-full" onClick={onAccept}>
                Accept Recommendation
              </Button>
              <div className="grid grid-cols-3 gap-2">
                <Button variant="secondary" size="sm" onClick={() => onOverride('P1')}>
                  Override P1
                </Button>
                <Button variant="secondary" size="sm" onClick={() => onOverride('P2')}>
                  Override P2
                </Button>
                <Button variant="secondary" size="sm" onClick={() => onOverride('P3')}>
                  Override P3
                </Button>
              </div>
              {reviewMessage && (
                <div className="bg-p3/10 border border-p3 text-p3 text-sm rounded-md px-3 py-2">
                  {reviewMessage}
                </div>
              )}
            </div>
          </section>
        </div>
      </div>
    </div>
  )
}
