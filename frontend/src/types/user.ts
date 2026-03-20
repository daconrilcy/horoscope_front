export interface UserSettings {
  astrologer_profile: string;
}

export interface UserSettingsApiResponse {
  data: UserSettings;
  meta: {
    request_id: string;
  };
}
