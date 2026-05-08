import { useNavigate } from "react-router-dom"

import { SignUpForm } from "../features/auth/SignUpForm"

export function RegisterPage() {
  const navigate = useNavigate()

  return <SignUpForm onSignIn={() => navigate("/login")} />
}
