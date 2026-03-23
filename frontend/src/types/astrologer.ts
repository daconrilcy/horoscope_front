export type SpecialtyDetail = {
  title: string
  description: string
}

export type AstrologerMetrics = {
  total_experience_years: number
  experience_years: number
  consultations_count: number
  average_rating: number
}

export type AstrologerReview = {
  id: string
  user_name: string
  rating: number
  comment?: string
  tags: string[]
  created_at: string
}

export type AstrologerActionState = {
  has_chat: boolean
  has_natal_interpretation: boolean
  last_chat_id?: string
  last_natal_interpretation_id?: string
}

export type Astrologer = {
  id: string
  name: string
  first_name: string
  last_name: string
  provider_type?: "ia" | "real"
  avatar_url: string | null
  specialties: string[]
  style: string
  bio_short: string
}

export type AstrologerProfile = Astrologer & {
  bio_full: string
  gender: "male" | "female" | "non_binary" | "other"
  age?: number
  location?: string
  quote?: string
  mission_statement?: string
  ideal_for?: string
  metrics: AstrologerMetrics
  specialties_details: SpecialtyDetail[]
  professional_background: string[]
  key_skills: string[]
  behavioral_style: string[]

  // Social proof
  reviews: AstrologerReview[]
  review_summary: {
    average_rating: number
    review_count: number
  }
  user_rating?: number
  user_review?: AstrologerReview

  // Contextual actions
  action_state: AstrologerActionState
}
