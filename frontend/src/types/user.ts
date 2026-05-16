export interface UserSettings {
  astrologer_profile: string;
  default_astrologer_id: string | null;
  default_language_code?: string | null;
  detected_locale?: string | null;
  detected_country_code?: string | null;
  detected_timezone?: string | null;
}

export interface UserSettingsApiResponse {
  data: UserSettings;
  meta: {
    request_id: string;
  };
}
