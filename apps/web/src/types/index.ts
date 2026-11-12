export interface GeoJsonGeometry {
  type: string
  coordinates: number[] | number[][] | number[][][] | number[][][][]
  [key: string]: unknown
}

export interface User {
  id: string
  email: string
  full_name: string
  role: 'admin' | 'analyst' | 'reviewer' | 'viewer'
  is_active: boolean
}

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user_id: string
  email: string
  full_name: string
  role: string
}

export interface Event {
  id: string
  event_type: string
  name: string
  event_date: string
  geometry?: GeoJsonGeometry | null
  stac_collection_id?: string
  status: string
  created_at: string
  property_count?: number
  scored_count?: number
}

export interface Property {
  id: string
  external_property_id: string
  geometry: GeoJsonGeometry
  address_hash?: string
  building_type?: string
  exposure_value?: number
  region?: string
  data_source: string
  created_at: string
  updated_at: string
}

export interface Score {
  id: string
  property_id: string
  event_id: string
  model_version: string
  damage_probability: number
  damage_confidence: string
  inspection_priority: 'P1' | 'P2' | 'P3'
  recommended_action: string
  evidence: Evidence
  created_at: string
}

export interface Evidence {
  flood_extent_signal: number
  proximity_signal: number
  rainfall_signal: number
  river_stage_signal: number
  optical_change_signal: number
  elevation_signal: number
  data_sources: Record<string, string>
  confidence_factors: Record<string, string>
}

export interface TriageItem {
  property_id: string
  external_property_id: string
  geometry: GeoJsonGeometry | Record<string, never>
  exposure_value?: number
  damage_probability: number
  inspection_priority: 'P1' | 'P2' | 'P3'
  recommended_action: string
  created_at: string
}

export interface PropertyEvidence {
  property_id: string
  external_property_id: string
  score: {
    id: string
    damage_probability: number
    inspection_priority: string
    recommended_action: string
    damage_confidence: string
    model_version: string
    created_at: string
  }
  evidence: Evidence
  property_details: {
    building_type?: string
    exposure_value?: number
    region?: string
  }
}

export interface ScoreEventResult {
  event_id: string
  scored_count: number
  skipped_count: number
  total_properties: number
}

export interface ReviewScoreResult {
  score_id: string
  action: string
  updated_priority: string
  audit_event_id: string
}

export interface HealthStatus {
  status: string
  version: string
  model_version: string
  environment: string
}
