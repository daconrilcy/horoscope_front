import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { useNavigate, useSearchParams } from "react-router-dom"

import { loginApi, AuthApiError } from "@api"
import { setAccessToken } from "../utils/authToken"
import { useTranslation } from "@i18n"
import { createSignInSchema } from "@i18n/zod/auth"
import { Field } from "@ui/Field"
import { Button } from "@ui/Button"

type SignInFormData = {
  email: string
  password: string
}

type SignInFormProps = {
  onRegister?: () => void
}

export function SignInForm({ onRegister }: SignInFormProps = {}) {
  const t = useTranslation("auth")
  const schema = createSignInSchema(t)
  const [apiError, setApiError] = useState<string | null>(null)
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<SignInFormData>({
    resolver: zodResolver(schema),
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
        <Field
          id="signin-email"
          label={t.signIn.emailLabel}
          type="email"
          autoComplete="email"
          error={errors.email?.message}
          {...register("email")}
        />
        <Field
          id="signin-password"
          label={t.signIn.passwordLabel}
          type="password"
          autoComplete="current-password"
          error={errors.password?.message}
          {...register("password")}
        />
        {apiError && (
          <span className="chat-error" role="alert">
            {apiError}
          </span>
        )}
        <Button type="submit" loading={isSubmitting} fullWidth>
          {isSubmitting ? t.signIn.submitLoading : t.signIn.submitButton}
        </Button>
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
