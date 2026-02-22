import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"

import { registerApi, AuthApiError } from "../api/auth"
import { setAccessToken } from "../utils/authToken"

const signUpSchema = z.object({
  email: z.string().email("Adresse e-mail invalide."),
  password: z.string().min(8, "Le mot de passe doit contenir au moins 8 caractères."),
})

type SignUpFormData = z.infer<typeof signUpSchema>

type SignUpFormProps = {
  onSignIn: () => void
}

export function SignUpForm({ onSignIn }: SignUpFormProps) {
  const [apiError, setApiError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<SignUpFormData>({
    resolver: zodResolver(signUpSchema),
  })

  async function onSubmit(data: SignUpFormData) {
    setApiError(null)
    try {
      const result = await registerApi(data.email, data.password)
      setAccessToken(result.access_token)
    } catch (err) {
      if (err instanceof AuthApiError && err.code === "email_already_registered") {
        setApiError("Cette adresse e-mail est déjà utilisée.")
      } else if (err instanceof AuthApiError) {
        setApiError("Inscription impossible. Veuillez réessayer.")
      } else {
        setApiError("Une erreur est survenue. Veuillez réessayer.")
      }
    }
  }

  return (
    <section className="panel">
      <h2>Créer un compte</h2>
      <form className="chat-form" onSubmit={handleSubmit(onSubmit)} noValidate>
        <div>
          <label htmlFor="signup-email">Adresse e-mail</label>
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
          <label htmlFor="signup-password">Mot de passe</label>
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
              Inscription en cours...
            </span>
          ) : (
            "Créer mon compte"
          )}
        </button>
      </form>
      <p>
        Déjà un compte ?{" "}
        <button type="button" onClick={onSignIn}>
          Se connecter
        </button>
      </p>
    </section>
  )
}
