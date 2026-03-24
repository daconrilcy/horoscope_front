import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import type { UserSettings, UserSettingsApiResponse } from "@app-types/user";
import { API_BASE_URL, apiFetch } from "./client";
import { getAccessTokenSnapshot } from "../utils/authToken";

async function fetchUserSettings(): Promise<UserSettings> {
  const token = getAccessTokenSnapshot();
  if (!token) throw new Error("No token found");

  const response = await apiFetch(`${API_BASE_URL}/v1/users/me/settings`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error("Failed to fetch user settings");
  }

  const result: UserSettingsApiResponse = await response.json();
  return result.data;
}

async function patchUserSettings(payload: Partial<UserSettings>): Promise<UserSettings> {
  const token = getAccessTokenSnapshot();
  if (!token) throw new Error("No token found");

  const response = await apiFetch(`${API_BASE_URL}/v1/users/me/settings`, {
    method: "PATCH",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error("Failed to update user settings");
  }

  const result: UserSettingsApiResponse = await response.json();
  return result.data;
}

export function useUserSettings() {
  return useQuery({
    queryKey: ["user-settings"],
    queryFn: fetchUserSettings,
  });
}

export function useUpdateUserSettings() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: patchUserSettings,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["user-settings"] }),
  });
}
