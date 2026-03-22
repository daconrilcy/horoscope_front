export type Astrologer = {
  id: string
  name: string
  first_name: string
  last_name: string
  avatar_url: string | null
  specialties: string[]
  style: string
  bio_short: string
}

export type AstrologerProfile = Astrologer & {
  bio_full: string
  gender: "male" | "female" | "non_binary" | "other"
  age: number | null
  professional_background: string[]
  key_skills: string[]
  behavioral_style: string[]
}
