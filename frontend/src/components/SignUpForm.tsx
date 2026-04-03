import { useState, useEffect } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { useNavigate, useSearchParams } from "react-router-dom"

import { registerApi, AuthApiError } from "@api"
import { setAccessToken } from "../utils/authToken"
import { useTranslation } from "@i18n"
import { createSignUpSchema } from "@i18n/zod/auth"
import { Field } from "@ui/Field"
import { Button } from "@ui/Button"
import { PRICING_CONFIG } from "../config/pricingConfig"

type SignUpFormData = {
  email: string
  password: string
}

type SignUpFormProps = {
  onSignIn: () => void
}

export function SignUpForm({ onSignIn }: SignUpFormProps) {
  const tAuth = useTranslation("auth")
  const tLanding = useTranslation("landing")
  const schema = createSignUpSchema(tAuth)
  const [apiError, setApiError] = useState<string | null>(null)
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  const googleOauthEnabled = import.meta.env.VITE_GOOGLE_OAUTH_ENABLED === "true"
  const planCode = searchParams.get("plan")
  const selectedPlan = planCode && PRICING_CONFIG[planCode] ? PRICING_CONFIG[planCode] : null

  useEffect(() => {
    if (selectedPlan) {
      sessionStorage.setItem("intended_plan", selectedPlan.planCode)
    }
  }, [selectedPlan])

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
      navigate("/profile", { replace: true })
    } catch (err) {
      if (err instanceof AuthApiError && err.code === "email_already_registered") {
        setApiError(tAuth.signUp.errorEmailTaken)
      } else if (err instanceof AuthApiError) {
        setApiError(tAuth.signUp.errorRegistrationFailed)
      } else {
        setApiError(tAuth.signUp.errorGeneric)
      }
    }
  }

  const handleGoogleSignIn = () => {
    // AC3.10: Graceful degradation
    alert("Disponible prochainement")
  }

  return (
    <section className="panel premium-glass-card auth-form-card">
      <h2 className="auth-form-title">{tAuth.signUp.title}</h2>

      {selectedPlan && (
        <div className="auth-plan-badge">
          Plan sélectionné : {(tLanding.pricing.plans as any)[selectedPlan.planCode]?.name || selectedPlan.planCode}
        </div>
      )}

      {googleOauthEnabled && (
        <>
          <button 
            type="button" 
            className="google-auth-btn"
            onClick={handleGoogleSignIn}
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M19.6429 10.2303C19.6429 9.54545 19.5816 8.88485 19.4694 8.24848H10V12.003H15.4031C15.1704 13.2576 14.4643 14.3182 13.4031 15.0212V17.4636H16.6429C18.5383 15.7182 19.6429 13.1545 19.6429 10.2303Z" fill="#4285F4"/>
              <path d="M10 20C12.7 20 14.9643 19.103 16.6429 17.4636L13.4031 14.9455C12.5051 15.5485 11.352 15.903 10 15.903C7.39286 15.903 5.18367 14.1424 4.39796 11.7758H1.06633V14.3576C2.71429 17.6303 6.09184 20 10 20Z" fill="#34A853"/>
              <path d="M4.39796 11.7758C4.19388 11.1727 4.08163 10.5303 4.08163 9.86364C4.08163 9.19697 4.19388 8.55455 4.39796 7.95152V5.3697H1.06633C0.387755 6.72121 0 8.25152 0 9.86364C0 11.4758 0.387755 13.0061 1.06633 14.3576L4.39796 11.7758Z" fill="#FBBC05"/>
              <path d="M10 3.95758C11.4694 3.95758 12.7857 4.46061 13.8214 5.43939L16.7143 2.5C14.9592 0.951515 12.6939 0 10 0C6.09184 0 2.71429 2.3697 1.06633 5.3697L4.39796 7.95152C5.18367 5.58485 7.39286 3.95758 10 3.95758Z" fill="#EA4335"/>
            </svg>
            Continuer avec Google
          </button>
          <div className="auth-divider">
            <span>ou</span>
          </div>
        </>
      )}

      <form className="auth-form" onSubmit={handleSubmit(onSubmit)} noValidate>
        <Field
          id="signup-email"
          label={tAuth.signUp.emailLabel}
          type="email"
          autoComplete="email"
          error={errors.email?.message}
          {...register("email")}
        />
        <Field
          id="signup-password"
          label={tAuth.signUp.passwordLabel}
          type="password"
          autoComplete="new-password"
          error={errors.password?.message}
          {...register("password")}
        />
        {apiError && (
          <span className="auth-error-inline" role="alert">
            {apiError}
          </span>
        )}
        <Button 
          type="submit" 
          loading={isSubmitting} 
          fullWidth 
          variant="primary"
          size="lg"
          className="auth-submit-btn"
        >
          {isSubmitting ? tAuth.signUp.submitLoading : "Créer mon compte"}
        </Button>
      </form>

      <div className="auth-reassurance">
        <span>Sans carte bancaire</span>
        <span className="auth-reassurance-dot"></span>
        <span>Annulation à tout moment</span>
        <span className="auth-reassurance-dot"></span>
        <span>Données protégées RGPD</span>
      </div>

      <p className="auth-switch-link">
        {tAuth.signUp.alreadyHaveAccount}{" "}
        <button type="button" onClick={onSignIn}>
          {tAuth.signUp.signInLink}
        </button>
      </p>
    </section>
  )
}
