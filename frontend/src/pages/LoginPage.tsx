import { useNavigate } from "react-router-dom"

import { SignInForm } from "../features/auth/SignInForm"

export function LoginPage() {
  const navigate = useNavigate()

  return <SignInForm onRegister={() => navigate("/register")} />
}
