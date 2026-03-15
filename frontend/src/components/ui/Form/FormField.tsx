import React from 'react';
import { Controller } from 'react-hook-form';
import { useFormContext } from './Form';
import { Field, type FieldProps } from '../Field/Field';
import { Select, type SelectProps } from '../Select/Select';

interface FormFieldBaseProps {
  name: string;
}

type FormFieldProps = FormFieldBaseProps & (
  | ({ as?: 'input' } & FieldProps)
  | ({ as: 'select' } & SelectProps)
);

/**
 * Wrapper intelligent pour connecter Field ou Select à react-hook-form
 */
export const FormField: React.FC<FormFieldProps> = ({ name, as = 'input', ...props }) => {
  const { control } = useFormContext();

  return (
    <Controller
      name={name}
      control={control}
      render={({ field, fieldState }) => {
        if (as === 'select') {
          const selectProps = props as SelectProps;
          return (
            <Select
              {...selectProps}
              {...field}
              error={fieldState.error?.message}
            />
          );
        }

        const fieldProps = props as FieldProps;
        return (
          <Field
            {...fieldProps}
            {...field}
            value={(field.value as string) ?? ''}
            error={fieldState.error?.message}
          />
        );
      }}
    />
  );
};
