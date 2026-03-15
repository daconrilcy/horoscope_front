import React, { createContext, useContext } from 'react';
import { useForm, type UseFormReturn, type FieldValues, type SubmitHandler } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

/**
 * Pattern createFormSchema :
 * Pour externaliser les messages d'erreur et supporter l'i18n, définissez une factory :
 * 
 * const createLoginSchema = (t: (key: string) => string) => z.object({
 *   email: z.string().email(t('errors.email_invalid')),
 *   password: z.string().min(8, t('errors.password_too_short'))
 * });
 * 
 * Usage : <Form schema={createLoginSchema(t)} onSubmit={...}>
 */

interface FormProps<TSchema extends z.ZodType<any, any, any>> {
  schema: TSchema;
  onSubmit: SubmitHandler<z.infer<TSchema>>;
  loading?: boolean;
  children: React.ReactNode;
  className?: string;
  id?: string;
  /** Initial values for the form fields */
  defaultValues?: any;
}

const FormContext = createContext<UseFormReturn<any> | null>(null);

/**
 * Hook pour accéder aux méthodes de react-hook-form dans les composants enfants
 */
export function useFormContext<TFieldValues extends FieldValues = FieldValues>() {
  const ctx = useContext(FormContext);
  if (!ctx) {
    throw new Error('useFormContext must be used inside a <Form> component');
  }
  return ctx as UseFormReturn<TFieldValues>;
}

/**
 * Composant Form générique intégrant react-hook-form et zod
 */
export function Form<TSchema extends z.ZodType<any, any, any>>({
  schema,
  onSubmit,
  loading = false,
  children,
  className,
  id,
  defaultValues,
}: FormProps<TSchema>) {
  const methods = useForm<z.infer<TSchema>>({
    resolver: zodResolver(schema),
    defaultValues,
    mode: 'onTouched',
  });

  return (
    <FormContext.Provider value={methods}>
      <form
        id={id}
        onSubmit={methods.handleSubmit(onSubmit)}
        className={className}
        noValidate
      >
        <fieldset disabled={loading} style={{ border: 'none', padding: 0, margin: 0 }}>
          {children}
        </fieldset>
      </form>
    </FormContext.Provider>
  );
}
