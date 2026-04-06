import { useNavigate } from "react-router-dom"

import { SignUpForm } from "../components/SignUpForm"

export function RegisterPage() {
  const navigate = useNavigate()

  return <SignUpForm onSignIn={() => navigate("/login")} />
}
