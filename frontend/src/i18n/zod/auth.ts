import { z } from "zod"
import type { AuthTranslation } from "@i18n/auth"

export function createSignInSchema(t: AuthTranslation) {
  return z.object({
    email: z.string().email(t.validation.emailInvalid),
    password: z.string().min(1, t.validation.passwordRequired),
  })
}

export function createSignUpSchema(t: AuthTranslation) {
  return z.object({
    email: z.string().email(t.validation.emailInvalid),
    password: z.string().min(8, t.validation.passwordTooShort),
  })
}

export type SignInFormData = z.infer<ReturnType<typeof createSignInSchema>>
export type SignUpFormData = z.infer<ReturnType<typeof createSignUpSchema>>
