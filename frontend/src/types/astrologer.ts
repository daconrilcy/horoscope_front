export type Astrologer = {
  id: string
  name: string
  avatar_url: string
  specialties: string[]
  style: string
  bio_short: string
}

export type AstrologerProfile = Astrologer & {
  bio_full: string
  languages: string[]
  experience_years: number
}
