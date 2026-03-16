export type KeyPointItem = {
  id: string
  label: string
  icon?: string
  strength?: number // 0 to 100
  tone?: string
}

export type KeyPointsSectionModel = {
  title: string
  items: KeyPointItem[]
}
