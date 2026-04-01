import React from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { useTranslation } from "@i18n"
import { useCreateHelpTicket } from "@api/help"
import { Button } from "@ui/Button"
import { Field } from "@ui/Field/Field"
import { ArrowLeft, Send } from "lucide-react"

interface SupportTicketFormProps {
  category: { code: string; label: string }
  onCancel: () => void
  onSuccess: () => void
}

type FormValues = {
  subject: string
  description: string
}

export function SupportTicketForm({ category, onCancel, onSuccess }: SupportTicketFormProps) {
  const { help } = useTranslation("support")
  const createTicket = useCreateHelpTicket()
  
  const schema = z.object({
    subject: z.string()
      .min(1, help.form.subject.errorRequired)
      .max(160, help.form.subject.errorMaxLen),
    description: z.string()
      .min(20, help.form.description.errorMinLen),
  })

  const { 
    register, 
    handleSubmit, 
    formState: { errors, isSubmitting } 
  } = useForm<FormValues>({
    resolver: zodResolver(schema)
  })

  const onSubmit = async (values: FormValues) => {
    try {
      await createTicket.mutateAsync({
        category_code: category.code,
        subject: values.subject,
        description: values.description,
      })
      onSuccess()
    } catch (err) {
      console.error("Failed to create ticket", err)
    }
  }

  return (
    <div className="ticket-form-container">
      <div className="ticket-form__header">
        <Button variant="ghost" onClick={onCancel} leftIcon={<ArrowLeft size={18} />}>
          {help.form.changeCategory}
        </Button>
        <div className="ticket-form__category-info">
          {help.form.selectedCategory.replace("{category}", category.label)}
        </div>
      </div>

      <form className="ticket-form" onSubmit={handleSubmit(onSubmit)}>
        <Field
          label={help.form.subject.label}
          placeholder={help.form.subject.placeholder}
          {...register("subject")}
          error={errors.subject?.message}
        />

        <div className="field">
          <label className="field__label" htmlFor="ticket-description">
            {help.form.description.label}
          </label>
          <textarea
            id="ticket-description"
            className={`field__input field__input--textarea ${errors.description ? 'field__input--error' : ''}`}
            placeholder={help.form.description.placeholder}
            rows={5}
            {...register("description")}
          />
          {errors.description && (
            <span className="field__error" role="alert">{errors.description.message}</span>
          )}
        </div>

        {createTicket.isError && (
          <div className="form-error-message">
            {createTicket.error instanceof Error ? createTicket.error.message : help.form.errorGeneric}
          </div>
        )}

        <div className="form-actions">
          <Button 
            type="submit" 
            variant="primary" 
            disabled={isSubmitting}
            loading={isSubmitting}
            leftIcon={<Send size={18} />}
          >
            {help.form.submit}
          </Button>
        </div>
      </form>
    </div>
  )
}
