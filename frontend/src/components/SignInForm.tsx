import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { useNavigate, useSearchParams } from "react-router-dom"

import { loginApi, AuthApiError } from "../api/auth"
import { setAccessToken } from "../utils/authToken"
import { detectLang } from "../i18n/astrology"
import { authTranslations } from "../i18n/auth"

const signInSchema = z.object({
  email: z.string().email("Adresse e-mail invalide."),
  password: z.string().min(1, "Le mot de passe est requis."),
})

type SignInFormData = z.infer<typeof signInSchema>

type SignInFormProps = {
  onRegister?: () => void
}

export function SignInForm({ onRegister }: SignInFormProps = {}) {
  const lang = detectLang()
  const t = authTranslations(lang)
  const [apiError, setApiError] = useState<string | null>(null)
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<SignInFormData>({
    resolver: zodResolver(signInSchema),
  })

  async function onSubmit(data: SignInFormData) {
    setApiError(null)
    try {
      const result = await loginApi(data.email, data.password)
      setAccessToken(result.access_token)
      const returnTo = searchParams.get("returnTo")
      if (returnTo && returnTo.startsWith("/") && !returnTo.startsWith("//")) {
        navigate(returnTo, { replace: true })
      } else {
        navigate("/dashboard", { replace: true })
      }
    } catch (err) {
      if (err instanceof AuthApiError) {
        setApiError(t.signIn.errorInvalidCredentials)
      } else {
        setApiError(t.signIn.errorGeneric)
      }
    }
  }

  return (
    <section className="panel">
      <h2>{t.signIn.title}</h2>
      <form className="chat-form" onSubmit={handleSubmit(onSubmit)} noValidate>
        <div>
          <label htmlFor="signin-email">{t.signIn.emailLabel}</label>
          <input
            id="signin-email"
            type="email"
            autoComplete="email"
            aria-describedby={errors.email ? "signin-email-error" : undefined}
            aria-invalid={Boolean(errors.email)}
            {...register("email")}
          />
          {errors.email && (
            <span id="signin-email-error" className="chat-error" role="alert">
              {errors.email.message}
            </span>
          )}
        </div>
        <div>
          <label htmlFor="signin-password">{t.signIn.passwordLabel}</label>
          <input
            id="signin-password"
            type="password"
            autoComplete="current-password"
            aria-describedby={errors.password ? "signin-password-error" : undefined}
            aria-invalid={Boolean(errors.password)}
            {...register("password")}
          />
          {errors.password && (
            <span id="signin-password-error" className="chat-error" role="alert">
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
              {t.signIn.submitLoading}
            </span>
          ) : (
            t.signIn.submitButton
          )}
        </button>
      </form>
      {onRegister && (
        <p>
          {t.signIn.noAccount}{" "}
          <button type="button" onClick={onRegister}>
            {t.signIn.createAccount}
          </button>
        </p>
      )}
    </section>
  )
}
