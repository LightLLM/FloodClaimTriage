import type { Event, TriageItem } from '@/types'

export const DEMO_EVENTS: Event[] = [
  {
    id: 'evt-tx-2023',
    event_type: 'flood',
    name: 'Texas Flood August 2023',
    event_date: '2023-08-15',
    stac_collection_id: 'sentinel2-floods-tx-2023',
    status: 'active',
    created_at: '2023-08-16T10:00:00Z',
    property_count: 1240,
    scored_count: 1180,
  },
  {
    id: 'evt-fl-2023',
    event_type: 'flood',
    name: 'Florida Hurricane September 2023',
    event_date: '2023-09-10',
    stac_collection_id: 'sentinel2-hurricane-fl-2023',
    status: 'active',
    created_at: '2023-09-11T08:00:00Z',
    property_count: 860,
    scored_count: 840,
  },
]

export const DEMO_TRIAGE: TriageItem[] = [
  {
    property_id: 'p-001',
    external_property_id: 'PROP-00012',
    geometry: {},
    exposure_value: 485000,
    damage_probability: 0.91,
    inspection_priority: 'P1',
    recommended_action: 'Field inspection',
    created_at: '2023-08-16T12:00:00Z',
  },
  {
    property_id: 'p-002',
    external_property_id: 'PROP-00047',
    geometry: {},
    exposure_value: 320000,
    damage_probability: 0.84,
    inspection_priority: 'P1',
    recommended_action: 'Field inspection',
    created_at: '2023-08-16T12:00:00Z',
  },
  {
    property_id: 'p-003',
    external_property_id: 'PROP-00103',
    geometry: {},
    exposure_value: 210000,
    damage_probability: 0.78,
    inspection_priority: 'P1',
    recommended_action: 'Field inspection',
    created_at: '2023-08-16T12:00:00Z',
  },
  {
    property_id: 'p-004',
    external_property_id: 'PROP-00221',
    geometry: {},
    exposure_value: 560000,
    damage_probability: 0.62,
    inspection_priority: 'P2',
    recommended_action: 'Desk review',
    created_at: '2023-08-16T12:00:00Z',
  },
  {
    property_id: 'p-005',
    external_property_id: 'PROP-00308',
    geometry: {},
    exposure_value: 175000,
    damage_probability: 0.51,
    inspection_priority: 'P2',
    recommended_action: 'Desk review',
    created_at: '2023-08-16T12:00:00Z',
  },
  {
    property_id: 'p-006',
    external_property_id: 'PROP-00455',
    geometry: {},
    exposure_value: 98000,
    damage_probability: 0.28,
    inspection_priority: 'P3',
    recommended_action: 'No action',
    created_at: '2023-08-16T12:00:00Z',
  },
  {
    property_id: 'p-007',
    external_property_id: 'PROP-00512',
    geometry: {},
    exposure_value: 142000,
    damage_probability: 0.19,
    inspection_priority: 'P3',
    recommended_action: 'No action',
    created_at: '2023-08-16T12:00:00Z',
  },
]

export const DEMO_USERS: Record<
  string,
  { password: string; user: { id: string; email: string; full_name: string; role: string } }
> = {
  'admin@example.com': {
    password: 'admin123',
    user: {
      id: 'demo-admin',
      email: 'admin@example.com',
      full_name: 'Admin User',
      role: 'admin',
    },
  },
  'analyst@example.com': {
    password: 'analyst123',
    user: {
      id: 'demo-analyst',
      email: 'analyst@example.com',
      full_name: 'Jane Analyst',
      role: 'analyst',
    },
  },
}

export function isDemoMode(): boolean {
  return localStorage.getItem('demo_mode') === 'true'
}
