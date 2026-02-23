import { Outlet } from "react-router-dom"
import { ConsultationProvider } from "../../../state/consultationStore"

export function ConsultationLayout() {
  return (
    <ConsultationProvider>
      <Outlet />
    </ConsultationProvider>
  )
}
