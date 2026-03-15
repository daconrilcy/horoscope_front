import { useMemo, useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { useNavigate, useSearchParams } from "react-router-dom"

import { registerApi, AuthApiError } from "@api"
import { setAccessToken } from "../utils/authToken"
import { detectLang } from "../i18n/astrology"
import { authTranslations, type AuthTranslation } from "../i18n/auth"

export function createSignUpSchema(t: AuthTranslation) {
  return z.object({
    email: z.string().email(t.validation.emailInvalid),
    password: z.string().min(8, t.validation.passwordTooShort),
  })
}

type SignUpFormData = z.infer<ReturnType<typeof createSignUpSchema>>

type SignUpFormProps = {
  onSignIn: () => void
}

export function SignUpForm({ onSignIn }: SignUpFormProps) {
  const lang = detectLang()
  const t = authTranslations(lang)
  const schema = useMemo(() => createSignUpSchema(t), [t])
  const [apiError, setApiError] = useState<string | null>(null)
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<SignUpFormData>({
    resolver: zodResolver(schema),
  })

  async function onSubmit(data: SignUpFormData) {
    setApiError(null)
    try {
      const result = await registerApi(data.email, data.password)
      setAccessToken(result.access_token)
      const returnTo = searchParams.get("returnTo")
      if (returnTo && returnTo.startsWith("/") && !returnTo.startsWith("//")) {
        navigate(returnTo, { replace: true })
      } else {
        navigate("/dashboard", { replace: true })
      }
    } catch (err) {
      if (err instanceof AuthApiError && err.code === "email_already_registered") {
        setApiError(t.signUp.errorEmailTaken)
      } else if (err instanceof AuthApiError) {
        setApiError(t.signUp.errorRegistrationFailed)
      } else {
        setApiError(t.signUp.errorGeneric)
      }
    }
  }

  return (
    <section className="panel">
      <h2>{t.signUp.title}</h2>
      <form className="chat-form" onSubmit={handleSubmit(onSubmit)} noValidate>
        <div>
          <label htmlFor="signup-email">{t.signUp.emailLabel}</label>
          <input
            id="signup-email"
            type="email"
            autoComplete="email"
            aria-describedby={errors.email ? "signup-email-error" : undefined}
            aria-invalid={Boolean(errors.email)}
            {...register("email")}
          />
          {errors.email && (
            <span id="signup-email-error" className="chat-error" role="alert">
              {errors.email.message}
            </span>
          )}
        </div>
        <div>
          <label htmlFor="signup-password">{t.signUp.passwordLabel}</label>
          <input
            id="signup-password"
            type="password"
            autoComplete="new-password"
            aria-describedby={errors.password ? "signup-password-error" : undefined}
            aria-invalid={Boolean(errors.password)}
            {...register("password")}
          />
          {errors.password && (
            <span id="signup-password-error" className="chat-error" role="alert">
              {errors.password.message}
            </span>
          )}
        </div>
        {apiError && (
          <span className="chat-error" role="alert">
            {apiError}
          </span>
        )}
        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? (
            <span className="state-line">
              <span className="state-loading" aria-hidden="true" />
              {t.signUp.submitLoading}
            </span>
          ) : (
            t.signUp.submitButton
          )}
        </button>
      </form>
      <p>
        {t.signUp.alreadyHaveAccount}{" "}
        <button type="button" onClick={onSignIn}>
          {t.signUp.signInLink}
        </button>
      </p>
    </section>
  )
}

