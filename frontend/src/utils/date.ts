export function todayIso(): string {
  const now = new Date()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  return `${now.getFullYear()}-${month}-${day}`
}

export function eachIsoDate(start: string, end: string): string[] {
  const dates: string[] = []
  const current = new Date(`${start}T00:00:00`)
  const last = new Date(`${end}T00:00:00`)

  while (current <= last) {
    const month = String(current.getMonth() + 1).padStart(2, '0')
    const day = String(current.getDate()).padStart(2, '0')
    dates.push(`${current.getFullYear()}-${month}-${day}`)
    current.setDate(current.getDate() + 1)
  }

  return dates
}

export function formatDayDate(date: string): { weekday: string; label: string } {
  const value = new Date(`${date}T00:00:00`)
  return {
    weekday: new Intl.DateTimeFormat('es-PE', { weekday: 'long' }).format(value),
    label: new Intl.DateTimeFormat('es-PE', { day: 'numeric', month: 'short' }).format(value),
  }
}
