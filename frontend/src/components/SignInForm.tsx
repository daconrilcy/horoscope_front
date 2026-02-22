import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"

import { loginApi, AuthApiError } from "../api/auth"
import { setAccessToken } from "../utils/authToken"

const signInSchema = z.object({
  email: z.string().email("Adresse e-mail invalide."),
  password: z.string().min(1, "Le mot de passe est requis."),
})

type SignInFormData = z.infer<typeof signInSchema>

type SignInFormProps = {
  onRegister?: () => void
}

export function SignInForm({ onRegister }: SignInFormProps = {}) {
  const [apiError, setApiError] = useState<string | null>(null)

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
    } catch (err) {
      if (err instanceof AuthApiError) {
        setApiError("Identifiants incorrects. Veuillez réessayer.")
      } else {
        setApiError("Une erreur est survenue. Veuillez réessayer.")
      }
    }
  }

  return (
    <section className="panel">
      <h2>Connexion</h2>
      <form className="chat-form" onSubmit={handleSubmit(onSubmit)} noValidate>
        <div>
          <label htmlFor="signin-email">Adresse e-mail</label>
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
          <label htmlFor="signin-password">Mot de passe</label>
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
              Connexion en cours...
            </span>
          ) : (
            "Se connecter"
          )}
        </button>
      </form>
      {onRegister && (
        <p>
          Pas encore de compte ?{" "}
          <button type="button" onClick={onRegister}>
            Créer un compte
          </button>
        </p>
      )}
    </section>
  )
}
