import React from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { useTranslation } from "@i18n"
import { useCreateHelpTicket } from "@api/help"
import { Button } from "@ui/Button"
import { Field } from "@ui/Field/Field"
import { ArrowLeft, Send, Hash } from "lucide-react"

interface SupportTicketFormProps {
  category: { code: string; label: string }
  onCancel: () => void
  onSuccess: () => void
}

type FormValues = {
  subject: string | undefined
  description: string
}

export function SupportTicketForm({ category, onCancel, onSuccess }: SupportTicketFormProps) {
  const { help } = useTranslation("support")
  const createTicket = useCreateHelpTicket()
  const isOtherCategory = category.code === "other"
  
  const schema = z.object({
    subject: isOtherCategory
      ? z.string()
          .min(1, help.form.subject.errorRequired)
          .max(160, help.form.subject.errorMaxLen)
      : z.string().max(160).optional(),
    description: z.string()
      .min(20, help.form.description.errorMinLen),
  })

  const { 
    register, 
    handleSubmit, 
    formState: { errors, isSubmitting } 
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      subject: "",
      description: "",
    },
  })

  const onSubmit = async (values: FormValues) => {
    try {
      await createTicket.mutateAsync({
        category_code: category.code,
        subject: isOtherCategory ? (values.subject ?? "") : category.label,
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
        <div className="category-chip">
          <Hash size={14} />
          {category.label}
        </div>
        <Button variant="ghost" onClick={onCancel} leftIcon={<ArrowLeft size={18} />}>
          {help.form.changeCategory}
        </Button>
      </div>

      <form className="ticket-form" onSubmit={handleSubmit(onSubmit)}>
        {isOtherCategory ? (
          <Field
            label={help.form.subject.label}
            placeholder={help.form.subject.placeholder}
            {...register("subject")}
            error={errors.subject?.message}
          />
        ) : null}

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
          <span className="form-field-hint">{help.form.description.hint}</span>
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
