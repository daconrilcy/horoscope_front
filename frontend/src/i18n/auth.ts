import type { AstrologyLang } from "./astrology"

export interface AuthTranslation {
  signIn: {
    title: string
    emailLabel: string
    passwordLabel: string
    submitButton: string
    submitLoading: string
    errorInvalidCredentials: string
    errorGeneric: string
    noAccount: string
    createAccount: string
  }
  signUp: {
    title: string
    emailLabel: string
    passwordLabel: string
    submitButton: string
    submitLoading: string
    errorEmailTaken: string
    errorRegistrationFailed: string
    errorGeneric: string
    alreadyHaveAccount: string
    signInLink: string
  }
}

const translations: Record<AstrologyLang, AuthTranslation> = {
  fr: {
    signIn: {
      title: "Connexion",
      emailLabel: "Adresse e-mail",
      passwordLabel: "Mot de passe",
      submitButton: "Se connecter",
      submitLoading: "Connexion en cours...",
      errorInvalidCredentials: "Identifiants incorrects. Veuillez réessayer.",
      errorGeneric: "Une erreur est survenue. Veuillez réessayer.",
      noAccount: "Pas encore de compte ?",
      createAccount: "Créer un compte",
    },
    signUp: {
      title: "Créer un compte",
      emailLabel: "Adresse e-mail",
      passwordLabel: "Mot de passe",
      submitButton: "Créer mon compte",
      submitLoading: "Inscription en cours...",
      errorEmailTaken: "Cette adresse e-mail est déjà utilisée.",
      errorRegistrationFailed: "Inscription impossible. Veuillez réessayer.",
      errorGeneric: "Une erreur est survenue. Veuillez réessayer.",
      alreadyHaveAccount: "Déjà un compte ?",
      signInLink: "Se connecter",
    },
  },
  en: {
    signIn: {
      title: "Sign In",
      emailLabel: "Email Address",
      passwordLabel: "Password",
      submitButton: "Sign In",
      submitLoading: "Signing in...",
      errorInvalidCredentials: "Invalid credentials. Please try again.",
      errorGeneric: "An error occurred. Please try again.",
      noAccount: "Don't have an account?",
      createAccount: "Create an account",
    },
    signUp: {
      title: "Create an Account",
      emailLabel: "Email Address",
      passwordLabel: "Password",
      submitButton: "Create my account",
      submitLoading: "Signing up...",
      errorEmailTaken: "This email address is already in use.",
      errorRegistrationFailed: "Registration failed. Please try again.",
      errorGeneric: "An error occurred. Please try again.",
      alreadyHaveAccount: "Already have an account?",
      signInLink: "Sign In",
    },
  },
  es: {
    signIn: {
      title: "Iniciar sesión",
      emailLabel: "Correo electrónico",
      passwordLabel: "Contraseña",
      submitButton: "Iniciar sesión",
      submitLoading: "Iniciando sesión...",
      errorInvalidCredentials: "Credenciales inválidas. Por favor, inténtelo de nuevo.",
      errorGeneric: "Ha ocurrido un error. Por favor, inténtelo de nuevo.",
      noAccount: "¿No tienes una cuenta?",
      createAccount: "Crear una cuenta",
    },
    signUp: {
      title: "Crear una cuenta",
      emailLabel: "Correo electrónico",
      passwordLabel: "Contraseña",
      submitButton: "Crear mi cuenta",
      submitLoading: "Registrando...",
      errorEmailTaken: "Esta dirección de correo electrónico ya está en uso.",
      errorRegistrationFailed: "Error al registrar. Por favor, inténtelo de nuevo.",
      errorGeneric: "Ha ocurrido un error. Por favor, inténtelo de nuevo.",
      alreadyHaveAccount: "¿Ya tienes una cuenta?",
      signInLink: "Iniciar sesión",
    },
  },
}

export function authTranslations(lang: AstrologyLang = "fr"): AuthTranslation {
  return translations[lang] ?? translations.fr
}
