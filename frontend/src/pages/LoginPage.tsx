import { useNavigate } from "react-router-dom"

import { SignInForm } from "../components/SignInForm"

export function LoginPage() {
  const navigate = useNavigate()

  return <SignInForm onRegister={() => navigate("/register")} />
}
