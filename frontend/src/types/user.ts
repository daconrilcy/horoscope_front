export interface UserSettings {
  astrologer_profile: string;
  default_astrologer_id: string | null;
}

export interface UserSettingsApiResponse {
  data: UserSettings;
  meta: {
    request_id: string;
  };
}
