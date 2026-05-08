// Composant de formulaire generique reliant Zod et react-hook-form.
import { createContext, useContext, type ReactNode } from 'react';
import { useForm, type DefaultValues, type UseFormReturn, type FieldValues, type Resolver, type SubmitHandler } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import './Form.css';

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

interface FormProps<TFieldValues extends FieldValues> {
  /** Schema Zod qui valide les valeurs manipulees par le formulaire. */
  schema: z.ZodType<TFieldValues>;
  onSubmit: SubmitHandler<TFieldValues>;
  loading?: boolean;
  children: ReactNode;
  className?: string;
  id?: string;
  /** Initial values for the form fields */
  defaultValues?: DefaultValues<TFieldValues>;
}

const FormContext = createContext<UseFormReturn<FieldValues> | null>(null);

/**
 * Hook pour accéder aux méthodes de react-hook-form dans les composants enfants
 */
export function useFormContext<TFieldValues extends FieldValues = FieldValues>(): UseFormReturn<TFieldValues> {
  const ctx = useContext(FormContext);
  if (!ctx) {
    throw new Error('useFormContext must be used inside a <Form> component');
  }
  return ctx as UseFormReturn<TFieldValues>;
}

/**
 * Composant Form générique intégrant react-hook-form et zod
 */
export function Form<TFieldValues extends FieldValues>({
  schema,
  onSubmit,
  loading = false,
  children,
  className,
  id,
  defaultValues,
}: FormProps<TFieldValues>) {
  const resolverSchema = schema as unknown as Parameters<typeof zodResolver>[0];
  const methods = useForm<TFieldValues>({
    resolver: zodResolver(resolverSchema) as Resolver<TFieldValues>,
    defaultValues,
    mode: 'onTouched',
  });

  return (
    <FormContext.Provider value={methods as unknown as UseFormReturn<FieldValues>}>
      <form
        id={id}
        onSubmit={methods.handleSubmit(onSubmit)}
        className={className}
        noValidate
      >
        <fieldset disabled={loading} className="form-fieldset-reset">
          {children}
        </fieldset>
      </form>
    </FormContext.Provider>
  );
}

