import { type ClassValue, clsx } from 'clsx'

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs)
}

export function formatProbability(value: number): string {
  return `${(value * 100).toFixed(1)}%`
}

export function getPriorityColor(priority: 'P1' | 'P2' | 'P3'): string {
  const colors = {
    P1: 'text-p1',
    P2: 'text-p2',
    P3: 'text-p3',
  }
  return colors[priority] || 'text-text'
}

export function getPriorityBg(priority: 'P1' | 'P2' | 'P3'): string {
  const colors = {
    P1: 'bg-p1/20 border-p1',
    P2: 'bg-p2/20 border-p2',
    P3: 'bg-p3/20 border-p3',
  }
  return colors[priority] || 'bg-card border-border'
}

export function formatCurrency(value: number | undefined): string {
  if (value === undefined) return 'N/A'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value)
}

export function formatDate(date: string): string {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

export function formatDateTime(date: string): string {
  return new Date(date).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
