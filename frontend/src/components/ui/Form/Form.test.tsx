// @ts-nocheck
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { z } from 'zod';
import { Form } from './Form';
import { FormField } from './FormField';
import { Button } from '../Button/Button';

const schema = z.object({
  email: z.string().email('Email invalide'),
  name: z.string().min(3, 'Nom trop court'),
});

describe('Form & FormField', () => {
  it('submits correctly when data is valid', async () => {
    const handleSubmit = vi.fn();
    render(
      <Form schema={schema} onSubmit={handleSubmit}>
        <FormField name="email" label="Email" />
        <FormField name="name" label="Nom" />
        <Button type="submit">Envoyer</Button>
      </Form>
    );

    fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByLabelText('Nom'), { target: { value: 'Cyril' } });
    fireEvent.click(screen.getByText('Envoyer'));

    await waitFor(() => {
      expect(handleSubmit).toHaveBeenCalledWith(
        expect.objectContaining({ email: 'test@example.com', name: 'Cyril' }),
        expect.anything()
      );
    });
  });

  it('displays validation errors and prevents submission when data is invalid', async () => {
    const handleSubmit = vi.fn();
    render(
      <Form schema={schema} onSubmit={handleSubmit}>
        <FormField name="email" label="Email" />
        <FormField name="name" label="Nom" />
        <Button type="submit">Envoyer</Button>
      </Form>
    );

    fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'invalid-email' } });
    fireEvent.click(screen.getByText('Envoyer'));

    expect(await screen.findByText('Email invalide')).toBeInTheDocument();
    expect(handleSubmit).not.toHaveBeenCalled();
  });

  it('disables fields when loading is true', () => {
    render(
      <Form schema={schema} onSubmit={() => {}} loading={true}>
        <FormField name="email" label="Email" />
        <Button type="submit">Envoyer</Button>
      </Form>
    );

    expect(screen.getByLabelText('Email')).toBeDisabled();
  });

  it('integrates with Select component', async () => {
    const selectSchema = z.object({
      choice: z.string().min(1, 'Sélection requise'),
    });
    const options = [{ value: 'a', label: 'Option A' }];
    const handleSubmit = vi.fn();

    render(
      <Form 
        schema={selectSchema} 
        onSubmit={handleSubmit}
        defaultValues={{ choice: '' }}
      >
        <FormField name="choice" as="select" options={options} label="Choix" />
        <Button type="submit">Envoyer</Button>
      </Form>
    );

    // Initial state
    fireEvent.click(screen.getByText('Envoyer'));
    expect(await screen.findByText('Sélection requise')).toBeInTheDocument();

    // Select option
    fireEvent.click(screen.getByRole('button', { name: /choix/i }));
    fireEvent.click(screen.getByText('Option A'));
    
    fireEvent.click(screen.getByText('Envoyer'));

    await waitFor(() => {
      expect(handleSubmit).toHaveBeenCalledWith({ choice: 'a' }, expect.anything());
    });
  });
});

