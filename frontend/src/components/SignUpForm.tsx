import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { useNavigate, useSearchParams } from "react-router-dom"

import { registerApi, AuthApiError } from "@api"
import { setAccessToken } from "../utils/authToken"
import { useTranslation } from "@i18n"
import { createSignUpSchema } from "@i18n/zod/auth"
import { Field } from "@ui/Field"
import { Button } from "@ui/Button"

type SignUpFormData = {
  email: string
  password: string
}

type SignUpFormProps = {
  onSignIn: () => void
}

export function SignUpForm({ onSignIn }: SignUpFormProps) {
  const t = useTranslation("auth")
  const schema = createSignUpSchema(t)
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
        <Field
          id="signup-email"
          label={t.signUp.emailLabel}
          type="email"
          autoComplete="email"
          error={errors.email?.message}
          {...register("email")}
        />
        <Field
          id="signup-password"
          label={t.signUp.passwordLabel}
          type="password"
          autoComplete="new-password"
          error={errors.password?.message}
          {...register("password")}
        />
        {apiError && (
          <span className="chat-error" role="alert">
            {apiError}
          </span>
        )}
        <Button type="submit" loading={isSubmitting} fullWidth>
          {isSubmitting ? t.signUp.submitLoading : t.signUp.submitButton}
        </Button>
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
